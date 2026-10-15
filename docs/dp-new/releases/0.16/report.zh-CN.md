# DP-NEW 元数据 0.16 上线报告

## 1. Implementation Summary

**元数据上线 PASS。** 2026-10-15 12:56:21（Asia/Taipei）现有 GitHub Pages 正式部署成功，13:00 后公网验收完成。正式目录从 0.14 更新为 0.16：31 个来源（25 会议、6 期刊）、77 个年度集合、72 个元数据包。

本次相对 0.14 的 15 个新增/更新包：ICML 2026、IJCAI 2026、ICCV 2025、AAMAS 2026；MIDL 2026、MLHC 2026、CHIL 2026、MLCB 2025、L4DC 2026；GLJ、JLB、PLOS Medicine、PLOS Global Public Health、PLOS Biology、PLOS Climate 的 2026 快照。新增五会议共 464 条、新增六期刊共 1552 条；这些是声明范围快照，非完整未来全年。

发布前修正原工具仅枚举会议的问题，让既有标题规范化和公网校验同时覆盖 journals；新增三个校验回归。规范化结果 changed_packs=0、normalized_titles=0；沿用已验收的 manifest/pack 字节，没有为本地测试消耗版本。

## 2. Files Changed

Cloud 仓库：`/Users/junesum/Documents/aPaper-Cloud-trans24-python-engine`；发布工作树：`/Users/junesum/Documents/AtomPaper-worktrees/dp-new-metadata-publication`。

Cloud main 已推送，实际部署 source commit：`0b93377125e032ab606c38056451f3f55a48de40`（工具/说明修改 `cb773b1`，预发布证据 `0b93377`）。发布前正常合并远端 `81b224a`，保留其 App 资格包 9062、appcast 与首页变更，没有 force push。当前提交仅更新报告和收据，不改变已部署的 public 字节。

Modified：英文/中文 README、网页 metadata 说明、两份既有发布工具。Created：release verifier 测试、发布计划及真实 HTTPS 收据。Deleted：无产品文件。manifest SHA、version record 和全部 pack 字节保持已验收候选身份。

App 开发副本同步只限元数据说明/工具/测试；资格启动脚本在正常退出后使用正式 HTTPS 元数据源。正式 App、生产资料库、账号与翻译包不变。App 仓库源码/报告保留本地；本轮推送只限 Cloud。

## 3. Architecture Verification

沿用现有 Pages 工作流，没有新建服务、改变 DNS/机器信任或添加下载器。TLS、manifest SHA、pack 大小/hash 校验保持。公共 wire 继续分开 conferences/journals，旧客户端不误认期刊。31 source、77 collection 和 72 pack 数据直接来自最终 manifest；partial、pack:null 和来源 provenance 不变。

发布范围是公共元数据，不是正式 App 二进制发版。已有 App 资格 appcast 与 Translation version 的公网实际字节已核对保持一致；没有更换签名、推新 App release 或迁移生产用户数据。

## 4. Validation Evidence

- [正式部署流水线](https://github.com/YociLam/aPaper-Cloud/actions/runs/38684026216)：success；部署 SHA 与上述 source commit 一致。
- [公网版本](https://cloud.apaper.ai/v1/conferences/version.json)：0.16；[普通 manifest URL](https://cloud.apaper.ai/v1/conferences/manifest.json) 的 SHA-256 为 `7d5a82fdddcaaa1597475d7dfcdb9971762973aaf8c8f764a42e764b470e2c74`，与 version record、本地已验收候选完全一致。
- 官方 release verifier：实际 HTTPS 校验 72/72 包，0 fail；覆盖大小、SHA 和本地参考，不仅查看 HTTP200。另以不带缓存绕过参数的常规 URL 校验本次 15/15 包，0 fail。
- Cloud `cargo test --locked`：13 executed、13 pass、0 fail；Python unittest：18 executed、18 pass、0 fail；App 开发副本新增工具回归：3 executed、3 pass、0 fail。真实 validator：31 sources/77 collections/72 packs；规范化没有改包。App 上一轮合并回归 6/6、downloader 24/24 等按原收据继承，不重复计作本轮执行。
- 常规公网资格 appcast：1886 bytes，SHA `96a94e11cb5f6aa09eb1751d229fd6526ec99ca019cdb53c476fe3b5516149ce`；Translation version：276 bytes，SHA `bcbcba8fb9d08d7de436028a9583e6020e05cc326bc2e14b400837875be0d10b`；均与已保留参考字节相同。

[验收汇总](dp-new-publish-summary.json)、[实际校验 argv 与全部 72 IDs](dp-new-publish-verification-command.json)、[完整公网校验日志](dp-new-publish-live-verification.log)、[常规 URL 的 15 包证据](dp-new-publish-plain-pack-verification.json)、[既有分发控制文件](dp-new-publish-unrelated-controls.json)、[预发布计划与变更包清单](publication-plan.json)。控制文件最初使用默认 Python User-Agent 获得 403；随后正常匿名 curl HTTPS 获得 HTTP200 并按字节核对，没有认证/安全绕过，也未将 403 当作文件不存在。

manifest 的 generated_at/updated_at 保留数据快照身份（2026-10-14T16:12:47Z）；实际部署时间另记，不将发布日期伪装为数据覆盖截止点。期刊采集截止仍是 2026-10-14T15:44:19Z。

## 5. Known Risks

JLB partial/10、两条摘要/许可前提和原 publisher 审计队列保持明确状态，发布不会自动解决这些内容缺口。没有新模型配置或付费检索；模型依赖推荐/Reader、ICCV 原生论文级日期与历史非相关 suite 问题仍按原报告追踪。

本轮新增的是正式公网控制面与包的真实 HTTPS 证据。没有将其冒充 App 内公开源版本变化/坏包恢复的新增原生观察；之前 verified-cache 原生目录、选择与 Reader 证据保持原边界。正式旧版 App 是否具备期刊 UI 取决于其客户端版本；本次没有发布新客户端。

## 6. Next Recommended Step

如需立即查看新目录，正常退出已验收 E1 候选后，用更新后的安全启动脚本重新打开；它仍使用同一隔离根，并改为 `https://cloud.apaper.ai` 元数据源。若候选仍在运行，脚本只前置现有窗口，不会强退或改变当前阅读状态。无需 Owner 做 hash、Git 或出版方核对。

Metadata publication: PASS / 0.16
Public catalog: PASS / 31 sources / 77 collections
Public packs: PASS / 72 of 72
Changed ordinary URLs: PASS / 15 of 15
Cloud pushed: YES
Production metadata deployed: YES
Formal App released/replaced: NO
Production user data migrated: NO
Rollback executed: NO
Parent publisher audit: PARTIAL / unchanged
