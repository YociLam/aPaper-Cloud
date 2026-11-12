# aPaper App distribution

This repository serves public update metadata, update archives, and research resources. Product information, installation guides, feedback, and DMG installers live in [aPaper](https://github.com/YociLam/aPaper).

## Current status

The first public App release, **0.1.0**, is in preparation. No verified App update is currently offered. Stable and qualification feeds contain no release items. Historical test metadata does not establish current download availability.

App versions and literature catalog versions are independent. Catalog version 0.16 is not an App version. Never use this repository's global latest Release to discover an App update.

## Package locations

| Artifact | Repository | Tag / filename |
| --- | --- | --- |
| macOS installer | `YociLam/aPaper` (ID `1428580757`) | `v<version>-b<build>` / `aPaper.dmg` |
| macOS full update | `YociLam/aPaper-Cloud` (ID `1305956053`) | `apaper-macos-v<version>-b<build>` / `aPaper-<version>-b<build>-macos-arm64.zip` |

Display versions use `MAJOR.MINOR.PATCH`. Internal build numbers increase for every distributed build, including rebuilds and a change in display version. Public artifacts and tags are immutable. New bytes require a new build and tag.

The installer and full update archive are packaged from the same sealed App. Recursive file hashes, symlinks, permissions, and code seals are verified after extraction. Signing, notarization, and supported update behavior are stated for each actual release; a package's presence does not establish Apple notarization or installation qualification.

GitHub automatically offers ZIP/tar snapshots for tags. These contain the public repository's files, not a macOS installer. The App source remains private.

## Update interfaces

| Channel | Fixed appcast |
| --- | --- |
| stable | `https://cloud.apaper.ai/v1/app/macos/arm64/stable/appcast.xml` |
| qualification | `https://cloud.apaper.ai/v1/app/macos/arm64/qualification/appcast.xml` |

Each channel also exposes `release.json` beside its appcast. An empty feed offers no update. A withdrawn status record describes availability; it does not identify an installable version. A missing or invalid response is not evidence that an installed client is current.

The supported target is Apple silicon (arm64), macOS 14.6 or later. There is no published Intel Mac, Windows, or Linux update channel. Qualification is isolated testing, with its own bundle identity, trust key, and synthetic data; its results do not establish general macOS distribution readiness.

For installer-capable releases, the Sparkle enclosure binds the immutable HTTPS archive URL, byte length, Ed25519 signature, version, build, minimum OS, and reviewed multilingual notes. The App embeds only the public verification key. Private signing keys and signing tools never belong in the distributed App or this repository. Legacy information-only releases have no executable enclosure and require manual installation.

Update checks, consent, download, installation, and relaunch are distinct capabilities. Supported clients require user consent before installation. A completed installation alone does not establish account-session continuity.

## Publication and verification

1. Freeze and review the intended source, release notes, package contents, and distribution configuration in the canonical private release record.
2. Verify the DMG and ZIP, code seals, archive signature, sizes, and hashes. Obtain approval for the exact final artifacts and public projections.
3. Stage and publish immutable versioned assets in the correct repositories. App Releases are explicitly not repository-global latest.
4. Download the complete public assets anonymously over HTTPS and verify their actual bytes and signatures.
5. Publish matching channel XML/JSON and Cloud homepage information, then verify the live responses and download links.
6. Update the product website only after asset and channel verification. Qualify native installation, relaunch, and account continuity separately.

Resume an interrupted publication from the same canonical record and reconcile actual repository, release, asset, and deployment identities. Never overwrite a published asset or reuse a historical tag. Preserve the previous channel bytes and website deployment for a scoped recovery. Withdrawing an offer does not downgrade installed Apps or restore user data.

Public release metadata contains product and platform facts, reviewed notes, public URLs, byte counts, hashes, and signature information. It must not contain private source identities, local paths, approval records, credentials, or private signing material. Third-party notices and required runtime material accompany the App.

## Bundled resources and research data

The translator and its runtime ship inside the App and change through App releases. `public/v1/app/macos/arm64/components/translation.json` remains a compatibility status record, not a separate downloadable engine release.

Conference and journal packs, catalog manifests, model policy, and their maintenance tools have independent lifecycles. An App release or repository cleanup must preserve these resources and their checksums.
