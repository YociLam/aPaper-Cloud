# aPaper App distribution contract

This public repository is the current distribution repository, not the App source repository.
App distribution, conference synchronization and historical Translation Engine assets are separate
products. Never resolve App updates using `/releases/latest` or global Release ordering.

## macOS arm64 channels

| Channel | Sparkle appcast | Immutable full ZIP release tag |
| --- | --- | --- |
| qualification | `https://cloud.apaper.ai/v1/app/macos/arm64/qualification/appcast.xml` | `apaper-update-qualification-<unique-id>` (prerelease, `make_latest=false`) |
| beta | `https://cloud.apaper.ai/v1/app/macos/arm64/beta/appcast.xml` | `apaper-macos-beta-<unique-id>` (prerelease) |
| stable | `https://cloud.apaper.ai/v1/app/macos/arm64/stable/appcast.xml` | `apaper-macos-v<version>` (separate production approval) |

These are reserved interfaces, not claims that any feed is published. No x86_64 App channel exists
until that architecture has qualified artifacts. Do not change the App's minimum macOS version.

Qualification uses `com.atompaper.APaperUpdateQualification`, its own EdDSA key, isolated install
container and synthetic AppData. A and B must compile the exact HTTPS feed and public key into
SUFeedURL/SUPublicEDKey; B has a higher CFBundleVersion. No private keys enter Git, Pages or bundles.
Apple Development qualification is not Developer ID/notarization readiness.

Each feed pins a single Sparkle full-package item: actual build, display version, minimum system
version, immutable HTTPS GitHub Release archive URL, exact byte length and Sparkle EdDSA signature.
Use namespaced aPaper significance/translated notes from the release contract. The URL and bytes
are bound to consent. No archive belongs in Git history or Pages. Never rewrite distributed bytes;
use a higher build and new tag. Missing/invalid feeds must not mean “latest”.

## Publication order

1. Freeze source commit/tree and build A/B. Review the exact signed bundle, recursive archives,
   licenses/source-distribution obligations, symbols, credentials, URLs and identifying material.
2. Verify codesign/entitlements, Sparkle signature, bytes and SHA-256 locally. Obtain any required
   narrowly scoped disclosure approval before a public binary upload.
3. Publish B to its unique qualification prerelease, explicitly not latest. Anonymous HEAD/GET
   must follow HTTPS GitHub asset redirects and reproduce the signed bytes and SHA-256.
4. Only then commit the small qualification appcast under `public/v1/app/macos/arm64/qualification/`.
   A main change may deploy the entire public tree automatically. Preserve conference paths and
   verify actual live XML, cache headers and checksums after deployment; HTTP 200 alone is invalid
   evidence because the current host uses an HTML fallback for unknown paths.
5. Stop the loopback server. Run native discovery/no-preconsent-download and one-confirmation
   A→B installation/relaunch with synthetic data receipts. Record discovery, archive delivery,
   native relaunch and production readiness separately.

The source repository supplies `scripts/preflight-macos-appcast.py` for repeatable anonymous remote
validation. Run Sparkle `sign_update --verify` on its downloaded output too; signature metadata alone
is not cryptographic verification. Record commit/tree, tag/release/asset IDs, feed SHA, archive SHA
and bytes, UTC publication time, response/cache headers and sanitized redirect chain.

The static, versioned platform/architecture/channel boundary is independent of the current native
client implementation. A later approved client can use a separately specified artifact format in
this namespace; this contract does not implement Tauri, Windows or a dynamic updater backend.

Historical `translation-engine-v0.1` assets and `public/v1/translation/**` remain intact. See
[Translation Engine retention](translation-engine/README.md#retention-policy-update-01-q2).
