# aPaper App distribution contract

This public repository is the current distribution repository, not the App source repository.
App distribution, conference synchronization and historical Translation Engine assets are separate
products. Never resolve App updates using `/releases/latest` or global Release ordering.

## Current manual distribution contract (Release-01)

- Product installer: `YociLam/aPaper`, numeric repository ID `1428580757`, independent public documentation history. New `aPaper.dmg` assets use immutable `v<version>-b<build>` tags in that repository.
- Update archive: this repository, ID `1305956053`, immutable `apaper-macos-v<version>-b<build>` tags. Keep all historical releases, conference/journal packs and translation routes.
- Source repository is private; it is never a public tag target or export source. Public release JSON contains only product/platform/version, capability, public URLs, byte counts, hashes and reviewed notes.
- One sealed App is packaged into DMG and ZIP. Recursive file hashes, symlinks, modes and valid code seals must match after unpacking. Full ZIP does not imply a delta or installation eligibility.
- Apple paid membership/notarization is deferred for explicitly labeled ad-hoc manual installation. The existing Developer ID/notarized production lane below remains intact.
- The accepted formal client checks the existing **stable** URL below. Without production Ed25519 custody, serve an information-only item with `sparkle:version`, display version, minimum macOS, arm64/stable markers and the product website link, **without any executable enclosure**. The client opens `https://apaper.ai` only after user consent. Automatic checking remains separate from installation; automatic installation is unavailable.
- The downloadable Cloud ZIP is retained for a future separately qualified installer path. Do not activate an unsigned archive, reuse qualification trust roots, or use repository-global latest.
- Prepare and validate → upload reconciled drafts → exact combined approval → publish immutable assets → anonymous full-byte hashes → promote stable XML/JSON → verify live MIME/content → promote website last. Draft access is authenticated, not anonymous publication.
- Resume the same canonical release record, reconciling repository/release/asset IDs and hashes. A different artifact requires a new version/build/tag; no clobber, moved tag, forced ref or historical deletion.
- Preserve prior website deployment and channel bytes. Withdrawing an offer does not downgrade installed Apps or restore account/research data. Prefer a higher-build forward correction.

These rules establish the route; they do not announce a public binary, activate stable metadata or replace the live website. The canonical private `apaper-release` Skill owns preparation, approval and execution. Third-party notices and necessary runtime material remain in the App; no product open-source license is implied.

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

## Website and README resource status

`public/v1/app/macos/arm64/components/translation.json` is a status-only snapshot of verified
App-bundled resources, not a Cloud engine download manifest or a stable App release announcement.
It records translator/environment versions independently, archive revision, exact package/resource
hashes and the UTC commit times when the corresponding packaged source/resource inputs last changed. It has no asset URL.
The homepage's four status fields and both README summaries must match this record. When resources
change, update all three surfaces together from the actual signed bundle; do not replace resource
change times with the website deployment time. Historical `/v1/translation/**` remains unchanged.

The translator archive is regenerated by `scripts/package-translation-engine.sh` from the current
App source. Read its size/hash from the signed bundle's generated `translator-package-manifest.json`,
not the checked-in seed descriptor. For the inspected v0.6 source snapshot the signed translator archive
is 30355 bytes / `3f488425a0697561e0aab1e8b44730acbb8d47c5c93f91c1eb541ed0dbff7e95`.
The component record is read from the generated manifests in the verified bundle. Translator and
engine artifact inputs last changed at 2026-10-21 14:19:11 UTC; website deployment time is separate.

Every App release must update both language READMEs and the website in the same publication
change: product version/build, resource versions, actual update times and download links. The
current user-facing environment package label is `v0.2`; keep the underlying environment v0.1
and archive revision fields separate for compatibility.
