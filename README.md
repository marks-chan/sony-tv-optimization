# Sony TV 优化记录与诊断工具

记录一次 Sony BRAVIA Android TV 的桌面响应优化，保留诊断、界面检查和恢复原桌面的 Python 工具。

2026-10-21 完成优化：存储占用从 90% 降至 62%，用户确认方向键导航和 Home 返回“明显顺畅了”。重启验证通过，随后按用户要求关闭电视，确认进入待机且屏幕关闭。

## 已完成的调整

- 回收系统管理的缓存，可用存储从约 0.67 GiB 增至 2.36 GiB。
- 使用 FLauncher 作为默认桌面，关闭其图标高亮动画；系统三项动画倍率设为 0.5。
- 停用原桌面 `com.dangbei.TVHomeLauncher`，避免它在后台重新启动。
- 清理 NewTV 极光 `com.ktcp.tvvideo` 的更新包和本地数据，在用户 0 下卸载并停用。只读固件中的出厂 APK 保留。
- 停用会强制回装 NewTV 的索尼应用中心 `com.sony.dangbeimarket`，并隐藏其失效的桌面入口。索尼应用中心的安装和更新功能因此暂停。
- 根据用户更正，重新安装云视听极光 `com.ktcp.video` 并恢复桌面入口。之前删除的本地数据无法恢复，可能需要重新登录。

详细结果及验证范围见 [优化报告](docs/optimization-report.md)。

## 文件

| 文件 | 用途 |
| --- | --- |
| `sony-tv-diagnostics/collect_tv.py` | 读取 Sony 电视的存储、内存、进程、默认桌面和动画设置，生成本地 JSON 快照 |
| `sony-tv-diagnostics/tv_ui.py` | 通过 ADB 检查界面树、按键、点击和截图的辅助函数 |
| `sony-tv-diagnostics/restore_original_home.py` | 启用原 Sony 桌面并将其恢复为默认主页 |
| `docs/optimization-report.md` | 优化结果、应用包标识、验证与恢复说明 |

## 使用工具

需要 Python 3 和 [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)。工具仅使用 Python 标准库。

电视开机并完成 ADB 授权后，设置目标地址。将 `TV_IP` 替换为实际电视地址：

```sh
export SONY_TV_TARGET="TV_IP:5555"
adb connect "$SONY_TV_TARGET"
python3 sony-tv-diagnostics/collect_tv.py inspection
```

快照保存在 `sony-tv-diagnostics/inspection.json`，同名快照不会被覆盖。未设置 `SONY_TV_TARGET` 时，脚本会退出，避免连接到预设设备。

恢复原桌面：

```sh
python3 sony-tv-diagnostics/restore_original_home.py
```

该脚本恢复原主页；已删除的应用数据需要另行处理。恢复索尼应用中心可能再次自动安装 NewTV，具体恢复命令和影响见优化报告。

## 本地诊断资料

设备地址通过环境变量传入。调试凭据、原始日志、设备快照、界面树、截图和下载的 APK 均留在本机，并由 `.gitignore` 排除。

本仓库没有会自动批量卸载应用或修改电视固件的脚本。

## FLauncher 来源

本次使用 [osrosal/flauncher](https://github.com/osrosal/flauncher) 的 [v2025.07.001 发布包](https://github.com/osrosal/flauncher/releases/tag/v2025.07.001)，选择 `armeabi-v7a` 架构。下载后已将 SHA-256 与发布元数据核对一致：

```text
467fd0befe6daa3993a8a34a3981a631858ace28b38d9836d691478af8b71e40
```

仓库保留来源与校验记录；APK 保存在本机。
