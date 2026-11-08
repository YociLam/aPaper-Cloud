<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a></p>
</div>

# aPaper Cloud

aPaper Cloud hosts public update metadata and research resources used by the aPaper App. The App source and private user data are maintained separately.

[Website](https://cloud.apaper.ai) · [Contact](mailto:contact@apaper.ai)

## Public resources

| Resource | Public path | Purpose |
| --- | --- | --- |
| macOS App updates | [Stable appcast](https://cloud.apaper.ai/v1/app/macos/arm64/stable/appcast.xml) | Offers an App update only after its archive has been published and verified. |
| Literature catalog | [Version](https://cloud.apaper.ai/v1/conferences/version.json) · [Manifest](https://cloud.apaper.ai/v1/conferences/manifest.json) | Lists available conference and journal metadata packs with checksums. |
| Dogzee model groups | [Policy JSON](https://cloud.apaper.ai/v1/config/dogzee-group-policy.v1.json) | Public group names, model reasoning options, and agent defaults. |

App installers are published in [aPaper Releases](https://github.com/YociLam/aPaper/releases). Verified update archives, when available, are published in this repository's [Releases](https://github.com/YociLam/aPaper-Cloud/releases). The translator and its runtime environment are bundled inside each App archive and update with the App; they are not separate Cloud downloads.

Current stable: no verified update is currently offered.

## Literature packs

| Venue | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| NeurIPS | — | 3,540 | 4,493 | 5,823 | announced |
| ICML | — | 1,828 | 2,610 | 3,330 | 6,552 |
| ICLR | — | 435 (partial) | 2,261 (partial) | 3,708 (partial) | 5,359 (partial) |
| CVPR | — | 2,352 | 2,710 | 2,871 | 4,068 |
| ACL | — | 2,150 | 1,982 | 3,353 | 4,806 (partial) |
| AAAI | — | 1,578 | 2,331 | 3,028 | 4,149 |
| IJCAI | — | 850 | 1,047 | 1,279 | 972 |
| EMNLP | — | 2,241 | 2,388 | 3,488 | announced |
| ICCV | — | 2,156 | — | 2,701 | — |
| ECCV | 1,645 | — | 2,387 | — | announced |
| AISTATS | — | — | 547 | 583 | 588 |
| COLT | — | — | — | 181 | 196 |
| AAMAS | — | — | — | 479 | 640 (partial) |
| CoRL | — | — | 264 (partial) | 263 | — |
| RSS | — | — | 134 | 163 | 210 |
| OSDI | — | 55 | 53 | 53 | 136 |
| SOSP | — | 9 (partial) | 43 (partial) | 65 (partial) | — |
| IEEE S&P | — | cataloged | 261 | 65 | 254 (partial / no pack) |
| NDSS | — | 94 | 140 | 211 | 265 |
| ACCV | 277 | — | 269 | — | — |
| MIDL | — | — | — | — | 221 |
| MLHC | — | — | — | — | 74 |
| CHIL | — | — | — | — | 40 |
| MLCB | — | — | — | 23 | — |
| L4DC | — | — | — | — | 106 |

Unqualified counts indicate validated metadata packs. **Partial** means coverage
is incomplete; only editions with a valid pack are selectable; **cataloged** means an edition is recorded but its pack is not yet
published; **announced** means final proceedings are pending. The live manifest is authoritative.
The table uses the catalog publication time; per-edition update times are not currently tracked.

The App uses versioned metadata and checksums to detect catalog changes and verify downloaded packs. The model policy contains public configuration only; account credentials and API keys are never stored here.

For publication and channel details, see the [App distribution contract](APP-DISTRIBUTION.md). To validate the public catalog locally, run the repository's catalog validator and tests.
