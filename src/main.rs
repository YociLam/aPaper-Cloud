use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
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
    published_at: String,
    updated_at: String,
    acceptance_status: String,
    provenance_url: String,
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
        _ => Err(
            "usage: apaper-cloud validate-site <public-dir> | pack --input <jsonl> --output <jsonl.zst>"
                .to_string(),
        ),
    }
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
