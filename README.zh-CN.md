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

当前稳定发布：暂无经过核验的可用更新。

## 文献包列表

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

App 使用版本信息与校验值检测文献目录变化并验证下载的数据包。模型策略只包含公开配置，不存储账户凭据或 API 密钥。

发布流程与渠道约定见[应用分发说明](APP-DISTRIBUTION.md)。本地可运行仓库中的目录校验器和测试检查公开资源。
