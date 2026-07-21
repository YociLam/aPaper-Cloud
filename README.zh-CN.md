<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><a href="./README.md">English</a> · <strong>简体中文</strong></p>
</div>

# aPaper Cloud

`aPaper Cloud` 是一个静态、版本化的 aPaper 公共元数据分发项目。它不存储用户资料、
阅读历史、推荐内容、账户凭据、PDF 文件或其他私有工作区数据。

首个发布的数据集为各类学术会议论文集目录。会议元数据按具体会议及举办年份独立划分，
因此 App 只会下载用户所选会议年份对应的数据包。

- 正式地址：`https://cloud.apaper.ai`
- 当前 Manifest：`v0.10`
- 目录更新时间：`2026-07-21 18:02:36 UTC`

## 收录概览

下表来自 `public/v1/conferences/manifest.json`。数字表示该会议年份当前收录的论文数；
未附状态说明的数字表示该年份的数据包已完整发布并通过发布校验，可供 App 同步。

| 会议 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ICLR | — | 435（部分） | 2,261（部分） | 3,708（部分） | 5,359（部分） |
| ICML | — | 1,828 | 2,610 | 3,330 | 6,341（已编目） |
| NeurIPS | — | 3,540 | 4,493 | 5,823 | 已公布 |
| AAAI | — | 1,578 | 2,331 | 3,028 | 4,149 |
| CVPR | — | 2,352 | 2,710 | 2,871 | 4,068 |
| ECCV | 1,645 | — | 2,387 | — | 已公布 |
| IJCAI | — | 850 | 1,047 | 1,279 | 已公布 |
| ACL | — | 2,150 | 1,982 | 3,353 | 4,806 |
| EMNLP | — | 2,241 | 2,388 | 3,488 | 已公布 |
| OSDI | — | 55 | 53 | 53 | 136 |
| SOSP | — | 9（部分） | 43（部分） | 65（部分） | — |
| IEEE S&P | — | 已编目 | 261 | 65 | 254（部分） |
| NDSS | — | 94 | 140 | 211 | 265 |
| AISTATS | — | — | 547 | 583 | — |
| COLT | — | — | — | 181 | 196 |
| CoRL | — | — | 264（部分） | 263 | — |
| RSS | — | — | 134 | 163 | — |
| ICCV | — | 2,156 | — | 949 | — |
| ACCV | 277 | — | 269 | — | — |
| AAMAS | — | — | — | 479 | 639（部分） |

状态说明：

- **已发布**：元数据包已生成并通过记录数、体积和 SHA-256 校验，可供 App 同步。
- **部分**：已有可检索数据包，但元数据或公开 PDF 覆盖仍不完整。
- **已编目**：已确认会议年份或论文数量，但尚未发布可下载的数据包。
- **已公布**：会议年份已进入目录，正式论文集尚未达到发布条件。

目录表按每次 Manifest 发布统一更新时间；项目目前不为单个会议年份维护独立更新时间。

## 数据结构

```text
public/
  v1/
    conferences/
      version.json
      manifest.json
      packs/<venue>/<year>.jsonl.zst
```

- `version.json` 是 App 启动时首先访问的轻量版本入口。
- `manifest.json` 记录完整会议目录、会议多语言名称、年份、状态、论文数量、数据包大小和
  SHA-256。
- `packs/<venue>/<year>.jsonl.zst` 是按会议年份拆分的只读元数据包。
- 数据包只保存元数据和经过验证的来源链接，不保存 PDF 文件。

生产环境的规范来源始终是 `https://cloud.apaper.ai`。Manifest 中的数据包路径均为相对路径。
新增会议、修改会议多语言名称或发布新年份时，都不需要重新构建 App。

## App 同步约定

1. App 启动时请求 `version.json`，只比较远端与本地的两段式 `manifest_version`。
2. 版本相同则停止，不重复下载 Manifest 或会议数据包。
3. 版本不同才下载 `manifest.json`，并使用 `version.json` 中的 SHA-256 校验内容。
4. App 根据已校验的 Manifest 动态生成会议来源列表及其本地化名称。首次启动若尚未成功同步
   Manifest，则会议列表为空，只保留独立的 arXiv 与 bioRxiv 来源。
5. Manifest 校验通过后，App 通过有界后台队列逐个同步会议年份包，避免集中请求服务器。
6. 用户勾选会议年份时，如果本地数据包缺失或损坏，仍会触发一次按需恢复下载。

## 数据边界

- Rust 会校验 Schema、记录数、压缩体积和 SHA-256。
- Swift 不负责下载、解析或索引会议元数据。
- App 的本地缓存位于 `~/Documents/aPaper`，不写入源码仓库。
- PDF 保留在论文来源网站，仅在用户打开或导入论文时访问。
- `source_group` 只能保存出版方提供的 track、session、subject 或 collection，不能根据标题、
  摘要、会议名称或模型推断。
- 没有可靠逐论文分类时，`categories` 和 `source_group` 保持为空。

## 数据来源

已发布或已编目的会议包括 ICLR、ICML、NeurIPS、AAAI、CVPR、ECCV、IJCAI、ACL、
EMNLP、OSDI、SOSP、IEEE S&P、NDSS、AISTATS、COLT、CoRL、RSS、ICCV、ACCV 和
AAMAS。每条记录保留其官方 landing URL、PDF URL、DOI（如有）和 provenance URL。

ICLR 2024–2026 与 SOSP 2024–2025 目前仍包含通过参考项目 Supabase 导入的临时构建期数据。
这些记录带有 `metadata_channel=temporary_reference_supabase_v1`，App 不会在运行时访问
Supabase。迁移边界和拆除清单见
`skills/manage-apaper-cloud-metadata/TEMPORARY_REFERENCE_SUPABASE_CHANNEL.md`。

## 维护流程

`skills/` 中为每个会议提供独立提取 Skill，并由
`skills/manage-apaper-cloud-metadata/SKILL.md` 统一约束打包、版本升级、校验和发布流程。

一次标准更新包含：

1. 读取对应的 `skills/extract-<venue>-metadata/SKILL.md`，从官方来源提取数据。
2. 规范化为 aPaper 会议记录格式，并核对数量、必填字段、重复 ID 和来源分组。
3. 生成对应会议年份的 `.jsonl.zst` 数据包。
4. 更新 Manifest；一次发布只推进一次两段式版本号，例如 `0.9` → `0.10`。
5. 重新生成 `version.json`，执行本地校验和 Rust 测试。
6. 发布到 GitHub 与 Cloudflare，并逐个核对线上数据包的大小和 SHA-256。

## 通用工具

从出版方提取出的 JSON 数组可以先通过通用导入器规范化：

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- import-json \
  --input /tmp/<venue>-<year>.json \
  --venue <venue> \
  --edition <venue>:<year> \
  --year <year> \
  --output /tmp/<venue>-<year>.jsonl
```

将规范化 JSONL 打包为发布文件：

```bash
cargo run --manifest-path apaper-cloud/Cargo.toml -- pack \
  --input /tmp/<venue>-<year>.jsonl \
  --output apaper-cloud/public/v1/conferences/packs/<venue>/<year>.jsonl.zst
```

在最终修改 Manifest 后更新轻量版本入口：

```bash
python3 apaper-cloud/skills/manage-apaper-cloud-metadata/scripts/update_version.py \
  apaper-cloud/public
```

发布前执行完整本地校验：

```bash
cargo run --quiet --manifest-path apaper-cloud/Cargo.toml -- \
  validate-site apaper-cloud/public
cargo test --manifest-path apaper-cloud/Cargo.toml
cargo test --manifest-path rust/Cargo.toml -p apaper_discovery --lib
```

部署后核对版本、Manifest 和本次变化的每个会议年份包：

```bash
python3 apaper-cloud/skills/manage-apaper-cloud-metadata/scripts/verify_published_release.py \
  --public apaper-cloud/public \
  --origin https://cloud.apaper.ai \
  --pack <venue>:<year> \
  --pack <venue>:<year>
```

ACL Anthology XML、AAAI OAI-PMH、CVF Open Access 等来源具有各自的专用提取器；它们属于
会议 Skill 的采集适配层，不是整个项目唯一的导入方式。
