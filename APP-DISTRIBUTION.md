# aPaper App distribution

This repository serves public update metadata, update archives, and research resources. Product information, installation guides, feedback, and DMG installers live in [aPaper](https://github.com/YociLam/aPaper).

## Current status

The first formal App version is **0.1.0**. The installer is published in [aPaper Releases](https://github.com/YociLam/aPaper/releases). No verified App update archive is currently offered through the Appcast feeds.

## Release categories

User-facing release types are **Alpha**, **Beta**, and **Formal**. Use Semantic Versioning prerelease identifiers for test candidates: `MAJOR.MINOR.PATCH-alpha.N` and `MAJOR.MINOR.PATCH-beta.N`. The candidate number starts at `1` for each type and target version and increments for every new published build. For example: `0.2.0-alpha.1` → `0.2.0-alpha.2` → `0.2.0-beta.1` → `0.2.0`. GitHub titles are `aPaper MAJOR.MINOR.PATCH Alpha N`, `aPaper MAJOR.MINOR.PATCH Beta N`, and `aPaper MAJOR.MINOR.PATCH` for Formal; tags append `-b<build>` to the complete release version. Alpha is for early, limited testing while planned functionality may still change. Beta is for broader testing after the planned scope is feature-complete; only release-blocking fixes should be added during Beta. A Beta candidate becomes Formal by publishing the same core version without the prerelease suffix after final checks pass. Build numbers remain in tags and assets, not the user-facing title or release notes.

Keep Apple's bundle version fields numeric: `CFBundleShortVersionString` and `CFBundleVersion` use the core `MAJOR.MINOR.PATCH`; `APaperBuildNumber` carries the monotonically increasing integer build identity. Record the complete prerelease identity (for example, `0.2.0-alpha.1`) separately in release metadata, the GitHub tag, release title, and user-facing release notes. Never put an Alpha/Beta suffix in Apple's bundle version fields. Increment the internal build for every distributed candidate and Formal release. Feed URLs and publisher channel fields are operational configuration; omit them from product README copy and user-facing release notes.

App versions and literature catalog versions are independent. Catalog version 0.16 is not an App version. Never use this repository's global latest Release to discover an App update.

## Package locations

| Artifact | Repository | Tag / filename |
| --- | --- | --- |
| macOS installer | `YociLam/aPaper` (ID `1428580757`) | `v<release-version>-b<build>` / `aPaper.dmg` |
| macOS full update | `YociLam/aPaper-Cloud` (ID `1305956053`) | `apaper-macos-v<release-version>-b<build>` / `aPaper-<release-version>-b<build>-macos-arm64.zip` |

Display versions use `MAJOR.MINOR.PATCH`. Internal build numbers increase for every distributed build, including rebuilds and a change in display version. Public artifacts and tags are immutable. New bytes require a new build and tag.

The installer and full update archive are packaged from the same sealed App. Recursive file hashes, symlinks, permissions, and code seals are verified after extraction. Signing and supported update behavior are stated for each actual release; a package's presence does not establish its signing or installation qualification.

GitHub automatically offers ZIP/tar snapshots for tags. These contain the public repository's files, not a macOS installer. The App source remains private.

## Update interfaces

| Channel | Fixed appcast |
| --- | --- |
| Formal App updates | [Appcast](https://cloud.apaper.ai/v1/app/macos/arm64/stable/appcast.xml) |
| Alpha/Beta test updates | [Appcast](https://cloud.apaper.ai/v1/app/macos/arm64/qualification/appcast.xml) |

Each channel also exposes `release.json` beside its appcast. An empty feed offers no update. A withdrawn status record describes availability; it does not identify an installable version. A missing or invalid response is not evidence that an installed client is current.

The supported target is Apple silicon (arm64), macOS 14.6 or later. There is no published Intel Mac, Windows, or Linux update channel. Alpha/Beta builds use isolated testing, with their own bundle identity, trust key, and synthetic data; their results do not establish formal-release qualification.

For installer-capable releases, the Sparkle enclosure binds the immutable HTTPS archive URL, byte length, Ed25519 signature, version, build, minimum OS, and reviewed multilingual notes. The App embeds only the public verification key. Private signing keys and signing tools never belong in the distributed App or this repository. Legacy information-only releases have no executable enclosure and require manual installation.

Update checks, consent, download, installation, and relaunch are distinct capabilities. Supported clients require user consent before installation. A completed installation alone does not establish account-session continuity.

## Publication and verification

1. Freeze and review the intended source, release notes, package contents, and distribution configuration in the canonical private release record.
2. Verify the DMG and ZIP, code seals, archive signature, sizes, and hashes. Obtain approval for the exact final artifacts and public projections.
3. Stage and publish immutable versioned assets in the correct repositories. Alpha/Beta releases are prereleases; a Formal installer release is marked latest in the installer repository. App update discovery always uses its fixed Appcast, never the Cloud repository's global latest Release.
4. Download the complete public assets anonymously over HTTPS and verify their actual bytes and signatures.
5. Publish matching channel XML/JSON and Cloud homepage information, then verify the live responses and download links.
6. Update the product website only after asset and channel verification. Qualify native installation, relaunch, and account continuity separately.

Resume an interrupted publication from the same canonical record and reconcile actual repository, release, asset, and deployment identities. Never overwrite a published asset or reuse a historical tag. Preserve the previous channel bytes and website deployment for a scoped recovery. Withdrawing an offer does not downgrade installed Apps or restore user data.

Public release metadata contains product and platform facts, reviewed notes, public URLs, byte counts, hashes, and signature information. It must not contain private source identities, local paths, approval records, credentials, or private signing material. Third-party notices and required runtime material accompany the App.

## Bundled resources and research data

The translator and its runtime ship inside the App and change through App releases. `public/v1/app/macos/arm64/components/translation.json` remains a compatibility status record, not a separate downloadable engine release.

Conference and journal packs, catalog manifests, model policy, and their maintenance tools have independent lifecycles. An App release or repository cleanup must preserve these resources and their checksums.
