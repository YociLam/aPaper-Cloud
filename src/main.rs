use roxmltree::{Document, Node};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};

const MANIFEST_PATH: &str = "v1/conferences/manifest.json";
const VERSION_PATH: &str = "v1/conferences/version.json";
const MAX_PACK_RECORDS: usize = 30_000;
const MAX_PACK_COMPRESSED_BYTES: u64 = 128 * 1024 * 1024;

#[derive(Debug, Deserialize)]
struct Manifest {
    schema_version: u32,
    manifest_version: String,
    dataset: String,
    generated_at: String,
    venues: Vec<Venue>,
}

#[derive(Debug, Deserialize)]
struct ManifestVersion {
    schema_version: u32,
    dataset: String,
    manifest_version: String,
    updated_at: String,
    manifest_sha256: String,
}

#[derive(Debug, Deserialize)]
struct Venue {
    id: String,
    short_name: String,
    name: String,
    localized_names: BTreeMap<String, String>,
    #[serde(default)]
    localized_tag: BTreeMap<String, String>,
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
    #[serde(default, skip_serializing_if = "Option::is_none")]
    metadata_channel: Option<String>,
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
        Some("import-json") => import_json(parse_import_json_arguments(args.collect())?),
        _ => Err(
            "usage: apaper-cloud validate-site <public-dir> | pack --input <jsonl> --output <jsonl.zst> | ingest-acl --input <xml> [--input <xml>] --venue <id> --edition <id:year> --year <yyyy> --output <jsonl> | import-json --input <json> --venue <id> --edition <id:year> --year <yyyy> --output <jsonl>"
                .to_string(),
        ),
    }
}

#[derive(Debug)]
struct ImportJsonArguments {
    input: PathBuf,
    venue_id: String,
    edition_id: String,
    year: u16,
    output: PathBuf,
}

#[derive(Debug, Deserialize)]
struct ImportedPaperRecord {
    id: String,
    #[serde(default)]
    source_paper_id: String,
    #[serde(default)]
    doi: String,
    title: String,
    #[serde(rename = "abstract", default)]
    abstract_text: String,
    #[serde(default)]
    authors: Vec<String>,
    #[serde(default)]
    categories: Vec<String>,
    #[serde(default)]
    source_group: Option<ConferenceSourceGroup>,
    #[serde(default)]
    published: Option<String>,
    link: String,
    #[serde(default)]
    pdf_url: Option<String>,
    #[serde(default)]
    updated_at: Option<String>,
}

fn parse_import_json_arguments(args: Vec<String>) -> Result<ImportJsonArguments, String> {
    let mut input = None;
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
            "--input" => input = Some(PathBuf::from(value)),
            "--venue" => venue_id = Some(value.to_string()),
            "--edition" => edition_id = Some(value.to_string()),
            "--year" => {
                year = Some(
                    value
                        .parse::<u16>()
                        .map_err(|_| format!("invalid import year {value}"))?,
                )
            }
            "--output" => output = Some(PathBuf::from(value)),
            option => return Err(format!("unsupported import-json option {option}")),
        }
        index += 2;
    }
    let venue_id = venue_id.ok_or_else(|| "import-json requires --venue".to_string())?;
    let edition_id = edition_id.ok_or_else(|| "import-json requires --edition".to_string())?;
    let year = year.ok_or_else(|| "import-json requires --year".to_string())?;
    if edition_id != format!("{venue_id}:{year}") {
        return Err("import-json edition must match venue:year".to_string());
    }
    Ok(ImportJsonArguments {
        input: input.ok_or_else(|| "import-json requires --input".to_string())?,
        venue_id,
        edition_id,
        year,
        output: output.ok_or_else(|| "import-json requires --output".to_string())?,
    })
}

fn import_json(arguments: ImportJsonArguments) -> Result<(), String> {
    let input = File::open(&arguments.input)
        .map_err(|error| format!("could not open {}: {error}", arguments.input.display()))?;
    let imported: Vec<ImportedPaperRecord> = serde_json::from_reader(input).map_err(|error| {
        format!(
            "invalid imported JSON {}: {error}",
            arguments.input.display()
        )
    })?;
    if let Some(parent) = arguments.output.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("could not create {}: {error}", parent.display()))?;
    }
    let output = File::create(&arguments.output)
        .map_err(|error| format!("could not create {}: {error}", arguments.output.display()))?;
    let mut writer = BufWriter::new(output);
    let mut seen_ids = BTreeSet::new();
    let mut record_count = 0;
    let mut skipped_incomplete = 0;
    for imported in imported {
        let id = nonempty(imported.source_paper_id).unwrap_or(imported.id);
        let title = normalize_title_markup(&imported.title);
        let abstract_text = normalize_imported_abstract(&imported.abstract_text);
        let authors = imported
            .authors
            .into_iter()
            .map(|author| author.split_whitespace().collect::<Vec<_>>().join(" "))
            .filter(|author| !author.is_empty())
            .collect::<Vec<_>>();
        if id.trim().is_empty()
            || title.is_empty()
            || abstract_text.is_empty()
            || authors.is_empty()
            || imported.link.trim().is_empty()
        {
            skipped_incomplete += 1;
            continue;
        }
        if !seen_ids.insert(id.clone()) {
            return Err(format!("duplicate imported paper {id}"));
        }
        let published_at = imported
            .published
            .filter(|value| !value.trim().is_empty())
            .unwrap_or_else(|| format!("{:04}-01-01T00:00:00Z", arguments.year));
        let record = ConferencePaperRecord {
            schema_version: 1,
            id,
            venue_id: arguments.venue_id.clone(),
            edition_id: arguments.edition_id.clone(),
            year: arguments.year,
            title,
            authors,
            abstract_text,
            landing_url: imported.link.clone(),
            pdf_url: imported.pdf_url.filter(|value| !value.trim().is_empty()),
            doi: nonempty(imported.doi),
            categories: imported
                .categories
                .into_iter()
                .filter(|value| !value.trim().is_empty())
                .collect(),
            source_group: imported.source_group.filter(|group| {
                !group.id.trim().is_empty()
                    && !group.name.trim().is_empty()
                    && !group.kind.trim().is_empty()
            }),
            published_at: published_at.clone(),
            updated_at: imported
                .updated_at
                .filter(|value| !value.trim().is_empty())
                .unwrap_or(published_at),
            acceptance_status: "published".to_string(),
            provenance_url: imported.link,
            metadata_channel: None,
        };
        serde_json::to_writer(&mut writer, &record)
            .map_err(|error| format!("could not encode imported record: {error}"))?;
        writer
            .write_all(b"\n")
            .map_err(|error| format!("could not write imported records: {error}"))?;
        record_count += 1;
    }
    writer
        .flush()
        .map_err(|error| format!("could not finish imported records: {error}"))?;
    println!("record_count={record_count}");
    println!("skipped_incomplete={skipped_incomplete}");
    Ok(())
}

fn normalize_imported_abstract(value: &str) -> String {
    let words = value.split_whitespace().collect::<Vec<_>>();
    if words.len() % 2 == 0 {
        let midpoint = words.len() / 2;
        if words[..midpoint] == words[midpoint..] {
            return words[..midpoint].join(" ");
        }
    }
    words.join(" ")
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
    let mut skipped_incomplete = 0;

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
                let Some(record) =
                    acl_paper_record(&arguments, paper, &source_group, &published_at, &updated_at)?
                else {
                    skipped_incomplete += 1;
                    continue;
                };
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
    println!("skipped_incomplete={skipped_incomplete}");
    Ok(())
}

fn acl_paper_record(
    arguments: &IngestAclArguments,
    paper: Node<'_, '_>,
    source_group: &ConferenceSourceGroup,
    published_at: &str,
    updated_at: &str,
) -> Result<Option<ConferencePaperRecord>, String> {
    let title = normalize_title_markup(&child_markup_text(paper, "title"));
    let abstract_text = child_markup_text(paper, "abstract");
    let anthology_id = child_markup_text(paper, "url");
    if title.is_empty() || abstract_text.is_empty() || anthology_id.is_empty() {
        return Ok(None);
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
        return Ok(None);
    }
    let landing_url = format!("https://aclanthology.org/{anthology_id}/");
    Ok(Some(ConferencePaperRecord {
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
        metadata_channel: None,
    }))
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

fn normalize_title_markup(value: &str) -> String {
    let normalized = normalize_title_fragment(value)
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    let trimmed = normalized.trim();
    for quote in ['"', '\''] {
        if let Some(unquoted) = trimmed
            .strip_prefix(quote)
            .and_then(|value| value.strip_suffix(quote))
        {
            return unquoted.trim().to_string();
        }
    }
    normalized
}

fn normalize_title_fragment(value: &str) -> String {
    let characters = value.chars().collect::<Vec<_>>();
    let mut output = String::new();
    let mut index = 0;
    while index < characters.len() {
        match characters[index] {
            '\\' => normalize_title_command(&characters, &mut index, &mut output),
            '{' => {
                let (content, next) = title_group(&characters, index);
                output.push_str(&normalize_title_fragment(&content));
                index = next;
            }
            '}' => index += 1,
            '$' => {
                let start = index;
                while index < characters.len() && characters[index] == '$' {
                    index += 1;
                }
                if index - start >= 3 {
                    output.extend(std::iter::repeat('$').take(index - start));
                }
            }
            '^' => {
                index += 1;
                let content = if index < characters.len() && characters[index] == '{' {
                    let (content, next) = title_group(&characters, index);
                    index = next;
                    content
                } else if index < characters.len() {
                    let content = characters[index].to_string();
                    index += 1;
                    content
                } else {
                    String::new()
                };
                output.push_str(&title_superscript(&normalize_title_fragment(&content)));
            }
            '_' => {
                output.push('_');
                index += 1;
                if index < characters.len() && characters[index] == '{' {
                    let (content, next) = title_group(&characters, index);
                    output.push_str(&normalize_title_fragment(&content));
                    index = next;
                }
            }
            character => {
                output.push(character);
                index += 1;
            }
        }
    }
    output
}

fn normalize_title_command(characters: &[char], index: &mut usize, output: &mut String) {
    while *index < characters.len() && characters[*index] == '\\' {
        *index += 1;
    }
    if *index >= characters.len() {
        return;
    }
    let escaped = characters[*index];
    if matches!(escaped, '&' | '_' | '%' | '#' | '$' | '{' | '}') {
        output.push(escaped);
        *index += 1;
        return;
    }
    if matches!(escaped, '(' | ')' | '[' | ']') {
        *index += 1;
        return;
    }
    if escaped.is_whitespace() || matches!(escaped, ',' | ';' | ':' | '!') {
        output.push(' ');
        *index += 1;
        return;
    }
    if matches!(escaped, '"' | '\'' | '`' | '^' | '~') {
        let accent = escaped;
        *index += 1;
        let base = title_command_argument(characters, index);
        output.push_str(&apply_title_accent(accent, &base));
        return;
    }
    if !escaped.is_ascii_alphabetic() {
        output.push(' ');
        return;
    }

    let start = *index;
    while *index < characters.len() && characters[*index].is_ascii_alphabetic() {
        *index += 1;
    }
    let command = characters[start..*index].iter().collect::<String>();
    let formatting = [
        "boldsymbol",
        "underline",
        "mathcal",
        "mathbf",
        "mathrm",
        "mathtt",
        "mathbb",
        "textrm",
        "texttt",
        "textbf",
        "textit",
        "emph",
        "text",
        "widetilde",
        "tilde",
        "rm",
        "it",
        "bf",
    ];
    if let Some(prefix) = formatting
        .iter()
        .find(|candidate| command.starts_with(**candidate))
    {
        output.push_str(command.strip_prefix(prefix).unwrap_or_default());
        if *index < characters.len() && characters[*index] == '{' {
            let (content, next) = title_group(characters, *index);
            output.push_str(&normalize_title_fragment(&content));
            *index = next;
        }
        return;
    }
    if command.starts_with("frac") {
        output.push_str(command.strip_prefix("frac").unwrap_or_default());
        let numerator = title_command_argument(characters, index);
        let denominator = title_command_argument(characters, index);
        output.push_str(&normalize_title_fragment(&numerator));
        if !denominator.is_empty() {
            output.push('/');
            output.push_str(&normalize_title_fragment(&denominator));
        }
        return;
    }
    if command.starts_with("sqrt") {
        output.push('√');
        output.push_str(command.strip_prefix("sqrt").unwrap_or_default());
        let argument = title_command_argument(characters, index);
        output.push_str(&normalize_title_fragment(&argument));
        return;
    }

    let symbols = [
        ("varepsilon", "ε"),
        ("nrightarrow", "↛"),
        ("Rightarrow", "⇒"),
        ("boldsymbol", ""),
        ("natural", "♮"),
        ("partial", "∂"),
        ("approx", "≈"),
        ("oslash", "⊘"),
        ("epsilon", "ε"),
        ("lambda", "λ"),
        ("varphi", "φ"),
        ("infty", "∞"),
        ("nabla", "∇"),
        ("Theta", "Θ"),
        ("Delta", "Δ"),
        ("sigma", "σ"),
        ("omega", "ω"),
        ("alpha", "α"),
        ("gamma", "γ"),
        ("times", "×"),
        ("exists", "∃"),
        ("sharp", "♯"),
        ("beta", "β"),
        ("neq", "≠"),
        ("star", "⋆"),
        ("circ", "∘"),
        ("Phi", "Φ"),
        ("Psi", "Ψ"),
        ("phi", "φ"),
        ("psi", "ψ"),
        ("tau", "τ"),
        ("ell", "ℓ"),
        ("mu", "μ"),
        ("Pi", "Π"),
        ("pi", "π"),
        ("chi", "χ"),
        ("log", "log"),
    ];
    if let Some((prefix, replacement)) = symbols
        .iter()
        .find(|(candidate, _)| command.starts_with(*candidate))
    {
        output.push_str(replacement);
        output.push_str(command.strip_prefix(prefix).unwrap_or_default());
    } else {
        output.push('\\');
        output.push_str(&command);
    }
}

fn title_has_unsupported_markup(value: &str) -> bool {
    let characters = value.chars().collect::<Vec<_>>();
    let mut index = 0;
    while index < characters.len() {
        match characters[index] {
            '\\' | '{' | '}' => return true,
            '$' => {
                let start = index;
                while index < characters.len() && characters[index] == '$' {
                    index += 1;
                }
                if index - start < 3 {
                    return true;
                }
            }
            _ => index += 1,
        }
    }
    false
}

fn title_group(characters: &[char], start: usize) -> (String, usize) {
    let mut depth = 0;
    let mut index = start;
    let mut content = String::new();
    while index < characters.len() {
        match characters[index] {
            '{' => {
                if depth > 0 {
                    content.push('{');
                }
                depth += 1;
            }
            '}' => {
                depth -= 1;
                if depth == 0 {
                    return (content, index + 1);
                }
                content.push('}');
            }
            character => content.push(character),
        }
        index += 1;
    }
    (content, index)
}

fn title_command_argument(characters: &[char], index: &mut usize) -> String {
    while *index < characters.len() && characters[*index].is_whitespace() {
        *index += 1;
    }
    if *index < characters.len() && characters[*index] == '{' {
        let (content, next) = title_group(characters, *index);
        *index = next;
        content
    } else if *index < characters.len() {
        let content = characters[*index].to_string();
        *index += 1;
        content
    } else {
        String::new()
    }
}

fn apply_title_accent(accent: char, value: &str) -> String {
    let mut characters = value.chars();
    let Some(base) = characters.next() else {
        return String::new();
    };
    let accented = match (accent, base) {
        ('"', 'a') => 'ä',
        ('"', 'A') => 'Ä',
        ('"', 'e') => 'ë',
        ('"', 'E') => 'Ë',
        ('"', 'i') => 'ï',
        ('"', 'I') => 'Ï',
        ('"', 'o') => 'ö',
        ('"', 'O') => 'Ö',
        ('"', 'u') => 'ü',
        ('"', 'U') => 'Ü',
        ('"', 'y') => 'ÿ',
        ('\'', 'a') => 'á',
        ('\'', 'A') => 'Á',
        ('\'', 'e') => 'é',
        ('\'', 'E') => 'É',
        ('\'', 'i') => 'í',
        ('\'', 'I') => 'Í',
        ('\'', 'o') => 'ó',
        ('\'', 'O') => 'Ó',
        ('\'', 'u') => 'ú',
        ('\'', 'U') => 'Ú',
        ('`', 'a') => 'à',
        ('`', 'e') => 'è',
        ('`', 'i') => 'ì',
        ('`', 'o') => 'ò',
        ('`', 'u') => 'ù',
        ('^', 'a') => 'â',
        ('^', 'e') => 'ê',
        ('^', 'i') => 'î',
        ('^', 'o') => 'ô',
        ('^', 'u') => 'û',
        ('~', 'a') => 'ã',
        ('~', 'n') => 'ñ',
        ('~', 'o') => 'õ',
        _ => base,
    };
    format!("{accented}{}", characters.collect::<String>())
}

fn title_superscript(value: &str) -> String {
    let value = value.trim();
    let mapped = value
        .chars()
        .map(|character| match character {
            '0' => Some('⁰'),
            '1' => Some('¹'),
            '2' => Some('²'),
            '3' => Some('³'),
            '4' => Some('⁴'),
            '5' => Some('⁵'),
            '6' => Some('⁶'),
            '7' => Some('⁷'),
            '8' => Some('⁸'),
            '9' => Some('⁹'),
            '+' => Some('⁺'),
            '-' => Some('⁻'),
            '=' => Some('⁼'),
            '(' => Some('⁽'),
            ')' => Some('⁾'),
            '/' => Some('ᐟ'),
            '.' => Some('·'),
            '*' => Some('⁎'),
            'α' => Some('ᵅ'),
            'π' => Some('π'),
            '♮' => Some('♮'),
            ' ' => Some(' '),
            'a' => Some('ᵃ'),
            'b' => Some('ᵇ'),
            'c' => Some('ᶜ'),
            'd' => Some('ᵈ'),
            'e' => Some('ᵉ'),
            'f' => Some('ᶠ'),
            'g' => Some('ᵍ'),
            'h' => Some('ʰ'),
            'i' => Some('ⁱ'),
            'j' => Some('ʲ'),
            'k' => Some('ᵏ'),
            'l' => Some('ˡ'),
            'm' => Some('ᵐ'),
            'n' => Some('ⁿ'),
            'o' => Some('ᵒ'),
            'p' => Some('ᵖ'),
            'r' => Some('ʳ'),
            's' => Some('ˢ'),
            't' => Some('ᵗ'),
            'u' => Some('ᵘ'),
            'v' => Some('ᵛ'),
            'w' => Some('ʷ'),
            'x' => Some('ˣ'),
            'y' => Some('ʸ'),
            'z' => Some('ᶻ'),
            'A' => Some('ᴬ'),
            'B' => Some('ᴮ'),
            'C' => Some('ᶜ'),
            'D' => Some('ᴰ'),
            'E' => Some('ᴱ'),
            'F' => Some('ᶠ'),
            'G' => Some('ᴳ'),
            'H' => Some('ᴴ'),
            'I' => Some('ᴵ'),
            'J' => Some('ᴶ'),
            'K' => Some('ᴷ'),
            'L' => Some('ᴸ'),
            'M' => Some('ᴹ'),
            'N' => Some('ᴺ'),
            'O' => Some('ᴼ'),
            'P' => Some('ᴾ'),
            'Q' => Some('Q'),
            'R' => Some('ᴿ'),
            'S' => Some('ˢ'),
            'T' => Some('ᵀ'),
            'U' => Some('ᵁ'),
            'V' => Some('ⱽ'),
            'W' => Some('ᵂ'),
            'X' => Some('ˣ'),
            'Y' => Some('ʸ'),
            'Z' => Some('ᶻ'),
            _ => None,
        })
        .collect::<Option<String>>();
    mapped.unwrap_or_else(|| format!("↑{value}"))
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
    let manifest_bytes = fs::read(&manifest_path)
        .map_err(|error| format!("could not open {}: {error}", manifest_path.display()))?;
    let manifest: Manifest = serde_json::from_reader(manifest_bytes.as_slice())
        .map_err(|error| format!("invalid {}: {error}", manifest_path.display()))?;
    if manifest.schema_version != 1
        || !valid_manifest_version(&manifest.manifest_version)
        || manifest.dataset != "apaper.conferences"
    {
        return Err("conference manifest uses an unsupported contract".to_string());
    }
    let version_path = root.join(VERSION_PATH);
    let version: ManifestVersion = serde_json::from_reader(
        File::open(&version_path)
            .map_err(|error| format!("could not open {}: {error}", version_path.display()))?,
    )
    .map_err(|error| format!("invalid {}: {error}", version_path.display()))?;
    let manifest_digest = format!("{:x}", Sha256::digest(&manifest_bytes));
    if version.schema_version != manifest.schema_version
        || version.dataset != manifest.dataset
        || version.manifest_version != manifest.manifest_version
        || version.updated_at != manifest.generated_at
        || version.manifest_sha256 != manifest_digest
    {
        return Err("conference version metadata does not match the manifest".to_string());
    }
    if manifest.venues.is_empty() {
        return Err("conference manifest contains no venues".to_string());
    }

    let mut edition_ids = std::collections::BTreeSet::new();
    for venue in &manifest.venues {
        if venue.id.trim().is_empty()
            || venue.short_name.trim().is_empty()
            || venue.name.trim().is_empty()
            || venue.localized_names.len() < 2
            || venue.localized_names.get("en").map(String::as_str) != Some(venue.name.as_str())
            || venue
                .localized_names
                .get("zh-Hans")
                .is_none_or(|value| value.trim().is_empty())
            || venue.localized_names.iter().any(|(language, value)| {
                language.trim().is_empty()
                    || language.len() > 32
                    || value.trim().is_empty()
                    || value.len() > 256
            })
            || venue.localized_tag.iter().any(|(language, value)| {
                language.trim().is_empty()
                    || language.len() > 32
                    || value.trim().is_empty()
                    || value.len() > 96
            })
            || (!venue.localized_tag.is_empty()
                && (!venue.localized_tag.contains_key("en")
                    || !venue.localized_tag.contains_key("zh-Hans")))
        {
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

fn valid_manifest_version(version: &str) -> bool {
    let Some((major, minor)) = version.split_once('.') else {
        return false;
    };
    !major.is_empty()
        && !minor.is_empty()
        && !minor.contains('.')
        && major.chars().all(|character| character.is_ascii_digit())
        && minor.chars().all(|character| character.is_ascii_digit())
        && (major == "0" || !major.starts_with('0'))
        && (minor == "0" || !minor.starts_with('0'))
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
    let mut normalized_title_count = 0;
    for line in BufReader::new(input).lines() {
        let line = line.map_err(|error| format!("could not read input: {error}"))?;
        if line.trim().is_empty() {
            continue;
        }
        let mut paper: ConferencePaperRecord = serde_json::from_str(&line)
            .map_err(|error| format!("invalid normalized record: {error}"))?;
        let normalized_title = normalize_title_markup(&paper.title);
        if normalized_title != paper.title {
            paper.title = normalized_title;
            normalized_title_count += 1;
        }
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
    println!("normalized_title_count={normalized_title_count}");
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
        || normalize_title_markup(&paper.title) != paper.title
        || title_has_unsupported_markup(&paper.title)
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
    fn manifest_version_requires_two_numeric_segments() {
        assert!(valid_manifest_version("0.9"));
        assert!(valid_manifest_version("0.10"));
        assert!(valid_manifest_version("1.0"));
        assert!(!valid_manifest_version("9"));
        assert!(!valid_manifest_version("0.9.1"));
        assert!(!valid_manifest_version("0.09"));
    }

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
    fn conference_titles_remove_latex_formatting_without_losing_text() {
        assert_eq!(
            normalize_title_markup(r"\texttt{Droid}: A Resource Suite"),
            "Droid: A Resource Suite"
        );
        assert_eq!(
            normalize_title_markup(r"\textit{Do It Yourself (DIY)} Evaluation"),
            "Do It Yourself (DIY) Evaluation"
        );
        assert_eq!(
            normalize_title_markup(r"\mathrm{Wojood^{Relations}}: A Benchmark"),
            "Wojoodᴿᵉˡᵃᵗⁱᵒⁿˢ: A Benchmark"
        );
    }

    #[test]
    fn conference_titles_render_math_and_escaped_characters_as_plain_unicode() {
        assert_eq!(normalize_title_markup(r"$\\beta$-VAE"), "β-VAE");
        assert_eq!(
            normalize_title_markup(r"Memorization \neq Understanding"),
            "Memorization ≠ Understanding"
        );
        assert_eq!(
            normalize_title_markup(r"LLM\timesMapReduce-V3"),
            "LLM×MapReduce-V3"
        );
        assert_eq!(normalize_title_markup(r"L\\_2-Norm"), "L_2-Norm");
        assert_eq!(
            normalize_title_markup(r"\\(\\varepsilon\\)-Optimally"),
            "ε-Optimally"
        );
    }

    #[test]
    fn conference_titles_render_bibtex_accents() {
        assert_eq!(normalize_title_markup(r#"Schr\\"{o}dinger"#), "Schrödinger");
        assert_eq!(normalize_title_markup(r#"Nystr{\\"o}m"#), "Nyström");
        assert_eq!(normalize_title_markup(r"Fr\\'{e}chet"), "Fréchet");
    }

    #[test]
    fn conference_titles_preserve_semantic_superscripts_and_literal_currency() {
        assert_eq!(normalize_title_markup(r"I$^2$SB"), "I²SB");
        assert_eq!(normalize_title_markup(r"$O(1/k^3)$"), "O(1/k³)");
        assert_eq!(normalize_title_markup(r"E$^{FWI}$"), "Eᶠᵂᴵ");
        assert_eq!(normalize_title_markup(r"C$^*$"), "C⁎");
        assert_eq!(
            normalize_title_markup("DemoFusion With No $$$"),
            "DemoFusion With No $$$"
        );
        assert_eq!(
            normalize_title_markup("'Quoted upstream title'"),
            "Quoted upstream title"
        );
    }

    #[test]
    fn conference_titles_reject_unknown_source_markup() {
        let title = normalize_title_markup(r"An \unknown{Title}");
        assert_eq!(title, r"An \unknownTitle");
        assert!(title_has_unsupported_markup(&title));
        assert!(!title_has_unsupported_markup("DemoFusion With No $$$"));
    }

    #[test]
    fn acl_tracks_are_source_native_groups() {
        assert_eq!(acl_source_group("acl", "long", false).id, "acl.long");
        assert_eq!(acl_source_group("acl", "acl", true).id, "acl.findings");
    }

    #[test]
    fn acl_records_without_abstracts_are_skipped_without_aborting_the_edition() {
        let document = Document::parse(
            "<paper id=\"1\"><title>Incomplete paper</title><url>2024.acl-long.1</url><author><first>Ada</first><last>Lovelace</last></author></paper>",
        )
        .unwrap();
        let arguments = IngestAclArguments {
            inputs: Vec::new(),
            venue_id: "acl".to_string(),
            edition_id: "acl:2024".to_string(),
            year: 2024,
            output: PathBuf::new(),
        };
        let group = acl_source_group("acl", "long", false);

        assert!(acl_paper_record(
            &arguments,
            document.root_element(),
            &group,
            "2024-01-01T00:00:00Z",
            "2024-01-01T00:00:00Z",
        )
        .unwrap()
        .is_none());
    }

    #[test]
    fn imported_records_keep_only_complete_searchable_metadata() {
        let root = std::env::temp_dir().join(format!(
            "apaper-cloud-import-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&root).unwrap();
        let input = root.join("papers.json");
        let output = root.join("papers.jsonl");
        fs::write(
            &input,
            r#"[
                {"id":"complete","title":"A complete paper","abstract":"Useful abstract","authors":["Ada Lovelace"],"link":"https://example.com/complete"},
                {"id":"missing-abstract","title":"Incomplete","authors":["Grace Hopper"],"link":"https://example.com/incomplete"}
            ]"#,
        )
        .unwrap();

        import_json(ImportJsonArguments {
            input,
            venue_id: "cvpr".to_string(),
            edition_id: "cvpr:2025".to_string(),
            year: 2025,
            output: output.clone(),
        })
        .unwrap();

        let lines = fs::read_to_string(output).unwrap();
        assert_eq!(lines.lines().count(), 1);
        assert!(lines.contains("complete"));
        assert!(!lines.contains("missing-abstract"));
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn imported_abstracts_collapse_exact_upstream_duplication() {
        assert_eq!(
            normalize_imported_abstract("A complete abstract. A complete abstract."),
            "A complete abstract."
        );
        assert_eq!(
            normalize_imported_abstract("A complete abstract with a distinct conclusion."),
            "A complete abstract with a distinct conclusion."
        );
    }
}
