---
title: Cisco Modeling Labs 官方 UI 截图集（索引）
category: 业界分析 / 素材收集
source: Cisco DevNet · Cisco Modeling Labs v2.10 官方文档
created: 2026-10-22
tags:
  - CML
  - UI截图
  - 官方素材
---

# Cisco Modeling Labs 官方 UI 截图集（索引）

> **用途**：用于产品对标、界面参考、内部汇报配图。全部图片取自 **Cisco DevNet 官方文档站**的文档原图（非二次截屏、非缩放版本），按文档章节命名归档。
> **版权提示**：图片版权归 Cisco 所有，随官方文档发布。本目录仅供**内部研究参考**，不得用于对外宣传物料、不得二次分发或商用；对外引用请改为文字描述并注明文档出处。

## 采集说明

| 项目 | 内容 |
| --- | --- |
| 采集日期 | 2026-10-22 |
| 文档版本 | Cisco Modeling Labs v2.10（含 2.9 引入的权限与智能标注能力） |
| 文档总入口 | https://developer.cisco.com/docs/modeling-labs/vm-images-for-cml-labs/ |
| 文档内容源 | `https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/`（DevNet 文档站实际加载的 Sphinx 构建产物） |
| 遍历范围 | 文档树 `ui/` 目录下全部 **60 个用户界面章节** |
| 命中结果 | **22 个章节**含配图，去重后 **56 张原始 PNG**（磁盘上 58 个文件中有 2 组同图不同名，见下） |
| 未命中说明 | 其余 38 个章节为纯文字说明（操作步骤、字段解释），官方未配图 |
| 文件命名规则 | `<章节路径>__<原始文件名>.png`，可直接反查出处 |

> **为什么能取到原图**：`developer.cisco.com` 的文档页是前端渲染壳（首屏 HTML 里没有 `<img>`），正文与图片由 `pubhub.devnetcloud.com` 的 Sphinx 站点提供。直接取 `_images/` 目录，拿到的是文档原始 PNG，而不是页面上的缩放版本。

> **重复文件说明**：`ui_menu-bar_menu_intro__cml_menu_tools.png` 与 `ui_menu-bar_menu_tools__cml_menu_tools.png` 内容相同；`ui_pcap_pcap_intro__pcap_details.png` 与 `ui_pcap_pcap_running__pcap_details.png` 内容相同。同图被两个章节引用，故各保留两份。

## 一、核心界面（嵌图预览）

### Dashboard

![[ui_dashboard_dashboard_list_view__virl2_lab_manager_list_view.png]]

> Dashboard：Lab 列表视图，右上角 ADD / IMPORT，底部 CPU / MEMORY / DISK 资源条。

### Workbench

![[ui_workbench__virl2_workbench_actions.png]]

> Workbench：拓扑画布 + 顶部工具栏 + 右侧 SETTINGS / CONNECTIVITY / CONFIG / INTERFACES 面板，含 STOP / WIPE / CLONE / DELETE 与 OPEN CONSOLE。

### 链路抓包面板

![[ui_pcap_pcap_running__pcap_start.png]]

> 链路抓包面板：START / CLEAR / DOWNLOAD / SETTINGS，以及 No. / Time / Source / Destination / Protocol / Length / Info 列表。

### Dashboard 总览

![[ui_overview_overview_intro__ui_overview.png]]

> Dashboard 总览：Lab 磁贴卡片、运行/停止/擦除图标与资源占用条。

## 二、完整清单（按模块分组）


### 仪表盘与 Lab 列表

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_dashboard_dashboard_intro__virl2_lab_manager_list_view_previews.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/dashboard/dashboard_intro.html) |
| 2 | [[ui_dashboard_dashboard_list_view__virl2_lab_manager_list_multi-select.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/dashboard/dashboard_list_view.html) |
| 3 | [[ui_dashboard_dashboard_list_view__virl2_lab_manager_list_view.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/dashboard/dashboard_list_view.html) |
| 4 | [[ui_dashboard_sample_labs__sample-labs-import.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/dashboard/sample_labs.html) |

### 工作台工具栏

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_workbench__virl2_workbench_actions.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/workbench.html) |

### Lab 启停与擦除

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_lab_delete__virl2_lab_manager_start_stop_wipe.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_delete.html) |

### 节点启停与擦除

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_node_actions__virl2_workbench_start_stop_wipe.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/node_actions.html) |

### 节点配置

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_node_config__node_config.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/node_config.html) |

### 节点资源限制

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_cpu_limit_on_node__virl2_node_cpu_limit.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/cpu_limit_on_node.html) |

### 节点分级启动

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_node_staging_node_staging__01-NS_menu-item.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/node_staging/node_staging.html) |
| 2 | [[ui_node_staging_node_staging__02-NS_popup-dialog.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/node_staging/node_staging.html) |
| 3 | [[ui_node_staging_node_staging__03-NS_priority-setting.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/node_staging/node_staging.html) |

### 接口与连线

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_interface_add__virl2_workbench_add_link-4.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/interface_add.html) |

### 接口 MAC 分配

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_interface_mac_assign__interface_mac.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/interface_mac_assign.html) |

### 链路创建

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_link_create__virl2_workbench_add_link-1a.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_create.html) |
| 2 | [[ui_link_create__virl2_workbench_add_link-1b.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_create.html) |
| 3 | [[ui_link_create__virl2_workbench_add_link-3.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_create.html) |

### 链路隐藏与捆绑

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_link_hide__cml2_hiding_links_hide.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_hide.html) |
| 2 | [[ui_link_hide__cml2_hiding_links_show.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_hide.html) |
| 3 | [[ui_link_hide__cml2_link_bundling_off.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_hide.html) |
| 4 | [[ui_link_hide__cml2_link_bundling_on.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_hide.html) |

### 链路条件

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_link_conditioning_link_conditioning_intro__link_conditioning_page.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/link_conditioning/link_conditioning_intro.html) |

### 控制台

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_consoles_console_web_open__virl2_workbench_access_console.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/consoles/console_web_open.html) |

### 链路抓包

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_pcap_pcap_intro__pcap_details.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/pcap/pcap_intro.html) |
| 2 | [[ui_pcap_pcap_running__pcap_start.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/pcap/pcap_running.html) |

### 仿真统计与磁盘占用

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_simulation_statistics__node_disk_usage_in_nodes_pane.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/simulation_statistics.html) |
| 2 | [[ui_simulation_statistics__node_disk_usage_in_sim_stats.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/simulation_statistics.html) |

### 标注

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_annotations_annotations_overview__annotations_example.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/annotations/annotations_overview.html) |
| 2 | [[ui_annotations_annotations_overview__annotations_toolbar.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/annotations/annotations_overview.html) |

### 智能标注

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_smart_annotations_smart_annotations_bulk_edit__smart_annotations_bulk_1.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_bulk_edit.html) |
| 2 | [[ui_smart_annotations_smart_annotations_bulk_edit__smart_annotations_bulk_2.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_bulk_edit.html) |
| 3 | [[ui_smart_annotations_smart_annotations_bulk_edit__smart_annotations_bulk_3.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_bulk_edit.html) |
| 4 | [[ui_smart_annotations_smart_annotations_create__smart_annotations_create.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_create.html) |
| 5 | [[ui_smart_annotations_smart_annotations_disable__smart_annotations_disable_1.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_disable.html) |
| 6 | [[ui_smart_annotations_smart_annotations_disable__smart_annotations_disable_2.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_disable.html) |
| 7 | [[ui_smart_annotations_smart_annotations_edit__smart_annotations_config_distance.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_edit.html) |
| 8 | [[ui_smart_annotations_smart_annotations_edit__smart_annotations_config_grp_by_lnk.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_edit.html) |
| 9 | [[ui_smart_annotations_smart_annotations_edit__smart_annotations_config_label.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_edit.html) |
| 10 | [[ui_smart_annotations_smart_annotations_edit__smart_annotations_config_padding.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_edit.html) |
| 11 | [[ui_smart_annotations_smart_annotations_edit__smart_annotations_config_zindex.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_edit.html) |
| 12 | [[ui_smart_annotations_smart_annotations_hide__smart_annotations_hide_1.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_hide.html) |
| 13 | [[ui_smart_annotations_smart_annotations_hide__smart_annotations_hide_2.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_hide.html) |
| 14 | [[ui_smart_annotations_smart_annotations_in_practice__smart_annotations_exclusions.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_in_practice.html) |
| 15 | [[ui_smart_annotations_smart_annotations_overview__smart_annotations_example.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/smart_annotations/smart_annotations_overview.html) |

### Lab 共享与权限

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_lab_sharing__agp_add_permissions.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 2 | [[ui_lab_sharing__agp_lab_limited.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 3 | [[ui_lab_sharing__agp_lab_list_limited.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 4 | [[ui_lab_sharing__agp_label_full.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 5 | [[ui_lab_sharing__agp_label_limited.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 6 | [[ui_lab_sharing__agp_label_owner.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 7 | [[ui_lab_sharing__agp_permissions.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |
| 8 | [[ui_lab_sharing__agp_save_permissions.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/lab_sharing.html) |

### 菜单栏

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_menu-bar_menu_intro__cml_menu_tools.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/menu-bar/menu_intro.html) |
| 2 | [[ui_menu-bar_menu_user__cml_menu_user.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/menu-bar/menu_user.html) |

### ui/overview/overview_intro

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_overview_overview_intro__ui_overview.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/overview/overview_intro.html) |

### ui/resource_limits/rsrc_limits_view

| # | 截图文件（点击打开） | 官方文档页 |
| --- | --- | --- |
| 1 | [[ui_resource_limits_rsrc_limits_view__tools_rsrc_limits.png]] | [打开](https://pubhub.devnetcloud.com/media/cisco-modeling-labs-2-10/docs/guides/_build/html/ui/resource_limits/rsrc_limits_view.html) |

## 三、按功能域对照

| 功能域 | 可用截图 | 对应报告章节 |
| --- | --- | --- |
| 拓扑建模与资产管理 | Dashboard、Workbench、新建 Lab、示例实验导入、链路创建与隐藏 | 2 章 F1 |
| 节点运行与镜像 | 节点配置、节点启停/擦除、节点 CPU 限制、节点分级启动、仿真统计与磁盘占用 | 3 章 F2 |
| 交互与取证 | 控制台、链路抓包、链路条件、标注与智能标注 | 4 章 F3 |
| 外部互通 | 官方 `ui/ext_conn/` 三页无配图（见第四节） | 5 章 F4 |
| 自动化与 AI | Tools 菜单、用户菜单（API 文档与 MCP 客户端入口位于其中） | 6 章 F5 |
| 协作与治理 | Lab 共享权限、权限标签、资源限制 | 7 章 F6 |

## 四、缺口与后续

| 缺口 | 现状 | 补法 |
| --- | --- | --- |
| 外部连接器（ext-conn）配图 | 官方 `ui/ext_conn/` 三页均为文字，无图 | 自建环境后自截，或引用 2.0 版用户指南的旧版示意图 |
| MCP 客户端配置页 | 官方 MCP 文档为文字说明，无界面图 | 在 2.10 环境实测截取 |
| ISE / 9800-CL 节点界面 | 属节点镜像能力，不在 `ui/` 章节内 | 需自建 lab 后截取 |

*采集时间：2026-10-22 ｜ 来源：Cisco DevNet 官方文档 v2.10 ｜ 图片版权归 Cisco*
