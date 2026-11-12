<div align="center">
  <img src="./assets/aPaper.png" alt="aPaper Cloud" width="980">
  <p><a href="./README.md">English</a> · <strong>简体中文</strong></p>
</div>

# aPaper Cloud

aPaper Cloud 提供 aPaper App 使用的公开更新信息与研究资源。应用源码和用户私有数据在本仓库之外维护。

[网站](https://cloud.apaper.ai) · [联系支持](mailto:contact@apaper.ai)

## 公开资源

| 资源 | 公开路径 | 用途 |
| --- | --- | --- |
| macOS App 更新 | [稳定版更新源](https://cloud.apaper.ai/v1/app/macos/arm64/stable/appcast.xml) | 仅在更新归档发布并核验后提供可用更新。 |
| 文献目录 | [版本记录](https://cloud.apaper.ai/v1/conferences/version.json) · [Manifest](https://cloud.apaper.ai/v1/conferences/manifest.json) | 列出可用的会议、期刊元数据包及其校验值。 |
| Dogzee 模型分组 | [策略 JSON](https://cloud.apaper.ai/v1/config/dogzee-group-policy.v1.json) | 提供公开分组名称、模型推理选项与智能体默认配置。 |

App 安装包放在 [aPaper Releases](https://github.com/YociLam/aPaper/releases)。经过验证的更新归档在可用时发布到本仓库的 [Releases](https://github.com/YociLam/aPaper-Cloud/releases)。翻译器和运行环境包含在每个 App 归档中，随 App 更新，不单独作为 Cloud 下载资源发布。

当前稳定发布：暂无经过核验的可用更新。App 首发版本 **0.1.0** 正在准备中。

## 文献包列表

目录版本： **0.16** · 更新时间（UTC）： **2026-10-14T16:12:47Z**

共 31 个来源：25 个会议、6 个期刊；77 个年份条目中有 72 个数据包。按 Manifest 的 OECD 学科分类列出，跨学科来源会在多个分类中出现。

### 计算机与信息科学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | NeurIPS | — | [3,540](https://cloud.apaper.ai/v1/conferences/packs/neurips/2023.jsonl.zst) | [4,493](https://cloud.apaper.ai/v1/conferences/packs/neurips/2024.jsonl.zst) | [5,823](https://cloud.apaper.ai/v1/conferences/packs/neurips/2025.jsonl.zst) | 已预告 |
| 会议 | ICML | — | [1,828](https://cloud.apaper.ai/v1/conferences/packs/icml/2023.jsonl.zst) | [2,610](https://cloud.apaper.ai/v1/conferences/packs/icml/2024.jsonl.zst) | [3,330](https://cloud.apaper.ai/v1/conferences/packs/icml/2025.jsonl.zst) | [6,552](https://cloud.apaper.ai/v1/conferences/packs/icml/2026.jsonl.zst) |
| 会议 | ICLR | — | [435](https://cloud.apaper.ai/v1/conferences/packs/iclr/2023.jsonl.zst)（部分） | [2,261](https://cloud.apaper.ai/v1/conferences/packs/iclr/2024.jsonl.zst)（部分） | [3,708](https://cloud.apaper.ai/v1/conferences/packs/iclr/2025.jsonl.zst)（部分） | [5,359](https://cloud.apaper.ai/v1/conferences/packs/iclr/2026.jsonl.zst)（部分） |
| 会议 | CVPR | — | [2,352](https://cloud.apaper.ai/v1/conferences/packs/cvpr/2023.jsonl.zst) | [2,710](https://cloud.apaper.ai/v1/conferences/packs/cvpr/2024.jsonl.zst) | [2,871](https://cloud.apaper.ai/v1/conferences/packs/cvpr/2025.jsonl.zst) | [4,068](https://cloud.apaper.ai/v1/conferences/packs/cvpr/2026.jsonl.zst) |
| 会议 | ACL | — | [2,150](https://cloud.apaper.ai/v1/conferences/packs/acl/2023.jsonl.zst) | [1,982](https://cloud.apaper.ai/v1/conferences/packs/acl/2024.jsonl.zst) | [3,353](https://cloud.apaper.ai/v1/conferences/packs/acl/2025.jsonl.zst) | [4,806](https://cloud.apaper.ai/v1/conferences/packs/acl/2026.jsonl.zst)（部分） |
| 会议 | AAAI | — | [1,578](https://cloud.apaper.ai/v1/conferences/packs/aaai/2023.jsonl.zst) | [2,331](https://cloud.apaper.ai/v1/conferences/packs/aaai/2024.jsonl.zst) | [3,028](https://cloud.apaper.ai/v1/conferences/packs/aaai/2025.jsonl.zst) | [4,149](https://cloud.apaper.ai/v1/conferences/packs/aaai/2026.jsonl.zst) |
| 会议 | IJCAI | — | [850](https://cloud.apaper.ai/v1/conferences/packs/ijcai/2023.jsonl.zst) | [1,047](https://cloud.apaper.ai/v1/conferences/packs/ijcai/2024.jsonl.zst) | [1,279](https://cloud.apaper.ai/v1/conferences/packs/ijcai/2025.jsonl.zst) | [972](https://cloud.apaper.ai/v1/conferences/packs/ijcai/2026.jsonl.zst) |
| 会议 | EMNLP | — | [2,241](https://cloud.apaper.ai/v1/conferences/packs/emnlp/2023.jsonl.zst) | [2,388](https://cloud.apaper.ai/v1/conferences/packs/emnlp/2024.jsonl.zst) | [3,488](https://cloud.apaper.ai/v1/conferences/packs/emnlp/2025.jsonl.zst) | 已预告 |
| 会议 | ICCV | — | [2,156](https://cloud.apaper.ai/v1/conferences/packs/iccv/2023.jsonl.zst) | — | [2,701](https://cloud.apaper.ai/v1/conferences/packs/iccv/2025.jsonl.zst) | — |
| 会议 | ECCV | [1,645](https://cloud.apaper.ai/v1/conferences/packs/eccv/2022.jsonl.zst) | — | [2,387](https://cloud.apaper.ai/v1/conferences/packs/eccv/2024.jsonl.zst) | — | 已预告 |
| 会议 | AISTATS | — | — | [547](https://cloud.apaper.ai/v1/conferences/packs/aistats/2024.jsonl.zst) | [583](https://cloud.apaper.ai/v1/conferences/packs/aistats/2025.jsonl.zst) | [588](https://cloud.apaper.ai/v1/conferences/packs/aistats/2026.jsonl.zst) |
| 会议 | COLT | — | — | — | [181](https://cloud.apaper.ai/v1/conferences/packs/colt/2025.jsonl.zst) | [196](https://cloud.apaper.ai/v1/conferences/packs/colt/2026.jsonl.zst) |
| 会议 | AAMAS | — | — | — | [479](https://cloud.apaper.ai/v1/conferences/packs/aamas/2025.jsonl.zst) | [640](https://cloud.apaper.ai/v1/conferences/packs/aamas/2026.jsonl.zst)（部分） |
| 会议 | CoRL | — | — | [264](https://cloud.apaper.ai/v1/conferences/packs/corl/2024.jsonl.zst)（部分） | [263](https://cloud.apaper.ai/v1/conferences/packs/corl/2025.jsonl.zst) | — |
| 会议 | RSS | — | — | [134](https://cloud.apaper.ai/v1/conferences/packs/rss/2024.jsonl.zst) | [163](https://cloud.apaper.ai/v1/conferences/packs/rss/2025.jsonl.zst) | [210](https://cloud.apaper.ai/v1/conferences/packs/rss/2026.jsonl.zst) |
| 会议 | OSDI | — | [55](https://cloud.apaper.ai/v1/conferences/packs/osdi/2023.jsonl.zst) | [53](https://cloud.apaper.ai/v1/conferences/packs/osdi/2024.jsonl.zst) | [53](https://cloud.apaper.ai/v1/conferences/packs/osdi/2025.jsonl.zst) | [136](https://cloud.apaper.ai/v1/conferences/packs/osdi/2026.jsonl.zst) |
| 会议 | SOSP | — | [9](https://cloud.apaper.ai/v1/conferences/packs/sosp/2023.jsonl.zst)（部分） | [43](https://cloud.apaper.ai/v1/conferences/packs/sosp/2024.jsonl.zst)（部分） | [65](https://cloud.apaper.ai/v1/conferences/packs/sosp/2025.jsonl.zst)（部分） | — |
| 会议 | IEEE S&P | — | 已编目 | [261](https://cloud.apaper.ai/v1/conferences/packs/ieee_sp/2024.jsonl.zst) | [65](https://cloud.apaper.ai/v1/conferences/packs/ieee_sp/2025.jsonl.zst) | 254（部分，无数据包） |
| 会议 | NDSS | — | [94](https://cloud.apaper.ai/v1/conferences/packs/ndss/2023.jsonl.zst) | [140](https://cloud.apaper.ai/v1/conferences/packs/ndss/2024.jsonl.zst) | [211](https://cloud.apaper.ai/v1/conferences/packs/ndss/2025.jsonl.zst) | [265](https://cloud.apaper.ai/v1/conferences/packs/ndss/2026.jsonl.zst) |
| 会议 | ACCV | [277](https://cloud.apaper.ai/v1/conferences/packs/accv/2022.jsonl.zst) | — | [269](https://cloud.apaper.ai/v1/conferences/packs/accv/2024.jsonl.zst) | — | — |
| 会议 | MIDL | — | — | — | — | [221](https://cloud.apaper.ai/v1/conferences/packs/midl/2026.jsonl.zst) |
| 会议 | MLHC | — | — | — | — | [74](https://cloud.apaper.ai/v1/conferences/packs/mlhc/2026.jsonl.zst) |
| 会议 | CHIL | — | — | — | — | [40](https://cloud.apaper.ai/v1/conferences/packs/chil/2026.jsonl.zst) |
| 会议 | MLCB | — | — | — | [23](https://cloud.apaper.ai/v1/conferences/packs/mlcb/2025.jsonl.zst) | — |
| 会议 | L4DC | — | — | — | — | [106](https://cloud.apaper.ai/v1/conferences/packs/l4dc/2026.jsonl.zst) |

### 数学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | AISTATS | — | — | [547](https://cloud.apaper.ai/v1/conferences/packs/aistats/2024.jsonl.zst) | [583](https://cloud.apaper.ai/v1/conferences/packs/aistats/2025.jsonl.zst) | [588](https://cloud.apaper.ai/v1/conferences/packs/aistats/2026.jsonl.zst) |
| 会议 | COLT | — | — | — | [181](https://cloud.apaper.ai/v1/conferences/packs/colt/2025.jsonl.zst) | [196](https://cloud.apaper.ai/v1/conferences/packs/colt/2026.jsonl.zst) |

### 生物科学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | MLCB | — | — | — | [23](https://cloud.apaper.ai/v1/conferences/packs/mlcb/2025.jsonl.zst) | — |
| 期刊 | PLOS Biology | — | — | — | — | [365](https://cloud.apaper.ai/v1/conferences/packs/plos_biology/2026.jsonl.zst) |

### 电气工程、电子工程与信息工程

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | CoRL | — | — | [264](https://cloud.apaper.ai/v1/conferences/packs/corl/2024.jsonl.zst)（部分） | [263](https://cloud.apaper.ai/v1/conferences/packs/corl/2025.jsonl.zst) | — |
| 会议 | RSS | — | — | [134](https://cloud.apaper.ai/v1/conferences/packs/rss/2024.jsonl.zst) | [163](https://cloud.apaper.ai/v1/conferences/packs/rss/2025.jsonl.zst) | [210](https://cloud.apaper.ai/v1/conferences/packs/rss/2026.jsonl.zst) |
| 会议 | L4DC | — | — | — | — | [106](https://cloud.apaper.ai/v1/conferences/packs/l4dc/2026.jsonl.zst) |

### 医学工程

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | MIDL | — | — | — | — | [221](https://cloud.apaper.ai/v1/conferences/packs/midl/2026.jsonl.zst) |

### 健康科学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 会议 | MLHC | — | — | — | — | [74](https://cloud.apaper.ai/v1/conferences/packs/mlhc/2026.jsonl.zst) |
| 会议 | CHIL | — | — | — | — | [40](https://cloud.apaper.ai/v1/conferences/packs/chil/2026.jsonl.zst) |
| 期刊 | PLOS Medicine | — | — | — | — | [175](https://cloud.apaper.ai/v1/conferences/packs/plos_medicine/2026.jsonl.zst) |
| 期刊 | PLOS Global Public Health | — | — | — | — | [817](https://cloud.apaper.ai/v1/conferences/packs/plos_global_public_health/2026.jsonl.zst) |

### 地球与相关环境科学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 期刊 | PLOS Climate | — | — | — | — | [128](https://cloud.apaper.ai/v1/conferences/packs/plos_climate/2026.jsonl.zst) |

### 临床医学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 期刊 | PLOS Medicine | — | — | — | — | [175](https://cloud.apaper.ai/v1/conferences/packs/plos_medicine/2026.jsonl.zst) |

### 法学

| 类型 | 来源 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 期刊 | German Law Journal | — | — | — | — | [57](https://cloud.apaper.ai/v1/conferences/packs/glj/2026.jsonl.zst) |
| 期刊 | Journal of Law and the Biosciences | — | — | — | — | [10](https://cloud.apaper.ai/v1/conferences/packs/jlb/2026.jsonl.zst)（部分） |

数字链接可下载数据包；“部分”表示覆盖不完整，“已编目／已预告”表示尚无数据包；“—”表示 Manifest 未列出该年份。期刊 2026 年数据为 2026-01-01 至 2026-10-14 的快照，不代表全年。数量、状态及可用性以 Manifest 为准。

App 使用版本信息与校验值检测文献目录变化并验证下载的数据包。模型策略只包含公开配置，不存储账户凭据或 API 密钥。

发布流程与渠道约定见[应用分发说明](APP-DISTRIBUTION.md)。本地可运行仓库中的目录校验器和测试检查公开资源。
