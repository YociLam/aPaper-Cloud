<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><a href="./README.md">English</a> · <strong>简体中文</strong></p>
</div>

# aPaper Cloud

aPaper Cloud 提供 aPaper App 更新归档与学术文献元数据，为软件更新和会议目录同步提供
可校验的文件与版本信息。应用源码与用户的私有研究资料在本仓库之外维护。

[网站](https://cloud.apaper.ai) · [发布版本](https://github.com/YociLam/aPaper-Cloud/releases) · [联系支持](mailto:contact@apaper.ai)

## 目录

1. [应用下载与更新](#应用下载与更新)
2. [学术文献元数据](#学术文献元数据)
3. [App 内置资源](#app-内置资源)
4. [仓库结构](#仓库结构)
5. [完整性与发布规范](#完整性与发布规范)

## 应用下载与更新

新安装 DMG 由 [aPaper Releases](https://github.com/YociLam/aPaper/releases) 提供；本仓库继续提供完整更新 ZIP 与频道元数据。两种包装必须包含同一个封装 App。历史资产与下载地址保持不变。

正式版、测试版与资格验证版使用独立渠道。原生 macOS 更新器读取对应渠道的 Sparkle appcast，
其中明确指定归档地址、构建号、最低系统版本、准确大小及 EdDSA 签名。App 版本以对应渠道的更新源为准。

**当前状态：** 当前稳定发布通过生产 Ed25519 签名更新包支持用户确认后的应用内安装；App 使用临时签名、未经 Apple 公证。资格预发布保持独立。

当前资格预发布：[0.1.3（构建 9083）](https://github.com/YociLam/aPaper-Cloud/releases/tag/apaper-update-qualification-20261015-9083)，发布时间为 **2026-10-15 10:38:05 UTC**。

当前稳定发布： [0.1.2 (build 1003)](https://github.com/YociLam/aPaper/releases/tag/v0.1.2-b1003) · 2026-10-22T04:36:59Z · ad-hoc / unnotarized / sparkle-eddsa.

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

## App 内置资源

翻译环境随每个 App 归档一同交付，并随 App 版本更新。App 从已签名应用包内部署和修复对应资源。

| App 内置资源（macOS arm64） | 版本 | 更新时间（UTC） |
| --- | --- | --- |
| 翻译器 | `v0.6` | 2026-10-21 14:19:11 |
| 环境包 | `v0.2` | 2026-10-21 14:19:11 |

[资源状态记录](https://cloud.apaper.ai/v1/app/macos/arm64/components/translation.json)保存已验证的内置资源版本与校验值。

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
src/                                  目录打包与校验工具
APP-DISTRIBUTION.md                     应用发布与渠道合同
```

App 更新 ZIP 与适用的增量归档在本仓库的 Release 资产中分发；新安装 DMG 放在 aPaper Releases，已有 Cloud DMG 保留。静态服务的规范地址是
`https://cloud.apaper.ai`，会议 Manifest 中的包路径相对于该地址解析。

## 完整性与发布规范

元数据发布前校验 Schema、记录数、大小和 SHA-256。应用更新归档还需要原生代码签名检查与
生产 Sparkle EdDSA 签名与原生安装资格验证。明确标注的临时签名、未公证分发只支持安全版本检查与手动安装；Apple 付费会员及公证暂缓，既有公证生产通道门槛保留。无生产密钥时，检查信息不包含可执行 enclosure，也不替用资格验证密钥。本次文档修改不代表二进制或稳定频道已发布。

每次发布 App 时，必须同步更新**中英文 README 与网站**中对应的版本、构建号、
更新时间和下载地址。信息以实际签名产物及资源变更记录为准，不用网站部署时间代替引擎
更新时间。先上传并验证不可变 Release 资产，再发布引用它的 appcast；保留无关会议包及
App 更新渠道。

在本仓库根目录执行目录校验：

```sh
cargo run --locked -- validate-site public
cargo test --locked
```

GitHub Actions 在发布前校验目录。App 归档包含经校验的翻译环境及其许可说明。

## E1 期刊元数据

Schema 1 保持 `venues` 仅为会议，使用独立 `journals` 扩展；旧客户端不枚举期刊，新客户端明确保留 journal 类型、ISSN、出版方文章类型、实际卷期/文章号与日期精度。年度包是分发分区，不是出版方卷号。六个 2026 许可快照截至 2026-10-14T15:44:19Z，共 1,552 条；JLB 为可用 partial/10，14 条 NC/ND 许可明确排除，另两条许可/摘要缺口仍开放。其余五源仅对声明输入、范围和截止点完整，不代表未来全年。前 66 包字节不变。0.16 发布使用上述已验证快照字节；见[契约](docs/dp-new/E1-journal-contract.md)与 docs/dp-new/evidence/e1/ 逐源核对收据。
