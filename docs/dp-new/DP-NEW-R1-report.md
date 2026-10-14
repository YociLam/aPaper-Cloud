# DP-NEW-R1 续作报告

结论：**PARTIAL，本地未发布候选**。保留 [初始报告](DP-NEW-report.md) 的历史结果；本报告不把其原生阻塞改写为 PASS。

## 1. Implementation Summary

本轮实际修复三处：生产 conference downloader 先在临时路径取得并校验新包，再原子替换缓存，失败保留原已验证包；Cloud ACL importer 支持当前官方 XML 的 collection/volume/paper 身份结构；AAMAS Skill 增加明确 opt-in 的 PDFKit/Vision 两栏 OCR，仍只接纳前两页明确标记的 ABSTRACT，并要求人工比对。

CVPR、ACL 原审计输入都恰好为 8 MiB 且在正文中截断，原差异有本地获取原因。完整输入已冻结。ACL 实际 importer 原本跳过全部 4,813 项，修复后得到 4,806 条，ID 与现包完全相同，七项在 XML 缺摘要。现包不重打包，状态修正为 partial。AAAI 最终主技术轨 43 分册的 4,149 个 ID 与现包完全一致。AAMAS 恢复 CSLO7280，639 条保留记录内容完全相同，变为 partial/640；XWPK8237 仍无可接纳的标记摘要。

候选仍为未发布的 0.15：25 来源、71 届次、66 包；56 published、11 partial（10 个有包）、3 announced、1 cataloged。首批 MIDL/MLHC/CHIL/MLCB/L4DC 的 464 条及 ICML/IJCAI/ICCV 更新均保留。没有重新摄取通过的数据包，没有扩大来源批次。

真实 TLS 下载器／同步边界测试已通过；默认生产 Agent 从空缓存通过 HTTPS 取得线上 0.14，也通过版本/SHA 校验。线上仍为 0.14，不是候选 0.15 的公网刷新。实际 FFI/Swift 搜索确认六个 ICCV 代表记录（3 retained、3 added）保持身份/来源 URL 和年份字符串 2025。

原生构建只重建一次。最终独立候选、静态 FFI、资源和同一资格根可追踪。访客按钮在鼠标和键盘正常路径均不推进；键盘焦点和截图可用，因此没有将 App 称为 hung。未确定其 bootstrap 根因，也未证明这是 Owner 权限问题。Account 逻辑未改，原生目录／Reader 尚未观察到。

## 2. Files Changed

应用仓库：`/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper`，`codex/dp-new-candidate`。原 base e0e329455aab5056f9dd2817de33ac9fbf6ed8f7；产品局部检查点 ef787282a（明确 partial，不能代表验收）。

Cloud：`/Users/junesum/Documents/AtomPaper-worktrees/dp-new-cloud-candidate`，同名分支。原 base 2292fa911b22cda7cf9ecd3cb6608784b1a3717e；元数据局部检查点 3858a47。后续 Skills、测试、证据随本轮 handoff 检查点保存，完整 commit ID 以最终交接消息和 Git 为准。没有改用 remote main。

R1 Modified：discovery `sources/conference.rs` 包替换逻辑；CoreKit 实际测试；Cloud 与 App 开发副本 `src/main.rs`、AAMAS Skill/脚本、manifest/version、双语 README、AAMAS 2026 包；audit.json 只追加 r1 字段，保留历史 finding。Cloud 自有新增 discipline 文件及修改区格式整理，两副本一致。

R1 Created：`conference_refresh_tests.rs`、`tests/fixtures/catalog_https.py`、AAMAS `extract_pdf_columns.swift`、本报告、source/native identity R1、candidate/audit/record-diffs/skill-workflows R1、`evidence/r1/`。Deleted：无。原 DP-NEW 的所有实现、五个新来源及 Skills 一并保存在任务分支检查点。

相对初始 DP-NEW，本轮只改变 AAMAS 包字节。相对 0.14 共九个改变包，完整 counts/bytes/SHA 见 [候选清单](candidate-r1.json)。本轮 AAMAS：640 records、297321 bytes、SHA `0c3b0368246d76105a9b31d749b4df7d3e19f2d0adf168a8ffa9730ba6df2823`。ACL SHA 不变。差异见 [record-diffs-r1.json](record-diffs-r1.json)。

未纳入 SemanticRetrieval/model.onnx 工作区状态、构建目录 symlink、资格运行数据。Appcast、签名发布、Translation Engine 分发资产的 Cloud diff 为零。没有修改原主工作区。

## 3. Architecture Verification

继续一个 manifest、一个规范 selected-edition Set 和 Rust/Core 同步/发现所有权。单层 discipline→source、远端标签/顺序/成员关系、多标签呈现、100000 记录预算及有界下载队列均保留。展开不会启动发现或模型调用。有效 partial 包仍可选，pack:null 不能新增选择，已有不可用选择仍允许显式取消。

没有账户绕过、伪造同意、认证/profile 拷贝、重复下载器、TLS/校验削弱、Agent/ranking/Reader/TypeScript 改造。TLS fixture 在测试 Agent 中显式信任单个临时 CA，保持主机名和证书验证，不修改机器信任库。生产 HTTPS 测试使用正常 Agent，无自定义 CA。

新包临时文件仍由原 pack ownership guard 保护，只有校验通过才写入规范缓存及 meta。旧 manifest 对同路径新 ICCV bytes 校验失败；取得新 manifest 后恢复。恢复证据在启动同步/下载器边界，不能代替原生重启。持续使用旧会话 catalog 的客户端可能需要下一次正常启动检查，未承诺自动热升级。

## 4. Validation Evidence

### 身份与资格根

[源码身份](source-identity-r1.json) 的当前任务指纹：`e5f7805b3b03e9aeea7f5f6b4ba1949658affd10cd2af16bf71de23d4f84d564`。所有编入产品的任务源码仍逐字节匹配 ef787282a；之后是测试、Cloud CLI/Skills、数据和证据 overlay，不要求再次重建 App。

[原生身份](native-identity-r1.json)：

- App：`/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper/.qualification/dp-new-r1/aPaper-arm64.app`。
- bundle：`com.atompaper.APaperDPNewQualification`；Debug/arm64；资源 sourceRevision ef787282a。
- executable SHA：`925eb9113faa6cb62a4bfc1bdcdb4d6bf1042452ca64f838b17efc2736618599`。
- 静态 FFI archive SHA：`dec34ea8ab5b862919cb308377e34e4086909fb163063d48d630ded56431a0b9`；链接符号 receipt 包含实际 source_catalog 和 academic_search C exports；资源逐文件 SHA 在 identity 中。
- 最终启动 witness PID 99296；App/Core 资格配置根一致：`/var/folders/wl/g0m40l115jg74r9qmy662zr80000gn/T/apaper-dp-new-7y4zcgr_/AppData`。这不是已观察到工作区 Core catalog 调用的声明。
- 原路径差异来自 `.build` symlink，开始时旧源码清单及旧 binary SHA 均匹配。R1 rebuild 已更新该构建输出；原报告的 binary SHA 是历史记录，当前使用上面的独立复制产物。
- 资格缓存更新为最终候选，仅校验并替换任务根 manifest 和改变的 AAMAS 包/meta，没有改账户／onboarding flags。这仍是 cache fixture，不计 online 候选证据。

最终 manifest SHA：`137165cc72dadc950f882b5bbefe32d1017a3d6f2ce5e6418d3c59b54d2d0b9a`；初始未发布候选 SHA dab9… 已成为历史，不声称相同身份。version 在最终 manifest 修改后重新生成。两仓库 manifest/version、全部 66 包 bytes/hash、工具及 AAMAS Skill 逐项一致。

### R1 矩阵

| 条目 | 结果 | 边界 |
|---|---|---|
| R1-01 | PASS（身份） | 当前产品源码、binary、FFI、资源、witness、根可追踪；不等于工作区可用性 |
| R1-02 | BLOCKED | 实际 inspector 未进入；N1/N2 仍 NOT TESTED；共享选择确定性旧结果保留 |
| R1-03 | BLOCKED / NOT TESTED | 同根启动实际仍为 account gate；N3 UI 恢复/刷新、N4 布局/语言/主题/Reduce Motion 未观察 |
| R1-04 | BLOCKED | Core/FFI 新与更新源检索及 ICCV targeted regression PASS；N5 Reader PDF 与 N6 原生日期显示仍 NOT TESTED |
| R1-05 | PARTIAL | T1–T6 实际 downloader＋loopback TLS＋public catalog PASS；生产 0.14 真实 HTTPS PASS；候选 0.15 公网→FFI／原生链仍开放 |
| R1-06 | PARTIAL | ACL/AAAI/AAMAS 有具体对账/修复；CVPR、ICLR、IEEE S&P、SOSP、EMNLP 保留明确开放项 |
| R1-07 | PASS（范围/可恢复） | 针对目标验证与局部检查点；历史失败准确保留；无未经授权发布动作 |

### 更新后的原 AC 矩阵

AC-01/02：继承 PASS，definitions/mapping/DTO 字节不变。AC-03：实现继承 PASS，native NOT TESTED。AC-04：确定性 App scoped 1-test PASS 继承，native NOT TESTED。AC-05：缓存 FFI PASS，加 downloader/public-catalog/Swift 及线上 0.14 HTTPS 分层证据，候选在线链未测。AC-06：PARTIAL（拒绝/保留/恢复及 offline 有针对证据，UI 恢复未测）。AC-07：PARTIAL（下表）。AC-08：摄取 PASS，五源 464 条字节保持。AC-09：最终 candidate validator PASS。AC-10：native BLOCKED。AC-11：PARTIAL，实际 Core/FFI 数据 PASS，native PDF 未测。AC-12：PASS，无未经授权动作。

### 实际命令与计数

原始 receipts 在 [evidence/r1](evidence/r1/)。不累计重试，不把 XCTest 的 0 tests 与 Swift Testing 的实际 2 tests 混淆。

| cwd | 命令 | exit / executed-pass-fail-ignored |
|---|---|---|
| App candidate | `APAPER_DP_NEW_DOWNLOADED_CATALOG=/tmp/dp-new-r1-downloaded-catalog.json APAPER_DP_NEW_TRANSPORT_RECEIPT=/tmp/dp-new-r1-transport-requests.jsonl cargo test --locked --manifest-path rust/Cargo.toml -p apaper_discovery --lib sources::conference:: -- --nocapture` | 0；22/22/0/4，173 filtered |
| App candidate | `cargo test --locked --manifest-path rust/Cargo.toml -p apaper_discovery --lib production_https_catalog_acquisition_without_seeded_cache -- --ignored --nocapture` | 0；1/1/0/0，198 filtered；实时 0.14/20 sources/SHA a92d… |
| App candidate | CoreKit scoped 命令见下 | 0；Swift Testing 2/2/0/0；XCTest 0；包含 6 个真实 ICCV 代表查询 |
| Cloud candidate；App/apaper-cloud | `cargo test --locked` | 各 0；13/13/0/0 |
| 两个 Cloud 工具副本 | `python3 -m unittest discover -s tests -v` | 各 0；8/8/0/0（不把 subcases 另算测试数） |
| Cloud candidate | `cargo run --locked --quiet -- validate-site public` | 0；25 venues/71 editions；全部 66 包 hashes/counts 通过 |
| Cloud candidate | `cargo run --locked --quiet -- ingest-acl --input /tmp/dp-new-r1-audit/acl_xml.data --input /tmp/dp-new-r1-audit/findings_xml.data --venue acl --edition acl:2026 --year 2026 --output /tmp/dp-new-r1-acl-reconciled.jsonl` | 0；4806 emitted、7 skipped；ID 集合完全等于现包；修复前命令虽 exit0 但 0 emitted/4813 skipped，语义失败 receipt 保留 |
| App candidate | `/tmp/dp-new-skill-runtime/bin/python /tmp/dp-new-r1-aamas.py` | 0；仅针对 CSLO7280，OCR 后人工核对；没有全量历史 PDF 获取 |
| Cloud candidate | `import-json` / `pack`，见 skill-workflows-r1.json | 0；640、原639 retained equal；新增1，移除0 |
| App candidate | `APAPER_SKIP_XCODE_SIGNING=1 bash scripts/build-macos-apps.sh Debug arm64 dp-new-native-qualification` | 0；本轮仅一次；资源及代码签名校验；独立输出复制后再 verify |
| App candidate | `codesign --verify --deep --strict .qualification/dp-new-r1/aPaper-arm64.app` | 0 |
| Cloud candidate | `cargo fmt -- --check`（自身新增/修改区整理后） | 0；初次格式差异不算 PASS |
| 两仓库 | `git diff --check`；App build scripts `bash -n`；改动 Python `py_compile` | 0 |
| App candidate | AAMAS Skill `quick_validate.py` | 0；1 Skill，其他 9 unchanged 验证继承 |

CoreKit 实际命令：

```sh
APAPER_DP_NEW_ICCV_SAMPLES=/tmp/dp-new-r1-iccv-samples.json \
APAPER_DP_NEW_DOWNLOADED_CATALOG=/tmp/dp-new-r1-downloaded-catalog.json \
APAPER_CLOUD_ORIGIN=https://127.0.0.1:9 \
APAPER_DP_NEW_CANDIDATE_MANIFEST=/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper/apaper-cloud/public/v1/conferences/manifest.json \
swift test --package-path swift-packages/APaperCoreKit \
  --scratch-path /Users/junesum/.codex/worktrees/dp-new/AtomPaper/.build/dp-new-candidate-corekit \
  --filter 'downloadedCatalogProjectsIntoSwiftDisciplineRows|releaseCandidateVerifiedCacheCrossesProductionCatalogBridge'
```

证据类别：TLS fixture 使用生产 FileDownloader/同步/public catalog，Swift 读取其产生的 DTO JSON；FFI 另通过真实经 SHA 校验的 cache/pack。因此不宣称“候选在线下载→FFI→native”整条 PASS。真实公网测试只取已发布 0.14，未部署候选。Native 仅窗口、正常 guest 操作、同根启动及截图直接观察。Owner evidence：无。

T1：重复相同 version/digest 不再次取得 manifest。T2：旧 0.14 经 downloader 升到候选，定义、来源顺序、多标签及新增来源到达 public catalog 和 Swift 投影。T3：AISTATS 未变包跨实例复用、ICCV 新引用替换旧包。T4：坏 manifest SHA 保留旧 catalog，坏/中断 pack 保留已验证 bytes，恢复后可读取。T5：旧 ICCV 引用／新同路径 bytes 被拒，启动同步边界取得新引用后加载 2701 条。T6：空根 offline 无 conference catalog；冷启动 verified catalog+包可用；未获取 MIDL 包 offline 失败且不作可用缓存。网络请求 receipt 单独保存。

保留初始正常 App test 命令 exit65/0 executed：PaperMentorPresentationTests.swift:300/309 projectSearch 编译漂移。临时 scoped 仅排除 `PaperMentorPresentationTests.swift KfrKnowledgeStewardViewTests.swift`（后者依赖前者 fixture），原一测试 PASS 继承，未永久删除测试；不宣称 App suite PASS。可复现完整命令与输出仍在初始报告/evidence。

可复现的 scoped App 命令（继承证据，R1 未重复执行）：

```sh
xcodebuild test -project apps/macos/APaperApp/APaperApp.xcodeproj \
  -scheme APaperApp -configuration UnitTest -destination 'platform=macOS,arch=arm64' \
  -derivedDataPath .build/dp-new-candidate-unit-tests ARCHS=arm64 ONLY_ACTIVE_ARCH=YES \
  'EXCLUDED_SOURCE_FILE_NAMES=PaperMentorPresentationTests.swift KfrKnowledgeStewardViewTests.swift' \
  -only-testing:APaperAppTests/DailyReadingDateContinuityTests/testDisciplineProjectionsShareSelectionCountsAndPersistDisclosure \
  CODE_SIGNING_ALLOWED=NO
```

正常命令相同但去掉 `EXCLUDED_SOURCE_FILE_NAMES` 参数，其 exit65/0 executed 的原始错误没有隐藏。

没有再运行全 discovery 来重复历史 12 fail；已逐一核对相同测试身份和 assertion/left/right failure mode，12/12 一致，见 [baseline-failures](evidence/r1/dp-new-r1-baseline-failures.json)。Release/Agent cfg 失败保留初始分类，未修复或宣称 formal Release 通过。

### 逐来源处置

完整差异 ID、输入 hash、获取错误、受限项见 [audit-r1.json](audit-r1.json) 及 frozen input receipts。

| 来源 | 处置 | 精确结论 |
|---|---|---|
| CVPR | Still locally incomplete | 完整 all-days 4042 全在现4068内；26 pack-only 的官方 detail404 不能证明应移除，仍需最终撤回/保留身份对账；保留包 |
| ACL | Reconciled; validated catalog correction | 正确 Main/Findings collections＋front matter 对账；真实 importer4806/7；现包不变、partial；未声称七项 PDF 摘要恢复已完成 |
| AAAI | Reconciled; no change required | 43 主技术分册4149 IDs完全相同；不把另外五个专轨/关联会议分册771项强行并入 |
| ICLR | Precisely blocked by external prerequisite | 主会场 accepted＋正sourceid5353均已覆盖；六条最终状态缺口有具体ID；API403、forum browser verification；保留temporary5359；会场出席表不当最终accepted全集 |
| IEEE S&P | Still locally incomplete | 254 titles/authors≠verified pack；论文级身份/摘要/PDF获取、对账与验证尚未完成；publisher proceedings已确认，不能称 upstream未出版；pack:null保留 |
| AAMAS | Reconciled; validated pack correction | CSLO7280标记摘要OCR恢复；XWPK8237无标记摘要且Crossref无摘要，仍按原规则排除；partial640，不静默豁免 |
| SOSP | Precisely blocked by external prerequisite | 2025检查没有覆盖新届发现；已发现[2026](https://sigops.org/s/conferences/sosp/2026/schedule.html)及正式DOI；ACM proceedings/样本403，2026摄取未完成；不称无新届 |
| EMNLP | Precisely blocked by external publication prerequisite | [venue archive](https://aclanthology.org/venues/emnlp/)当前到2025；2026正式collection未确认，官方program已有会议安排；event404不作为“nothing new”；announced/pack:null保留 |

未决 mandatory 项及 partial 排除尚未获得 Owner 的父任务接受，父任务继续 PARTIAL。

## 5. Known Risks

实现缺陷：包校验前覆盖及 ACL XML 身份兼容已修复。原生 guest no-op 可复现但根因未确定；没有把它冒称已证明的账户缺陷或捕捉权限问题。

本地未完成：CVPR 26 条最终状态；IEEE S&P 论文级正式元数据与 PDF 验证；ACL 七项 PDF 摘要恢复没有执行。外部限制：ICLR accepted/final notes browser verification/API403；SOSP2026 ACM403；EMNLP2026最终collection未确认；AAMAS一条确实没有可接纳的标记摘要。上述类别不相互替代。

Native/tooling：间歇 CUA timeout 与其会话重置出现过，最终 AX/截图可用。N1–N5 及 N6 UI 显示仍未测。原生工作区可用性没有建立，不能称 usable acceptance PASS。候选公网 HTTPS origin 尚无获准可用实例，且没有做 candidate→FFI→native在线测试。

历史无关失败：12 个 discovery assertion 身份/模式一致；App test compilation及Release/Agent cfg保持原状。没有广泛模型调用、伪造发现结果或修改模型就绪规则。

## 6. Next Recommended Step

最短下一步是独立定位这个候选上正常 guest 事件未进入工作区的实际 bootstrap 状态／拒绝原因，再在同根继续 N1–N6；不再重建以解决导航或截图问题。

当前没有已确证需要 Owner 亲自授予权限、同意协议或完成保护步骤，因此不请求这些操作。精确候选已保存且当前停在账户页。正常复现启动（先正常退出该资格实例）：

```sh
APAPER_CLOUD_ORIGIN=https://127.0.0.1:9 \
/Users/junesum/.codex/worktrees/dp-new-candidate/AtomPaper/.qualification/dp-new-r1/aPaper-arm64.app/Contents/MacOS/aPaper \
  --apaper-interactive-qualification-root /var/folders/wl/g0m40l115jg74r9qmy662zr80000gn/T/apaper-dp-new-7y4zcgr_/AppData
```

前提：使用上面资格 marker/root 与 dedicated bundle，保留同根。最短复现：账户页 Shift-Tab 到 `account-skip-sign-in`，空格（或直接正常点击“暂不登录”）。期望工作区；现有失败信号是焦点/截图可响应但 account-gate-form不变。不要勾协议或填凭据来掩盖 guest 路由问题。Owner 无需 publisher reconciliation 或 hash 检查。

生产发布／回滚仍仅保留初始报告的未执行计划；改变包库存现增加 `--pack aamas:2026`，其余八个参数不变。没有执行发布、回滚、merge、push、正式替换或迁移。

Implementation: PARTIAL
Existing-source refresh: PARTIAL
New-source ingestion: PASS（保留5来源/464记录）
Automated verification: PARTIAL（R1受影响目标PASS；完整App/Release未PASS）
Catalog-refresh verification: PARTIAL（downloader/TLS及生产0.14 HTTPS PASS；候选公网/原生链开放）
Native verification: BLOCKED（身份/Debug启动PASS，工作区及Reader未观察）
Owner acceptance: PENDING
Local commit(s): PARTIAL checkpoints；最终ID见交接消息/Git
Merged: NO
Pushed: NO
Production metadata deployed: NO
Formal App replaced: NO
Production data migrated: NO
Released: NO
