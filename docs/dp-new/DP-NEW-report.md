# DP-NEW 自检报告

交付状态：**PARTIAL / 本地候选，尚未发布**。不是生产完成声明。

## 1. Implementation Summary — 实现总结

已在实际应用及元数据仓库实现：同一校验 Manifest 中的 OECD FORD 分类定义、每来源多标签引用、Rust 解码/校验/公开投影、生产 FFI 序列化、Swift DTO、单层学科目录、共享来源/年份选择、稳定目录展开偏好、不可用选择提示和显式取消选择。没有新增下载器、来源数据库、排名规则、Agent runtime、期刊 runtime 或 TypeScript 前端。

候选 Manifest `0.15`，schema `1`，25 来源、71 届次、66 数据包（57 published、9 带包 partial；另有 1 个 partial 无包）。首批新增 5 来源、464 条记录。ICML 2026、IJCAI 2026、ICCV 2025 完成实际更新。

执行身份：

- 应用：`/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper`，分支 `codex/dp-new-candidate`；HEAD `e0e329455aab5056f9dd2817de33ac9fbf6ed8f7`；基线 tree `1b83fa97e06590520f9ab228b143c9f6e165c32f`。
- 元数据：`/Users/junesum/Documents/AtomPaper-worktrees/dp-new-cloud-candidate`，分支 `codex/dp-new-candidate`；HEAD `2292fa911b22cda7cf9ecd3cb6608784b1a3717e`；tree `720e83047688ce0e874715dd4a7170c6a8285cb2`。
- 初始应用 checkout 在 AP-CR 分支，18 个已修改文件及 `.claude/`、两个 AP-CR 文档目录视为用户所有，未修改或纳入候选。最初隔离副本从 `7dc9a5244` 建立，发现 AP-CR 单次提交引入 KFR 调用参数不兼容后，用其前一个已提交 Daily 合并点 `e0e329455` 建立最终候选并仅应用本任务补丁；没有 merge/rebase/cherry-pick。
- 最初 Cloud clone 的 main `9a2c7f8` 是旧 `0.12`；读取远端 main 后确认 `2292fa9` 才是当前 Cloud 基线，包含与 live origin 一致的 `0.14`。最终候选以此建立，App-update、appcast、签名及 Translation Engine 资产保持原样。
- 权威运行源仍为 `https://cloud.apaper.ai`；实际读取的 `0.14` SHA 是 `a92d71605ab41fa9900c4f81f0c6b5dec38b3ec0ad419c70368ce4a125f624be`，20 来源、66 届次、59 包。最终 Cloud 候选是维护源，应用内 `apaper-cloud` 是经逐文件比较的开发副本。
- 任务自有构建缓存在两次隔离尝试间复用；没有复用其他任务的可写资格 profile。实际未提交修改的源码指纹见 [source-identity.json](source-identity.json)。

当前实现已落地；元数据候选通过实际校验；Debug 原生 App 构建及隔离启动通过；原生目录/交互验收被账户导航及捕捉环境阻塞；Owner 尚未接受。

## 2. Files Changed — 文件变更

Modified：discovery `model.rs` / `sources/conference.rs` / `lib.rs`、CoreKit `DailyPaper.swift` / MockDiscoveryService / 实际 DTO 测试、DailyResearchHomeViewModel / DailyPaperInspectorPanel / 本地化文件 / 实际 App 测试、两个构建脚本及现有资格启动身份分支。Core/FFI 端点本身无需重写，原有返回类型直接传递新增字段，实际桥接测试确认字段保留。

Created：共享结构的 `discipline.rs`（应用 discovery 与独立 Cloud 工具副本）、7 个新 extraction Skills（5 首批、ICML、IJCAI），仓库化的 ICCV/AAMAS Skills、PMLR/CVF/IJCAI 获取脚本与官方 fixtures、发布负向测试及本报告/审计/记录差异文件。Modified：两个 metadata 工具、版本脚本、管理 Skill、双语 README 与网站会议部分。Deleted：无。

改变的包（pack_version 均为 `0.15`；其余既有包字节及版本未改）：

| 届次 | 记录数 | 压缩字节 | SHA-256 |
| --- | ---: | ---: | --- |
| icml:2026 | 6552 | 2910598 | `8a12d71721aa5b8255a8a93d6d24dbb17f48fb92a5d6cc563f80101c3f44dad3` |
| ijcai:2026 | 972 | 451087 | `562518753fbd50e573380b118fc5e4a2f6be14e25d6c3c730a7423a06976670d` |
| iccv:2025 | 2701 | 1271630 | `3d1d9b988d2dd66721dd893713477f98fe96c6853cb5f1536efb2dc4cc005f01` |
| midl:2026 | 221 | 122624 | `6525d847e455bc44514cba982940842c2ae6f3528c70106780761affb1b1e987` |
| mlhc:2026 | 74 | 48918 | `e006e27b6dcc76548edbec88ec02a108e31eddbc922eb3615c1adc389c07796a` |
| chil:2026 | 40 | 23373 | `0fd9bbc6719bf9bfc37b2dcfafad854ce61f0ebc6de9e63d8fa625ce55260e09` |
| mlcb:2025 | 23 | 13931 | `ca2c06862238be665848f1bacfa77812484bb6cf460629c32dfc19cbf9debd8c` |
| l4dc:2026 | 106 | 50403 | `def4a53717b877a655b9895e89cbf4775ab6c35a9270c439a36e40f08e659998` |

记录对账：[record-diffs.json](record-diffs.json)。ICML 原先仅声明 6,341、没有包，本次实际新增 6,552 记录；IJCAI 原 announced/0，本次 972；ICCV 从 949 到 2,701，新增 1,752、移除 0，原 949 条修正 published_at/updated_at 为 CVF 实际仅提供的年份精度，未编造月日。首批 MIDL 221、MLHC 74、CHIL 40、MLCB 23、L4DC 106，均真实生成 JSONL 与 zstd 包。

## 3. Architecture Verification — 架构验证

分类代码/英文来自 OECD Frascati Manual 2015 表 2.2；中文是 aPaper 翻译，会议映射是 aPaper 根据官方 scope 的审核，不声称 OECD 官方分类会议。详见 [discipline-mapping.md](discipline-mapping.md)。同一个 SHA 覆盖 definitions 与 references，没有独立 taxonomy 刷新文件。

目录按 display_order；目录内来源按 catalog curated 顺序。未知但有效 ID 使用通用文件夹/徽章。空目录不显示；旧目录无 taxonomy 时进入本地化未分类组。导航只有 discipline → source。source-level discipline、legacy localized_tag、paper categories/source_group 独立。

选择仍为一个 edition-ID Set，统计及请求仍从规范 venues 数组生成，不从重复目录行累加。展开仅写既有 UserDefaults 呈现机制中的稳定 discipline ID，不刷新目录、不下载包、不调用模型。保留 100,000 记录预算、包验证、有限同步/重试、原有去重。可用性来自有效 pack reference；保留有效 partial，IEEE S&P partial/254/pack:null 仍不可选。刷新不删除选择；用户可显式取消已有不可用选择，不自动改选年份。

实际 Rust → Core → FFI → Swift DTO 缓存集成通过，MIDL 在两个组引用同一来源，MIDL/ICML 从真实包检索元数据。候选未部署，在线候选版本刷新不能当作已验证；资格使用既有 APAPER_CLOUD_ORIGIN override 和已校验 cache fixture，没有关闭 HTTPS 或校验。

## 4. Validation Evidence — 验证证据

| AC | 结果 | 证据与边界 |
| --- | --- | --- |
| AC-01 | PASS | 25 来源 refs、6 定义，官方分类/翻译/映射出处可追踪 |
| AC-02 | PASS | 实际 CoreKit 目标 A/C/D、B/D/E；未来 ID；1,000 来源及 50 组 |
| AC-03 | 实现 PASS；原生未测 | inspector 只有目录后直接来源；App 已编译，未到工作区 |
| AC-04 | 确定性 PASS | 实际 App 目标共享选择、全局计数、100 次切换、重启偏好、刷新不可用、显式取消 |
| AC-05 | PASS（缓存路径） | 实际生产 FFI/Swift DTO，真实 catalog/pack；下载后的在线候选刷新未测 |
| AC-06 | PARTIAL | Legacy、非法更新、last-good/offline/pack 行为目标测试；旧 Rust/Swift decoder 接受候选；原生刷新与 UI 重启未测 |
| AC-07 | PARTIAL | 全部 20 来源有检查记录、3 项实际更新；保留 scope/获取阻塞 |
| AC-08 | PASS（摄取） | 5/5 首批实际包、fixtures、Skills、精确 publisher ID 集合；原生选择见 AC-11 |
| AC-09 | PASS | 全 66 包 counts/bytes/SHA/IDs/title/provenance 校验；负向发布测试 |
| AC-10 | BLOCKED | 构建/隔离启动通过；guest account route 未进入 inspector，随后 ScreenCaptureKit -3811 |
| AC-11 | PARTIAL / native BLOCKED | 实际 FFI 获取新 MIDL/更新 ICML；PDF header 样本通过；未在 App 打开 PDF、验证目录/窗口/Reduce Motion |
| AC-12 | PASS | 无 merge/push/deploy/formal replacement/生产数据操作/Agent 改动 |

命令与实际结果（重复重试不累计为新的测试数）：

| cwd / 命令 | exit | 实际计数/结果 |
| --- | ---: | --- |
| Cloud candidate / `cargo test --locked` | 0 | 12 pass |
| Cloud candidate / `python3 -m unittest discover -s tests -v` | 0 | 8 pass（含 5 venue subcases、8 个非法 release subcases） |
| Cloud candidate / `python3 skills/manage-apaper-cloud-metadata/scripts/update_version.py public` 后 `cargo run --locked -- validate-site public` | 0 | 25 venues / 71 editions / 66 packs |
| App candidate / discovery `--lib sources::conference::tests` | 0 | 21 pass / 3 ignored |
| App candidate / discovery 全 `--lib` | 101 | 175 pass / 12 fail / 10 ignored；原基线 171 pass / 同样 12 fail / 10 ignored |
| CoreKit actual target / scoped `swift test` | 0 | 5 pass；真实桥接/cache/pack，不是 Swift-only catalog |
| 原始 Rust decoder 补充兼容测试 | 0 | 1 pass |
| 原始 Swift DTO 源码补充兼容检查 | 0 | 25 来源接受；不替代实际 CoreKit 目标 |
| App UnitTest 标准 scoped 命令 | 65 | 0 executed：既有 PaperMentorPresentationTests.projectSearch 编译不匹配 |
| App UnitTest scoped build（只排除两个非本任务测试文件） | 0 | 1 executed / 1 pass；排除 PaperMentorPresentationTests.swift 及依赖其共享 fixture 的 KfrKnowledgeStewardViewTests.swift；未修改这些文件，不能称整个 App test suite PASS |
| `build-macos-apps.sh Debug arm64 dp-new-native-qualification` | 0 | 原生候选及资源/codesign 校验通过 |
| 早期 Release qualification 尝试 | 65 | 既有 Agent RuntimeHostEntry cfg 缺字段；未修改 Agent 模块 |
| Skill Creator quick_validate | 0 | 10 Skills；PyYAML 仅安装于任务临时 venv |
| `git diff --check` / build scripts `bash -n` / Swift source parse | 0 | 范围与语法检查 |

PDF 是确定性样本 `%PDF-` header 验证，不是全部论文 PDF 的验收：MIDL 3/221、MLHC 1/74、CHIL 1/40、MLCB 1/23、L4DC 6/106、ICML 66/6,552、ICCV 28/2,701；IJCAI 20 个稳定样本及 26/26 个 publisher-group 样本（含重复交集，不能相加当作独立覆盖数）。初次 CDN 403/404 后重新检查通过，记录了重试，不当作永久可用保证。PDF 字节未进仓库。

Skill 执行：新 Skill 验证后重新完整运行 PMLR `fetch → import-json → pack`，6 个输出与候选包 SHA 完全相同，详见 [skill-workflows.json](skill-workflows.json)；ICCV all-days index → 4-worker detail fetch → normalize/pack → sample，IJCAI full contents → native subject/track → normalize/pack → sample。官方 fixtures 与真实 validator 负向输入测试都在实际仓库目标。

原生身份详见 [native-identity.json](native-identity.json)：bundle `com.atompaper.APaperDPNewQualification`，精确路径 `/Users/junesum/.codex/worktrees/dp-new/AtomPaper/.build/macos/Debug-dp-new-native-qualification/aPaper-arm64.app`，最终 executable SHA `8b52df0d02811fcf1f0d5d3541db92379089648d9ec791d5c84b7af2ced3fa9b`，实际启动 witness PID `89210`，App/Core root `/var/folders/wl/g0m40l115jg74r9qmy662zr80000gn/T/apaper-dp-new-7y4zcgr_/AppData`。通过 full app path 定位，没有基于 display name 或盲坐标操作。只完成中文/权限稍后/guest/Zotero 不迁移的候选 onboarding；没有输入凭证或同意协议，未读取/迁移生产研究数据。最终屏幕流失败时停止 UI 动作，不报告目录视觉/交互 PASS。

审计逐来源表（完整原状态列表、检查 UTC 和来源见 [audit.json](audit.json)）：

| 来源 / 届次 | 以前状态/数量 | 官方检查 / UTC | 发现与操作 | 结果/阻塞 |
| --- | --- | --- | --- | --- |
| neurips | neurips:2026 announced/0 | [官方源](https://proceedings.neurips.cc/paper_files/paper/2025/vol38-main-conference) / 2026-10-14T10:38:30Z | verified no change: exact latest proceedings index identities match the declared pack scope | unchanged |
| icml | icml:2026 cataloged/6341 | [官方源](https://proceedings.mlr.press/v306/) / 2026-10-14T10:04:09Z | new edition available: final PMLR v306; ingested 6,552 records; prior declared count 6,341 was not a pack | published / 6552 |
| iclr | iclr:2026 partial/5359 | [官方源](https://openreview.net/group?id=ICLR.cc/2026/Conference) / 2026-10-14T10:04:09Z | local ingestion incomplete: OpenReview group accessible, accepted final identity and PDF reconciliation not completed; retain temporary provenance and valid partial packs | partial / unchanged |
| cvpr | cvpr:2026 published/4068 | [官方源](https://openaccess.thecvf.com/CVPR2026?day=all) / 2026-10-14T10:04:09Z | local ingestion incomplete: official index/pack identity discrepancy; no records removed without scope evidence | 保留原数据；详见 finding |
| acl | acl:2026 published/4806 | [官方源](https://aclanthology.org/events/acl-2026/) / 2026-10-14T10:04:10Z | access/verification blocked: event index covers Main volumes but not the declared Findings collection; seven front-matter IDs and two other IDs need scope reconciliation; official XML acquisition returned HTTP 404. No deletions or guessed records applied. | 保留原数据；详见 finding |
| aaai | aaai:2026 published/4149 | [官方源](https://ojs.aaai.org/index.php/AAAI/issue/archive) / 2026-10-14T10:04:10Z | local ingestion incomplete: retrieved page does not establish an exact final proceedings identity set | 保留原数据；详见 finding |
| ijcai | ijcai:2026 announced/0 | [官方源](https://www.ijcai.org/proceedings/2026/) / 2026-10-14T10:04:11Z | new edition available: final publisher proceedings; ingested all 972 indexed contributions | published / 972 |
| emnlp | emnlp:2026 announced/0 | [官方源](https://aclanthology.org/events/emnlp-2026/) / 2026-10-14T10:04:11Z | access/verification blocked | 保留原数据；详见 finding |
| iccv | iccv:2025 published/949 | [官方源](https://openaccess.thecvf.com/ICCV2025?day=all) / 2026-10-14T10:04:12Z | existing pack updated: all-days official index 2,701; 1,752 added, no removals; 949 date-precision corrections | published / 2701 |
| eccv | eccv:2026 announced/0 | [官方源](https://www.ecva.net/papers.php) / 2026-10-14T10:04:13Z | verified no change: ECCV 2024 exact index identities match 2387 records; upstream 2026 not present in ECVA open-access edition index | 保留原数据；详见 finding |
| aistats | aistats:2026 published/588 | [官方源](https://proceedings.mlr.press/v300/) / 2026-10-14T10:04:13Z | verified no change: latest published index record identities match the pack (bounded index check) | 保留原数据；详见 finding |
| colt | colt:2026 published/196 | [官方源](https://proceedings.mlr.press/v336/) / 2026-10-14T10:04:46Z | verified no change: 197 index entries minus publisher preface hanneke26a = 196 research papers; exact identities match | published / 196 |
| aamas | aamas:2026 partial/639 | [官方源](https://ifaamas.org/Proceedings/aamas2026/forms/contents.htm) / 2026-10-14T10:04:14Z | verified no change in declared partial scope: 641 publisher PDF IDs; pack retains 639, excludes CSLO7280/XWPK8237 with unresolved abstracts | partial / 639 |
| corl | corl:2025 published/263 | [官方源](https://proceedings.mlr.press/v305/) / 2026-10-14T10:04:15Z | verified no change: latest published index record identities match the pack (bounded index check) | 保留原数据；详见 finding |
| rss | rss:2026 published/210 | [官方源](https://roboticsproceedings.org/rss22/) / 2026-10-14T10:04:15Z | verified no change: latest published index record identities match the pack (bounded index check) | 保留原数据；详见 finding |
| osdi | osdi:2026 published/136 | [官方源](https://www.usenix.org/conference/osdi26/technical-sessions) / 2026-10-14T10:04:16Z | verified no change in collection identities: 137 presentation links minus keynote = 136 papers; errata links exist, PDF content not exhaustively rechecked | published / 136 |
| sosp | sosp:2025 partial/65 | [官方源](https://dl.acm.org/doi/proceedings/10.1145/3731569) / 2026-10-14T10:04:16Z | access/verification blocked: ACM returned HTTP 403; no publisher replacement completed; preserve temporary provenance and partial packs | partial / unchanged |
| ieee_sp | ieee_sp:2026 partial/254 | [官方源](https://www.ieee-security.org/TC/SP2026/program.html) / 2026-10-14T10:04:16Z | local ingestion incomplete: existing partial count 254 with pack:null remains unavailable; program alone does not establish a verified pack | partial / 254 / unavailable |
| ndss | ndss:2026 published/265 | [官方源](https://www.ndss-symposium.org/ndss2026/accepted-papers/) / 2026-10-14T10:04:17Z | verified no change: latest published index record identities match the pack (bounded index check) | 保留原数据；详见 finding |
| accv | accv:2024 published/269 | [官方源](https://openaccess.thecvf.com/ACCV2024?day=all) / 2026-10-14T10:04:17Z | verified no change: latest published index record identities match the pack (bounded index check) | 保留原数据；详见 finding |

额外候选检查：

| 候选 | 官方入口 | 状态/未完成前提 |
| --- | --- | --- |
| uai | [源](https://proceedings.mlr.press/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| alt | [源](https://proceedings.mlr.press/v313/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| clear | [源](https://proceedings.mlr.press/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| acml | [源](https://proceedings.mlr.press/v304/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| automl | [源](https://proceedings.mlr.press/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| naacl | [源](https://aclanthology.org/events/naacl-2025/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| eacl | [源](https://aclanthology.org/events/eacl-2026/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| usenix_security | [源](https://www.usenix.org/conference/usenixsecurity26/technical-sessions) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| nsdi | [源](https://www.usenix.org/conference/nsdi26/technical-sessions) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| wacv | [源](https://openaccess.thecvf.com/WACV2026?day=all) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |
| miccai | [源](https://papers.miccai.org/miccai-2026/) | official page accessible; bounded review recorded, completeness not established; not admitted: extraction/scope/PDF reconciliation still required |

## 5. Known Risks — 已知风险

- 原生 source selector 尚未观察到，窄布局、多标签、键盘、Reduce Motion、刷新/重启 UI、真实 PDF 打开保持开放，不能由 build/parse 替代。
- 全 discovery 的 12 个失败在未改基线复现；不为 DP-NEW 改排名或 unrelated tests。标准 App tests 的 projectSearch 编译漂移同样未修改；scoped 排除仅用来执行 DP-NEW 自身测试。
- ACL/AAAI/ICLR/IEEE S&P 的完整 publisher collection reconciliation、CVPR 更小 index 与既有包的 scope 差异、SOSP ACM 403、EMNLP 404 等仍开放。没有因失败或更小 crawler 结果删记录。
- PDF 样本和 CDN 重试不等于全覆盖；ICLR/SOSP temporary provenance 保留；新增来源没有变成新 App runtime 上游依赖。
- 元数据仍未上线；旧 cache fixture 的通过不代表在线 candidate release 和 Owner 体验通过。

## 6. Next Recommended Step — 下一步

在这个已构建的隔离候选中完成正常 guest/account 进入工作区（不新建账号基础设施、不迁移生产资料），然后用同一 root 复验 MIDL 两目录联动、ICML 年份、重启偏好、窄布局/语言/Reduce Motion 和一次正常公开 PDF 打开。剩余 publisher scope 项按 audit 的具体缺口补齐；未完成前不发布。

将来获得发布授权后的顺序：先完成原生/Owner 资格和签名发布资格；核对 live 仍为本候选基线版本；按既有原子静态发布方式发布 conference prefix 的完整一致集合，保留 unrelated appcast/Translation Engine 资产；再执行 live verifier。不要先覆盖固定路径的 ICCV 新包而让旧 manifest 仍引用旧 SHA。未授权时不执行任何这些步骤。

```
python3 skills/manage-apaper-cloud-metadata/scripts/verify_published_release.py --public public --origin https://cloud.apaper.ai --pack icml:2026 --pack ijcai:2026 --pack iccv:2025 --pack midl:2026 --pack mlhc:2026 --pack chil:2026 --pack mlcb:2025 --pack l4dc:2026
```

回滚：保留完整 preceding `0.14` conference prefix（manifest/version/对应旧包），通过原有原子部署恢复这一 prefix，保留其他发布流当时的资产，然后验证旧 version SHA 及受影响包；不重置或迁移用户研究数据。客户端按既有 version-change/pack-checksum 恢复。若 live 已前进，不重用 `0.15`，先协调新基线/版本。

Implementation: PARTIAL（实现已落地，原生验收开放）
Existing-source refresh: PARTIAL（3 项实际更新，其余具体 gap 已列出）
New-source ingestion: PASS（5/5，464 记录，真实包与 Skills）
Automated verification: PARTIAL（本任务目标通过；全套已有失败/限定排除）
Native verification: BLOCKED（构建/隔离启动 PASS；selector/PDF 尚未观察）
Owner acceptance: PENDING
Local commit(s): NONE
Merged: NO
Pushed: NO
Production metadata deployed: NO
Formal App replaced: NO
Production data migrated: NO
Released: NO

最终同步核验：两仓库 Manifest/version 字节相同；66 个包逐一比较 SHA/bytes 完全相同；工具 main.rs/discipline.rs 相同。最终候选 Manifest SHA：`dab9dbdb1e042e74879618aeb5a3208147b4d0da28f0612f24e8c1d984ab4974`。
