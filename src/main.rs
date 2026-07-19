use roxmltree::{Document, Node};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::BTreeSet;
use std::env;
use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};

const MANIFEST_PATH: &str = "v1/conferences/manifest.json";
const MAX_PACK_RECORDS: usize = 30_000;
const MAX_PACK_COMPRESSED_BYTES: u64 = 128 * 1024 * 1024;

#[derive(Debug, Deserialize)]
struct Manifest {
    schema_version: u32,
    dataset: String,
    venues: Vec<Venue>,
}

#[derive(Debug, Deserialize)]
struct Venue {
    id: String,
    short_name: String,
    editions: Vec<Edition>,
}

#[derive(Debug, Deserialize)]
struct Edition {
    id: String,
    year: u16,
    paper_count: usize,
    pack: Option<PackReference>,
}

#[derive(Debug, Deserialize)]
struct PackReference {
    path: String,
    sha256: String,
    compressed_bytes: u64,
    record_count: usize,
}

#[derive(Debug, Deserialize, Serialize)]
struct ConferencePaperRecord {
    schema_version: u32,
    id: String,
    venue_id: String,
    edition_id: String,
    year: u16,
    title: String,
    authors: Vec<String>,
    #[serde(rename = "abstract")]
    abstract_text: String,
    landing_url: String,
    pdf_url: Option<String>,
    doi: Option<String>,
    categories: Vec<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    source_group: Option<ConferenceSourceGroup>,
    published_at: String,
    updated_at: String,
    acceptance_status: String,
    provenance_url: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct ConferenceSourceGroup {
    id: String,
    name: String,
    kind: String,
}

fn main() {
    if let Err(error) = run() {
        eprintln!("apaper-cloud: {error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    match args.next().as_deref() {
        Some("validate-site") => {
            let root = args
                .next()
                .map(PathBuf::from)
                .ok_or_else(|| "validate-site requires a public directory".to_string())?;
            if args.next().is_some() {
                return Err("validate-site accepts one public directory".to_string());
            }
            validate_site(&root)
        }
        Some("pack") => pack(parse_pack_arguments(args.collect())?),
        Some("ingest-acl") => ingest_acl(parse_ingest_acl_arguments(args.collect())?),
        _ => Err(
            "usage: apaper-cloud validate-site <public-dir> | pack --input <jsonl> --output <jsonl.zst> | ingest-acl --input <xml> [--input <xml>] --venue <id> --edition <id:year> --year <yyyy> --output <jsonl>"
                .to_string(),
        ),
    }
}

#[derive(Debug)]
struct IngestAclArguments {
    inputs: Vec<PathBuf>,
    venue_id: String,
    edition_id: String,
    year: u16,
    output: PathBuf,
}

fn parse_ingest_acl_arguments(args: Vec<String>) -> Result<IngestAclArguments, String> {
    let mut inputs = Vec::new();
    let mut venue_id = None;
    let mut edition_id = None;
    let mut year = None;
    let mut output = None;
    let mut index = 0;
    while index < args.len() {
        let value = args
            .get(index + 1)
            .ok_or_else(|| format!("{} requires a value", args[index]))?;
        match args[index].as_str() {
            "--input" => inputs.push(PathBuf::from(value)),
            "--venue" => venue_id = Some(value.to_string()),
            "--edition" => edition_id = Some(value.to_string()),
            "--year" => {
                year = Some(
                    value
                        .parse::<u16>()
                        .map_err(|_| format!("invalid ACL year {value}"))?,
                )
            }
            "--output" => output = Some(PathBuf::from(value)),
            option => return Err(format!("unsupported ingest-acl option {option}")),
        }
        index += 2;
    }
    if inputs.is_empty() {
        return Err("ingest-acl requires at least one --input XML file".to_string());
    }
    let venue_id = venue_id.ok_or_else(|| "ingest-acl requires --venue".to_string())?;
    let edition_id = edition_id.ok_or_else(|| "ingest-acl requires --edition".to_string())?;
    let year = year.ok_or_else(|| "ingest-acl requires --year".to_string())?;
    if edition_id != format!("{venue_id}:{year}") {
        return Err("ingest-acl edition must match venue:year".to_string());
    }
    Ok(IngestAclArguments {
        inputs,
        venue_id,
        edition_id,
        year,
        output: output.ok_or_else(|| "ingest-acl requires --output".to_string())?,
    })
}

fn ingest_acl(arguments: IngestAclArguments) -> Result<(), String> {
    if let Some(parent) = arguments.output.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("could not create {}: {error}", parent.display()))?;
    }
    let output = File::create(&arguments.output)
        .map_err(|error| format!("could not create {}: {error}", arguments.output.display()))?;
    let mut writer = BufWriter::new(output);
    let mut seen_ids = BTreeSet::new();
    let mut record_count = 0;

    for input_path in &arguments.inputs {
        let xml = fs::read_to_string(input_path)
            .map_err(|error| format!("could not read {}: {error}", input_path.display()))?;
        let document = Document::parse(&xml)
            .map_err(|error| format!("invalid ACL XML {}: {error}", input_path.display()))?;
        let collection = document.root_element();
        let collection_id = collection.attribute("id").unwrap_or_default();
        let is_primary_collection =
            collection_id == format!("{}.{}", arguments.year, arguments.venue_id);
        let is_findings_collection = collection_id == format!("{}.findings", arguments.year);
        if !is_primary_collection && !is_findings_collection {
            return Err(format!(
                "{} is not the primary or Findings collection for {} {}",
                collection_id, arguments.venue_id, arguments.year
            ));
        }

        for volume in collection
            .children()
            .filter(|node| node.has_tag_name("volume"))
        {
            let volume_id = volume.attribute("id").unwrap_or_default();
            if is_findings_collection && volume_id != arguments.venue_id {
                continue;
            }
            let source_group =
                acl_source_group(&arguments.venue_id, volume_id, is_findings_collection);
            let meta = volume
                .children()
                .find(|node| node.has_tag_name("meta"))
                .ok_or_else(|| format!("ACL volume {volume_id} is missing metadata"))?;
            let published_at = acl_publication_date(meta, arguments.year);
            let updated_at = format!(
                "{}T00:00:00Z",
                volume
                    .attribute("ingest-date")
                    .unwrap_or(&published_at[..10])
            );

            for paper in volume.children().filter(|node| node.has_tag_name("paper")) {
                let record =
                    acl_paper_record(&arguments, paper, &source_group, &published_at, &updated_at)?;
                if !seen_ids.insert(record.id.clone()) {
                    return Err(format!("duplicate ACL paper {}", record.id));
                }
                serde_json::to_writer(&mut writer, &record)
                    .map_err(|error| format!("could not encode ACL record: {error}"))?;
                writer
                    .write_all(b"\n")
                    .map_err(|error| format!("could not write ACL records: {error}"))?;
                record_count += 1;
            }
        }
    }
    writer
        .flush()
        .map_err(|error| format!("could not finish ACL records: {error}"))?;
    println!("record_count={record_count}");
    Ok(())
}

fn acl_paper_record(
    arguments: &IngestAclArguments,
    paper: Node<'_, '_>,
    source_group: &ConferenceSourceGroup,
    published_at: &str,
    updated_at: &str,
) -> Result<ConferencePaperRecord, String> {
    let title = child_markup_text(paper, "title");
    let abstract_text = child_markup_text(paper, "abstract");
    let anthology_id = child_markup_text(paper, "url");
    if title.is_empty() || abstract_text.is_empty() || anthology_id.is_empty() {
        return Err(format!(
            "ACL paper {} is missing title, abstract, or URL",
            paper.attribute("id").unwrap_or("unknown")
        ));
    }
    let authors = paper
        .children()
        .filter(|node| node.has_tag_name("author"))
        .map(|author| {
            [
                child_markup_text(author, "first"),
                child_markup_text(author, "last"),
            ]
            .into_iter()
            .filter(|part| !part.is_empty())
            .collect::<Vec<_>>()
            .join(" ")
        })
        .filter(|author| !author.is_empty())
        .collect::<Vec<_>>();
    if authors.is_empty() {
        return Err(format!("ACL paper {anthology_id} has no authors"));
    }
    let landing_url = format!("https://aclanthology.org/{anthology_id}/");
    Ok(ConferencePaperRecord {
        schema_version: 1,
        id: anthology_id.clone(),
        venue_id: arguments.venue_id.clone(),
        edition_id: arguments.edition_id.clone(),
        year: arguments.year,
        title,
        authors,
        abstract_text,
        landing_url: landing_url.clone(),
        pdf_url: Some(format!("https://aclanthology.org/{anthology_id}.pdf")),
        doi: nonempty(child_markup_text(paper, "doi")),
        categories: Vec::new(),
        source_group: Some(ConferenceSourceGroup {
            id: source_group.id.clone(),
            name: source_group.name.clone(),
            kind: source_group.kind.clone(),
        }),
        published_at: published_at.to_string(),
        updated_at: updated_at.to_string(),
        acceptance_status: "published".to_string(),
        provenance_url: landing_url,
    })
}

fn acl_source_group(venue_id: &str, volume_id: &str, is_findings: bool) -> ConferenceSourceGroup {
    let (suffix, name) = if is_findings {
        ("findings", "Findings")
    } else {
        match volume_id {
            "long" => ("long", "Long Papers"),
            "short" => ("short", "Short Papers"),
            "demo" => ("demo", "System Demonstrations"),
            "srw" => ("srw", "Student Research Workshop"),
            "tutorials" => ("tutorials", "Tutorials"),
            "industry" => ("industry", "Industry Track"),
            other => (other, other),
        }
    };
    ConferenceSourceGroup {
        id: format!("{venue_id}.{suffix}"),
        name: name.to_string(),
        kind: "proceedings_track".to_string(),
    }
}

fn acl_publication_date(meta: Node<'_, '_>, fallback_year: u16) -> String {
    let year = child_markup_text(meta, "year")
        .parse::<u16>()
        .unwrap_or(fallback_year);
    let month = match child_markup_text(meta, "month")
        .to_ascii_lowercase()
        .as_str()
    {
        "january" => 1,
        "february" => 2,
        "march" => 3,
        "april" => 4,
        "may" => 5,
        "june" => 6,
        "july" => 7,
        "august" => 8,
        "september" => 9,
        "october" => 10,
        "november" => 11,
        "december" => 12,
        _ => 1,
    };
    format!("{year:04}-{month:02}-01T00:00:00Z")
}

fn child_markup_text(node: Node<'_, '_>, tag_name: &str) -> String {
    node.children()
        .find(|child| child.has_tag_name(tag_name))
        .map(markup_text)
        .unwrap_or_default()
}

fn markup_text(node: Node<'_, '_>) -> String {
    node.descendants()
        .filter(|descendant| descendant.is_text())
        .filter_map(|descendant| descendant.text())
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

fn nonempty(value: String) -> Option<String> {
    (!value.is_empty()).then_some(value)
}

#[derive(Debug)]
struct PackArguments {
    input: PathBuf,
    output: PathBuf,
}

fn parse_pack_arguments(args: Vec<String>) -> Result<PackArguments, String> {
    let mut input = None;
    let mut output = None;
    let mut index = 0;
    while index < args.len() {
        let value = args
            .get(index + 1)
            .ok_or_else(|| format!("{} requires a value", args[index]))?;
        match args[index].as_str() {
            "--input" => input = Some(PathBuf::from(value)),
            "--output" => output = Some(PathBuf::from(value)),
            option => return Err(format!("unsupported pack option {option}")),
        }
        index += 2;
    }
    Ok(PackArguments {
        input: input.ok_or_else(|| "pack requires --input".to_string())?,
        output: output.ok_or_else(|| "pack requires --output".to_string())?,
    })
}

fn validate_site(root: &Path) -> Result<(), String> {
    let manifest_path = root.join(MANIFEST_PATH);
    let manifest: Manifest = serde_json::from_reader(
        File::open(&manifest_path)
            .map_err(|error| format!("could not open {}: {error}", manifest_path.display()))?,
    )
    .map_err(|error| format!("invalid {}: {error}", manifest_path.display()))?;
    if manifest.schema_version != 1 || manifest.dataset != "apaper.conferences" {
        return Err("conference manifest uses an unsupported contract".to_string());
    }
    if manifest.venues.is_empty() {
        return Err("conference manifest contains no venues".to_string());
    }

    let mut edition_ids = std::collections::BTreeSet::new();
    for venue in &manifest.venues {
        if venue.id.trim().is_empty() || venue.short_name.trim().is_empty() {
            return Err("conference venue identifiers and names are required".to_string());
        }
        for edition in &venue.editions {
            if edition.id != format!("{}:{}", venue.id, edition.year) {
                return Err(format!(
                    "edition {} does not match its venue and year",
                    edition.id
                ));
            }
            if !edition_ids.insert(edition.id.clone()) {
                return Err(format!("duplicate edition {}", edition.id));
            }
            if let Some(pack) = &edition.pack {
                validate_pack_reference(root, venue, edition, pack)?;
            }
        }
    }
    println!(
        "validated {} venues and {} exact editions",
        manifest.venues.len(),
        edition_ids.len()
    );
    Ok(())
}

fn validate_pack_reference(
    root: &Path,
    venue: &Venue,
    edition: &Edition,
    pack: &PackReference,
) -> Result<(), String> {
    if pack.record_count != edition.paper_count || pack.record_count > MAX_PACK_RECORDS {
        return Err(format!("{} has an invalid record count", edition.id));
    }
    if pack.compressed_bytes > MAX_PACK_COMPRESSED_BYTES {
        return Err(format!("{} exceeds the compressed size policy", edition.id));
    }
    let path = root.join("v1/conferences").join(&pack.path);
    let metadata =
        fs::metadata(&path).map_err(|error| format!("missing pack {}: {error}", path.display()))?;
    if metadata.len() != pack.compressed_bytes {
        return Err(format!(
            "{} compressed size does not match the manifest",
            edition.id
        ));
    }
    let bytes =
        fs::read(&path).map_err(|error| format!("could not read {}: {error}", path.display()))?;
    if sha256_hex(&bytes) != pack.sha256 {
        return Err(format!(
            "{} SHA-256 does not match the manifest",
            edition.id
        ));
    }
    let decoder = zstd::stream::read::Decoder::new(bytes.as_slice())
        .map_err(|error| format!("could not decode {}: {error}", edition.id))?;
    let mut record_count = 0;
    for line in BufReader::new(decoder).lines() {
        let line = line.map_err(|error| format!("could not read {}: {error}", edition.id))?;
        let paper: ConferencePaperRecord = serde_json::from_str(&line)
            .map_err(|error| format!("invalid record in {}: {error}", edition.id))?;
        validate_record(&paper, &venue.id, &edition.id, edition.year)?;
        record_count += 1;
    }
    if record_count != pack.record_count {
        return Err(format!(
            "{} decoded record count does not match the manifest",
            edition.id
        ));
    }
    Ok(())
}

fn pack(arguments: PackArguments) -> Result<(), String> {
    let input = File::open(&arguments.input)
        .map_err(|error| format!("could not open {}: {error}", arguments.input.display()))?;
    if let Some(parent) = arguments.output.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("could not create {}: {error}", parent.display()))?;
    }
    let temporary_path = arguments.output.with_extension("zst.partial");
    let output = File::create(&temporary_path)
        .map_err(|error| format!("could not create {}: {error}", temporary_path.display()))?;
    let mut encoder = zstd::stream::write::Encoder::new(BufWriter::new(output), 9)
        .map_err(|error| format!("could not start zstd encoding: {error}"))?;
    let mut count = 0;
    for line in BufReader::new(input).lines() {
        let line = line.map_err(|error| format!("could not read input: {error}"))?;
        if line.trim().is_empty() {
            continue;
        }
        let paper: ConferencePaperRecord = serde_json::from_str(&line)
            .map_err(|error| format!("invalid normalized record: {error}"))?;
        validate_record(&paper, &paper.venue_id, &paper.edition_id, paper.year)?;
        serde_json::to_writer(&mut encoder, &paper)
            .map_err(|error| format!("could not encode normalized record: {error}"))?;
        encoder
            .write_all(b"\n")
            .map_err(|error| format!("could not write pack: {error}"))?;
        count += 1;
        if count > MAX_PACK_RECORDS {
            return Err(format!(
                "one edition may contain at most {MAX_PACK_RECORDS} records"
            ));
        }
    }
    encoder
        .finish()
        .map_err(|error| format!("could not finish zstd encoding: {error}"))?;
    fs::rename(&temporary_path, &arguments.output)
        .map_err(|error| format!("could not publish {}: {error}", arguments.output.display()))?;
    let bytes = fs::read(&arguments.output)
        .map_err(|error| format!("could not read {}: {error}", arguments.output.display()))?;
    println!("record_count={count}");
    println!("compressed_bytes={}", bytes.len());
    println!("sha256={}", sha256_hex(&bytes));
    Ok(())
}

fn validate_record(
    paper: &ConferencePaperRecord,
    venue_id: &str,
    edition_id: &str,
    year: u16,
) -> Result<(), String> {
    if paper.schema_version != 1
        || paper.id.trim().is_empty()
        || paper.title.trim().is_empty()
        || paper.authors.is_empty()
        || paper.landing_url.trim().is_empty()
        || paper.provenance_url.trim().is_empty()
        || paper.venue_id != venue_id
        || paper.edition_id != edition_id
        || paper.year != year
        || paper.source_group.as_ref().is_some_and(|group| {
            group.id.trim().is_empty()
                || group.id.len() > 128
                || group.name.trim().is_empty()
                || group.name.len() > 256
                || group.kind.trim().is_empty()
                || group.kind.len() > 64
        })
    {
        return Err(format!(
            "record {} violates the conference pack contract",
            paper.id
        ));
    }
    Ok(())
}

fn sha256_hex(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn acl_markup_text_preserves_inline_content_once() {
        let document = Document::parse(
            "<paper><title>Learning <fixed-case>LLM</fixed-case> Systems</title></paper>",
        )
        .unwrap();

        assert_eq!(
            child_markup_text(document.root_element(), "title"),
            "Learning LLM Systems"
        );
    }

    #[test]
    fn acl_tracks_are_source_native_groups() {
        assert_eq!(acl_source_group("acl", "long", false).id, "acl.long");
        assert_eq!(acl_source_group("acl", "acl", true).id, "acl.findings");
    }
}
