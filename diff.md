![logo-blue](https://user-images.githubusercontent.com/51039935/197520391-f35db354-6071-4c12-86ea-fc450f04bc85.png)
# NAS媒体库管理工具


[![GitHub stars](https://img.shields.io/github/stars/0xforee/nas-tools?style=plastic)](https://github.com/0xforee/nas-tools/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/0xforee/nas-tools?style=plastic)](https://github.com/0xforee/nas-tools/network/members)
[![GitHub issues](https://img.shields.io/github/issues/0xforee/nas-tools?style=plastic)](https://github.com/0xforee/nas-tools/issues)
[![GitHub license](https://img.shields.io/github/license/0xforee/nas-tools?style=plastic)](https://github.com/0xforee/nas-tools/blob/master/LICENSE.md)
[![Docker pulls](https://img.shields.io/docker/pulls/0xforee/nas-tools?style=plastic)](https://hub.docker.com/r/0xforee/nas-tools)
[![Platform](https://img.shields.io/badge/platform-amd64/arm64-pink?style=plastic)](https://hub.docker.com/r/0xforee/nas-tools)

Docker：https://hub.docker.com/repository/docker/0xforee/nas-tools

## 基于官方主线版本增强
1. 基于主线最新 3.2.3 版本制作，配置可以完美迁移
1. 取消了用户认证
2. 取消新手刷流限制
1. 刷流增加部分下载能力（拆包），可以灵活配置下载种子的大小和比例，最大化提升刷流效率。（部分站点可能禁止，请慎用！！！）
2. 刷流增加限免限时检测能力，超过限免，自动降速为 1B/s，防止流量偷跑，默认为关。（目前已测试： mteam 和 hdmayi）
3. 刷流界面增加信息展示
   * 增加展示已保种大小
   * 种子明细增加展示种子大小，限免过期时间
3. 保留了 BT 能力和内置 BT 站点，可以继续索引和下载 BT 磁链和种子文件
4. 支持 jackett 和 prowlarr 索引器
   * 可以通过插件和内置索引器同时使用
5. 一些入口增加快捷跳转能力，方便将 nastools 作为媒体管理主要入口。具体如下：
   * 下载管理-正在下载：增加跳转下载器查看种子详情能力
   * 我的媒体库：增加标题跳转媒体库能力
   * 索引器：jackett 和 prowlarr 增加跳转各服务能力
   * 媒体服务器：每个服务器配置界面增加跳转服务能力
6. 支持 Mteam 新架构
   * 站点配置中配置 api-key 即可
     * api-key 从馒头-控制台-实验室-存取令牌 生成获取
   * 完美支持站点签到
     * 可从控制台登陆设备活动记录中查询到签到（登陆）记录
