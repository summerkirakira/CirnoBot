

<h1 align="center">CirnoBot</h1>

### 琪露诺Bot

---
专注Minecraft (加点亿点点娱乐实用功能）的QQ机器人，基于nonebot2, gocqhttp, serverTap开发的琪露诺家族的第三代成员。

### 实现功能

---
+ Minecraft相关
  + 服务端版本支持Bukkit, Spigot&PaperMC 1.12-1.18.1
  + 多服务器同时监听支持
  + 分群服务器绑定支持
  + 分服务器超级用户支持
  + 入服离服事件QQ群播报
  + 入服离服事件MC服务器播报
  + 玩家聊天消息监听，支持自定词条自动回复（mc骰娘已移植）
  + 所有广播/私聊消息均可支持颜色代码与PlaceholderAPI
  + MC服务器在线信息查询（内存占用，版本，在线玩家）
  + 获取服务器启用插件列表
  + 在线/离线玩家信息查询
  + 开启/关闭服务器白名单
  + 添加/移除服务器管理员
  + MC玩家ID绑定QQ号
  + 群成员自助申请白名单
  + 服务器向QQ群 / QQ群向服务器转发消息
  + 查询服务器最近10条玩家消息
  + 在QQ群执行MC指令
  + MC词条库
+ 其他功能&特性
  + 支持图片文本的群词条库支持(图片缓存到本地)
  + 在群聊中动态编辑词条
  + 支持群成员专属词条
  + 分群启用不同的词条库
  + 词条库由sqlite存储，无需开启my_sql服务
  + 美元/港币/日元...阿联酋迪拉姆... 货币转换支持
  + 开黑啦在线成员/语音频道查询支持
  + 完整的功能帮助

### 实现截图

---



### 简单部署

---
1.下载CirnoBot本体
```shell
git clone https://github.com/summerkirakira/CirnoBot.git # 下载CirnoBot文件
```
2.安装CirnoBot依赖(**强烈建议**使用你喜欢的 Python 环境管理工具创建新的虚拟环境)
```shell
pip install pip --upgrade # 更新pip

pip install -r requirements.txt # 安装python依赖
```
3. 启动CirnoBot！
```shell
nb run # 启动bot！
```
