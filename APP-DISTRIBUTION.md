# aPaper App distribution contract

This public repository is the current distribution repository, not the App source repository.
App updates and conference synchronization use independent versioned interfaces.
Never resolve App updates using `/releases/latest` or global Release ordering.

## Current manual distribution contract (Release-01)

- Product installer: `YociLam/aPaper`, numeric repository ID `1428580757`, independent public documentation history. New `aPaper.dmg` assets use immutable `v<version>-b<build>` tags in that repository.
- Update archive: this repository, ID 1305956053, uses immutable version/build tags for verified public assets. The five metadata-only demo Releases for 0.1.1–0.1.5 are retired; Release cleanup does not establish whether historical Git tags remain. Preserve conference/journal packs and translation compatibility routes.
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

## Bundled translation resources

The translator and its runtime environment ship inside the signed App archive and change only with an App release. No separate Cloud binary or download is published. The existing public/v1/app/macos/arm64/components/translation.json remains a compatibility-only status record for the release publisher; it is updated from a verified App bundle, not advertised as a separate release on the homepage or in the README.

Every new App release updates its version, build, time, and verified download links together in the appcast, release record, homepage, and both READMEs. The current demo stable item has been withdrawn because its archive URL no longer resolves. A new offer requires a new verified archive and normal release approval.
