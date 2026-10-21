# Sony BRAVIA 优化结果

日期：2026-10-21。设备为 BRAVIA 4K UR3，中国版 Android 10、MT5893 平台。

## 结果

| 指标 | 初始状态 | 优化完成后 |
| --- | --- | --- |
| `/data` 使用率 | 90% | 62% |
| `/data` 可用空间 | 699,668 KiB，约 0.67 GiB | 2,471,500 KiB，约 2.36 GiB |
| 默认主页 | 原 Sony 桌面 | FLauncher |
| 窗口、过渡、Animator 动画 | 1.0、1.0、未显式设置 | 均为 0.5 |
| 遥控导航及 Home 返回 | 用户反馈明显卡顿 | 用户确认“明显顺畅了” |

存储数据取自初始和关机前的实际采样。性能结论包含运行状态检查和用户体验反馈；没有进行受控的帧率或启动耗时基准测试。

## 配置与应用状态

| 项目 | 包标识 | 完成后的状态 |
| --- | --- | --- |
| 新桌面 | `me.efesser.flauncher` | 默认主页为 `.MainActivity`，重启后保持有效 |
| 原桌面 | `com.dangbei.TVHomeLauncher` | `disabled-user`，原 APK 保留 |
| NewTV 极光 | `com.ktcp.tvvideo` | 用户 0 下 `installed=false`、`enabled=3`；更新包和本地数据已清理 |
| 索尼应用中心 | `com.sony.dangbeimarket` | `disabled-user`，阻止强制回装 NewTV |
| 云视听极光 | `com.ktcp.video` | 从[官方站点](https://tv.qq.com/)重装 20.2.0.1023，桌面入口已恢复 |

NewTV 与云视听极光是两个不同的包。用户最初指定云视听极光，执行卸载后更正为 NewTV，因此随后重装了云视听极光。首次卸载已经删除其本地数据，重装无法恢复原登录状态和本地记录。

NewTV 的出厂 APK 位于 `/system/regional-priv-app/cn1/TencentVideo`，仍保留在只读固件中。最终状态为当前用户卸载并停用。

## 回装问题与处理

第一次卸载 NewTV 后，索尼应用中心重新安装更新包，并恢复应用的启用状态。应用中心更新到 3.0.0 后，即使其自动更新设置显示关闭，启动应用中心仍会回装 NewTV。

最终停用索尼应用中心，再次移除 NewTV 更新包，完成用户卸载、停用和应用专属外部目录清理。索尼应用中心因此暂停安装与更新功能；其 APK 和数据保留在设备上。

## 验证

- 多次重启后，FLauncher 仍为默认主页，原桌面未在后台运行。
- 原生系统设置和输入源菜单可用。
- 最后一次重启后，NewTV 保持当前用户卸载、停用状态，用户数据 inode 为 0，进程和应用专属外部目录均未发现。
- 索尼应用中心保持停用，普通启动入口无法解析，后台进程未运行。
- 云视听极光安装包、可启动 Activity 和桌面入口均已核对。重装后的账户登录和内容播放未验证。
- 用户随后明确反馈方向键导航及 Home 返回“明显顺畅了”。
- 结束时发送正常电视休眠按键，Sony 电源接口返回 `standby`，Android 状态为 `Asleep`，屏幕为 `OFF`。随后断开本次 ADB 连接。

## 恢复原桌面

电视开机并授权连接后，设置 `SONY_TV_TARGET`，运行：

```sh
python3 sony-tv-diagnostics/restore_original_home.py
```

脚本先确认设备厂商为 Sony，再启用原桌面并恢复默认 Home。原桌面 Activity：

```text
com.dangbei.TVHomeLauncher/com.dangbei.leard.leradlauncher.ui.sony.main.MainActivity
```

## 恢复动画设置

原窗口和过渡动画为 1.0，Animator 设置原本不存在：

```sh
adb -s "$SONY_TV_TARGET" shell settings put global window_animation_scale 1.0
adb -s "$SONY_TV_TARGET" shell settings put global transition_animation_scale 1.0
adb -s "$SONY_TV_TARGET" shell settings delete global animator_duration_scale
```

## 恢复索尼应用中心

```sh
adb -s "$SONY_TV_TARGET" shell pm enable --user 0 com.sony.dangbeimarket
```

重新启用或启动索尼应用中心可能再次安装 NewTV。FLauncher 中隐藏的应用中心入口可通过设置中的应用管理恢复显示。
