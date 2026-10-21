# Obsidian 配置备份说明

本目录存放**因状态混杂而无法直接入库**的插件配置留档。

## cross-player-settings.json

**背景**：cross-player 插件把「配置」和「运行时状态」混写在同一个
`data.json` 里，Git 无法只提交其中一部分。

- **已丢弃的状态字段**：`queue`（播放队列，含 position / duration /
  playbackUpdatedAt 等播放进度）、`playbackSpeed`、`consumptionStats`、
  `deletedPaths`、`queueScrollTop`、`queueUpdatedAt`。
  这些每看一个视频就变一次，且入库存的是本地绝对路径，跨机器无意义。
- **保留的配置**：原 `settings` 段（监控目录、播放倍速预设、跳转秒数、
  工具路径等），见 `cross-player-settings.json`。

**换机还原方法**：把该文件的内容拷贝到新机器的
`.obsidian/plugins/cross-player/data.json`，然后在插件里开启一次，
让插件自己补齐其余默认字段即可。