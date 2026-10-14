use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct JournalIdentity {
    pub title: String,
    pub publisher: String,
    pub issns: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct JournalArticleMetadata {
    #[serde(flatten)]
    pub identity: JournalIdentity,
    pub article_type: String,
    pub volume: Option<String>,
    pub issue: Option<String>,
    pub article_number: Option<String>,
    pub pages: Option<String>,
    pub provenance_urls: Vec<String>,
    pub online_published_at: Option<String>,
    pub issue_published_at: Option<String>,
    pub license_url: String,
    #[serde(default)]
    pub publication_updates: Vec<PublicationUpdate>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct CollectionCoverage {
    pub period_start: String,
    pub period_end: String,
    pub cutoff: String,
    pub included_article_types: Vec<String>,
    pub discovered: usize,
    pub admitted: usize,
    pub excluded: usize,
    pub unresolved: usize,
    pub duplicates: usize,
    pub completeness: String,
    pub identity_basis: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct PublicationUpdate {
    pub doi: String,
    pub update_type: String,
    pub published_at: Option<String>,
}

impl JournalIdentity {
    pub fn validate(&self) -> Result<(), String> {
        if self.title.trim().is_empty()
            || self.publisher.trim().is_empty()
            || self
                .issns
                .iter()
                .any(|s| s.len() != 9 || s.as_bytes()[4] != b'-')
        {
            return Err("invalid journal identity".into());
        }
        Ok(())
    }
}
impl JournalArticleMetadata {
    pub fn validate(&self) -> Result<(), String> {
        self.identity.validate()?;
        if self.article_type.trim().is_empty()
            || !(self
                .license_url
                .starts_with("https://creativecommons.org/licenses/by/")
                || self.license_url == "https://creativecommons.org/publicdomain/zero/1.0/")
        {
            return Err("journal record requires a native article type and reuse license".into());
        }
        Ok(())
    }
}
impl CollectionCoverage {
    pub fn validate(&self, year: u16, count: usize, state: &str) -> Result<(), String> {
        if self.period_start != format!("{year}-01-01")
            || self.identity_basis.trim().is_empty()
            || self.period_end < self.period_start
            || self.period_end > self.cutoff[..self.cutoff.len().min(10)].to_string()
            || self.cutoff.len() != 20
            || !self.cutoff.ends_with('Z')
            || self.included_article_types.is_empty()
            || self.admitted != count
            || self.discovered != self.admitted + self.excluded + self.unresolved
            || ![
                "snapshot_complete",
                "snapshot_partial",
                "historical_complete",
            ]
            .contains(&self.completeness.as_str())
            || (self.completeness == "snapshot_partial") != (self.unresolved > 0)
            || (state == "published" && self.unresolved > 0)
        {
            return Err("invalid journal collection coverage".into());
        }
        Ok(())
    }
}
