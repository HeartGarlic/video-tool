# video-tool

"video-tool" 用于批量给视频添加覆盖图片/GIF 并可选择加入背景音乐。界面基于 PyQt5 实现，处理过程调用 FFmpeg 完成。

## 安装依赖
1. 安装 Python 3.8 及以上版本。
2. 安装 FFmpeg，并确认 `ffmpeg` 可执行文件在系统环境变量或 `video.py` 指定路径。
3. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法
1. 将待处理的视频放入 `videos/` 目录，或在启动后通过界面选择其他目录。
2. 执行 `make run` 启动图形界面。
3. 在界面中依次选择输出目录、覆盖图片(GIF)及背景音乐（可选），点击“开始处理”即可批量生成视频。

## Makefile 目标
本仓库提供了简单的 `Makefile` 方便常用操作：

| 命令           | 说明                                       |
| -------------- | ------------------------------------------ |
| `make run`     | 运行 `video.py` 启动程序                   |
| `make freeze`  | 生成当前环境的 `requirements.txt` 文件     |
| `make package` | 使用 PyInstaller 打包成可执行文件           |
| `make clean`   | 清理构建产物 (`build/`, `dist/`, `*.spec` 等) |

打包完成后，可执行文件位于 `dist/` 目录，Windows 平台下扩展名为 `.exe`。

## 生成依赖文件
运行 `make freeze` 会将当前 Python 环境的依赖写入 `requirements.txt`，便于在其它环境中复现。

## 许可证

本项目遵循 MIT License，详见 [LICENSE](LICENSE)。
