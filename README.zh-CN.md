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

App 使用版本信息与校验值检测文献目录变化并验证下载的数据包。模型策略只包含公开配置，不存储账户凭据或 API 密钥。

发布流程与渠道约定见[应用分发说明](APP-DISTRIBUTION.md)。本地可运行仓库中的目录校验器和测试检查公开资源。
