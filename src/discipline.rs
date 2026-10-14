//! Additive source-level discipline contract. Publisher paper categories are separate.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct DisciplineTaxonomy {
    pub id: String,
    pub name: String,
    pub version: String,
    pub reference_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Discipline {
    pub id: String,
    pub code: String,
    pub name: String,
    pub localized_names: BTreeMap<String, String>,
    pub display_order: u32,
}

pub fn validate_disciplines<'a>(
    taxonomy: Option<&DisciplineTaxonomy>,
    disciplines: &[Discipline],
    assignments: impl Iterator<Item = &'a [String]>,
) -> Result<(), String> {
    let Some(taxonomy) = taxonomy else {
        if !disciplines.is_empty() || assignments.into_iter().any(|ids| !ids.is_empty()) {
            return Err("discipline references require a taxonomy".into());
        }
        return Ok(()); // Valid legacy catalogs remain usable.
    };
    if taxonomy.id.trim().is_empty()
        || taxonomy.name.trim().is_empty()
        || taxonomy.version.trim().is_empty()
        || !taxonomy.reference_url.starts_with("https://")
    {
        return Err("invalid discipline taxonomy provenance".into());
    }
    let mut ids = BTreeSet::new();
    let mut codes = BTreeSet::new();
    let mut orders = BTreeSet::new();
    for discipline in disciplines {
        if !discipline.id.starts_with(&format!("{}:", taxonomy.id))
            || discipline.id.len() <= taxonomy.id.len() + 1
            || discipline.code.trim().is_empty()
            || discipline.name.trim().is_empty()
            || ["en", "zh-Hans"].iter().any(|locale| {
                discipline
                    .localized_names
                    .get(*locale)
                    .is_none_or(|name| name.trim().is_empty())
            })
            || !ids.insert(discipline.id.as_str())
            || !codes.insert(discipline.code.as_str())
            || !orders.insert(discipline.display_order)
        {
            return Err("invalid or duplicate discipline definition".into());
        }
    }
    for references in assignments {
        let mut seen = BTreeSet::new();
        if references.is_empty()
            || references
                .iter()
                .any(|id| !ids.contains(id.as_str()) || !seen.insert(id))
        {
            return Err("missing, undefined or duplicate venue discipline reference".into());
        }
    }
    Ok(())
}
