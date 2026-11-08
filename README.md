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

The App uses versioned metadata and checksums to detect catalog changes and verify downloaded packs. The model policy contains public configuration only; account credentials and API keys are never stored here.

For publication and channel details, see the [App distribution contract](APP-DISTRIBUTION.md). To validate the public catalog locally, run the repository's catalog validator and tests.
