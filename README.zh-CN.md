<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><a href="./README.md">English</a> · <strong>简体中文</strong></p>
</div>

# aPaper Cloud

aPaper Cloud 是 aPaper 的公共分发仓库，统一提供应用安装与更新包、学术文献元数据及版本化
运行资源，为软件更新和会议目录同步提供可校验的文件与版本信息。应用源码与用户的私有
研究资料在本仓库之外维护。

[网站](https://cloud.apaper.ai) · [发布版本](https://github.com/YociLam/aPaper-Cloud/releases) · [联系支持](mailto:contact@apaper.ai)

## 目录

1. [应用下载与更新](#应用下载与更新)
2. [学术文献元数据](#学术文献元数据)
3. [翻译引擎](#翻译引擎)
4. [仓库结构](#仓库结构)
5. [完整性与发布规范](#完整性与发布规范)

## 应用下载与更新

应用文件通过 GitHub Releases 分发。同一版本可以同时提供用于自动更新的完整 ZIP 包，以及
供首次安装使用的 DMG；两种包装包含相同版本的应用，网站下载入口链接到对应的 Release 资产。

正式版、测试版与资格验证版使用独立渠道。原生 macOS 更新器读取对应渠道的 Sparkle appcast，
其中明确指定归档地址、构建号、最低系统版本、准确大小及 EdDSA 签名。仓库包含多个产品，
因此不会将全局“最新 Release”作为 App 的版本来源。

**当前状态：** App 分发正在进行资格验证，本仓库尚未发布正式稳定版 App。资格预发布包是
独立的测试构建，不是普通用户的安装渠道。

当前资格预发布：[0.1.3（构建 9083）](https://github.com/YociLam/aPaper-Cloud/releases/tag/apaper-update-qualification-20261015-9083)，发布时间为 **2026-10-15 10:38:05 UTC**。

渠道路径、发布顺序和校验要求见[应用分发合同](APP-DISTRIBUTION.md)。完整应用归档保存在
Releases，不进入 Git 历史或 Pages 静态站点。

## 学术文献元数据

会议数据按会议与年份组织，包含文献题录、官方页面、可用的 PDF 来源及 DOI 等信息。
数据包不包含论文 PDF、账户凭据、阅读历史或用户私有文献库内容。

| 目录 | 版本 | 更新时间（UTC） |
| --- | --- | --- |
| 会议 Manifest | `v0.16` | 2026-10-14 16:12:47 |

App 先检查轻量[版本记录](https://cloud.apaper.ai/v1/conferences/version.json)，仅在版本变化时
获取 [Manifest](https://cloud.apaper.ai/v1/conferences/manifest.json)，并验证其 SHA-256。
各会议年份包具有独立版本、字节数和校验值；缺失或过期的数据可以独立同步，无需重新安装 App。

### 收录范围

| 会议 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| NeurIPS | — | 3,540 | 4,493 | 5,823 | 已公布 |
| ICML | — | 1,828 | 2,610 | 3,330 | 6,552 |
| ICLR | — | 435 (部分) | 2,261 (部分) | 3,708 (部分) | 5,359 (部分) |
| CVPR | — | 2,352 | 2,710 | 2,871 | 4,068 |
| ACL | — | 2,150 | 1,982 | 3,353 | 4,806 (部分) |
| AAAI | — | 1,578 | 2,331 | 3,028 | 4,149 |
| IJCAI | — | 850 | 1,047 | 1,279 | 972 |
| EMNLP | — | 2,241 | 2,388 | 3,488 | 已公布 |
| ICCV | — | 2,156 | — | 2,701 | — |
| ECCV | 1,645 | — | 2,387 | — | 已公布 |
| AISTATS | — | — | 547 | 583 | 588 |
| COLT | — | — | — | 181 | 196 |
| AAMAS | — | — | — | 479 | 640 (部分) |
| CoRL | — | — | 264 (部分) | 263 | — |
| RSS | — | — | 134 | 163 | 210 |
| OSDI | — | 55 | 53 | 53 | 136 |
| SOSP | — | 9 (部分) | 43 (部分) | 65 (部分) | — |
| IEEE S&P | — | 已编目 | 261 | 65 | 254 (部分 / 无数据包) |
| NDSS | — | 94 | 140 | 211 | 265 |
| ACCV | 277 | — | 269 | — | — |
| MIDL | — | — | — | — | 221 |
| MLHC | — | — | — | — | 74 |
| CHIL | — | — | — | — | 40 |
| MLCB | — | — | — | 23 | — |
| L4DC | — | — | — | — | 106 |

未附状态的数字表示已发布的数据包。**部分**表示已有可检索数据但覆盖尚不完整；**已编目**表示
会议年份已登记、尚无已发布的数据包；**已公布**表示正式论文集尚待确认。实际可用状态以线上
Manifest 为准。表格使用会议目录的发布时间，目前不单独记录每个会议年份的更新时间。

每条记录保留来源信息。分类和来源分组只采用出版方明确提供的内容，不推断缺失分类。
部分 ICLR 与 SOSP 记录仍保留构建期来源标记 `temporary_reference_supabase_v1`，这不表示
App 在运行时连接 Supabase。

DP-NEW 目录包含 31 个来源（25 个会议、6 个期刊）、77 个年度选择、72 个数据包。带有效数据包的部分届次仍可选；“无数据包”不可选。分类定义与来源引用共享 Manifest 哈希；映射由 aPaper 审核，不是 OECD 对会议的官方分类。详见[执行报告](docs/dp-new/DP-NEW-report.md)和[分类映射](docs/dp-new/discipline-mapping.md)。

## 翻译引擎

当前 App 从已签名应用包内部署和修复专用翻译环境。翻译器更新随 App 版本一同交付，运行时
不轮询历史 Cloud 翻译版本接口，也不通过这些接口下载环境包。

| App 内置资源（macOS arm64） | 版本 | 更新时间（UTC） |
| --- | --- | --- |
| 翻译器 | `v0.4` | 2026-09-26 13:17:43 |
| 环境包 | `v0.1-r1` | 2026-08-27 12:30:26 |

上述信息对应网站展示的已验证内置资源快照，不代表另行提供了 Cloud v0.4 下载包，也不构成
正式 App 发布声明。翻译器与环境分别管理版本；`v0.1-r1` 表示 v0.1 环境归档的修订版。
[资源状态记录](https://cloud.apaper.ai/v1/app/macos/arm64/components/translation.json)保存准确的包校验值。

历史 `translation-engine-v0.1` Release 与 `/v1/translation/` 接口继续保留，用于兼容已有使用者、
维护者手动下载及可复现构建。其中，原 arm64 归档仍是 r1 构建配方固定引用的基础输入。
历史资产不覆盖、不重新标注为新版本环境包。详见[翻译引擎分发说明](translation-engine/README.md)。

## 仓库结构

```text
public/
  index.html                           公共资源状态页
  v1/app/macos/arm64/
    components/translation.json         App 内置资源状态
    <channel>/appcast.xml               对应渠道的应用更新源（发布后生效）
  v1/conferences/
    version.json                       目录版本与 Manifest 校验值
    manifest.json                      会议、年份及数据包完整性信息
    packs/<venue>/<year>.jsonl.zst      压缩文献元数据
  v1/translation/                      历史兼容元数据
translation-engine/                    环境来源、构建配方及历史资产路由
src/                                  目录打包与校验工具
APP-DISTRIBUTION.md                     应用发布与渠道合同
```

App ZIP／DMG 与历史环境归档通过 GitHub Release 资产分发。静态服务的规范地址是
`https://cloud.apaper.ai`，会议 Manifest 中的包路径相对于该地址解析。

## 完整性与发布规范

元数据发布前校验 Schema、记录数、大小和 SHA-256。应用更新归档还需要原生代码签名检查与
Sparkle EdDSA 签名。正式 App 分发另有 Developer ID 与公证门槛，资格验证通过不等于
正式稳定版已获准发布。

每次发布 App 或内置资源时，必须同步更新**中英文 README 与网站**中对应的版本、构建号、
更新时间和下载地址。信息以实际签名产物及资源变更记录为准，不用网站部署时间代替引擎
更新时间。先上传并验证不可变 Release 资产，再发布引用它的 appcast；保留无关会议包及
历史兼容接口。

在本仓库根目录执行目录校验：

```sh
cargo run --locked -- validate-site public
cargo test --locked
```

GitHub Actions 负责会议目录和翻译引擎分发校验。历史资产路由另有测试与 Worker 打包 dry-run；
更新其开发工具依赖不会部署或删除线上 Worker。

## E1 期刊元数据

Schema 1 保持 `venues` 仅为会议，使用独立 `journals` 扩展；旧客户端不枚举期刊，新客户端明确保留 journal 类型、ISSN、出版方文章类型、实际卷期/文章号与日期精度。年度包是分发分区，不是出版方卷号。六个 2026 许可快照截至 2026-10-14T15:44:19Z，共 1,552 条；JLB 为可用 partial/10，14 条 NC/ND 许可明确排除，另两条许可/摘要缺口仍开放。其余五源仅对声明输入、范围和截止点完整，不代表未来全年。前 66 包字节不变。0.16 发布使用上述已验证快照字节；见[契约](docs/dp-new/E1-journal-contract.md)与 docs/dp-new/evidence/e1/ 逐源核对收据。
