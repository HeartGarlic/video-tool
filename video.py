import os
import random
import sys
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog,
    QLabel, QVBoxLayout, QProgressBar, QMessageBox, QCheckBox, QComboBox, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QMutex, pyqtSignal, QObject
import ctypes

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

class VideoBatchTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频批处理工具：贴图覆盖+背景音乐")
        self.resize(600, 500)

        self.video_folder = "./videos"
        self.output_folder = "./output"
        self.image_path = "./overlay_gif.gif"
        self.music_path = ""
        self.music_folder = ""
        self.random_music = False
        self.keep_original_audio = True
        self.audio_volume = 1.0
        self.use_gpu = True
        self.ffmpeg_path = "./ffmpeg.exe" if os.name == 'nt' else "./ffmpeg"
        self.signals = WorkerSignals()

        print("初始化配置:")
        print(f"视频目录: {self.video_folder}, 输出目录: {self.output_folder}")
        print(f"贴图路径: {self.image_path}, 音乐路径: {self.music_path}, 随机音乐文件夹: {self.music_folder}")
        print(f"FFmpeg 路径: {self.ffmpeg_path}")

        self.init_ui()
        self.check_environment()

    def check_environment(self):
        print("检查环境中...")
        if not os.path.isfile(self.ffmpeg_path):
            QMessageBox.critical(self, "环境错误", f"未找到 FFmpeg 可执行文件: {self.ffmpeg_path}")
            sys.exit(1)

        try:
            subprocess.run([self.ffmpeg_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print("FFmpeg 执行失败:", e)
            QMessageBox.critical(self, "环境错误", "FFmpeg 执行失败，请确认路径和兼容性。")
            sys.exit(1)

        if os.name == 'nt':
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    QMessageBox.information(self, "权限提示", "建议以管理员权限运行该程序以确保功能正常。")
            except Exception:
                pass

    def init_ui(self):
        layout = QVBoxLayout()

        self.folder_label = QLabel(f"视频文件夹: {self.video_folder}")
        self.output_label = QLabel(f"输出文件夹: {self.output_folder}")
        self.image_label = QLabel(f"贴图: {self.image_path}")
        self.music_label = QLabel(f"音乐: {self.music_path}")
        self.music_folder_label = QLabel(f"音乐文件夹: {self.music_folder}")
        self.ffmpeg_label = QLabel(f"FFmpeg 路径: {self.ffmpeg_path}")

        btn_folder = QPushButton("选择视频文件夹")
        btn_folder.clicked.connect(self.select_folder)

        btn_output = QPushButton("选择输出文件夹")
        btn_output.clicked.connect(self.select_output_folder)

        btn_image = QPushButton("选择贴图图片/GIF")
        btn_image.clicked.connect(self.select_image)

        btn_music = QPushButton("选择背景音乐（可选）")
        btn_music.clicked.connect(self.select_music)

        btn_music_folder = QPushButton("选择音乐文件夹（随机）")
        btn_music_folder.clicked.connect(self.select_music_folder)

        self.random_music_checkbox = QCheckBox("使用随机音乐")
        self.random_music_checkbox.stateChanged.connect(self.toggle_random_music)

        self.original_audio_checkbox = QCheckBox("保留原视频声音")
        self.original_audio_checkbox.setChecked(True)
        self.original_audio_checkbox.stateChanged.connect(lambda state: setattr(self, 'keep_original_audio', state == Qt.Checked))

        self.gpu_checkbox = QCheckBox("启用GPU加速")
        self.gpu_checkbox.setChecked(True)
        self.gpu_checkbox.stateChanged.connect(lambda state: setattr(self, 'use_gpu', state == Qt.Checked))

        self.volume_input = QLineEdit("1.0")
        self.volume_input.setPlaceholderText("背景音乐音量 (默认1.0)")
        self.volume_input.textChanged.connect(self.set_volume)

        self.ffmpeg_input = QLineEdit(self.ffmpeg_path)
        self.ffmpeg_input.setPlaceholderText("FFmpeg 可执行文件路径")
        self.ffmpeg_input.textChanged.connect(lambda text: setattr(self, 'ffmpeg_path', text.strip()))

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("状态：等待开始处理")

        btn_process = QPushButton("开始处理")
        btn_process.clicked.connect(self.start_processing_thread)

        layout.addWidget(self.folder_label)
        layout.addWidget(btn_folder)
        layout.addWidget(self.output_label)
        layout.addWidget(btn_output)
        layout.addWidget(self.image_label)
        layout.addWidget(btn_image)
        layout.addWidget(self.music_label)
        layout.addWidget(btn_music)
        layout.addWidget(self.music_folder_label)
        layout.addWidget(btn_music_folder)
        layout.addWidget(self.random_music_checkbox)
        layout.addWidget(self.original_audio_checkbox)
        layout.addWidget(self.gpu_checkbox)
        layout.addWidget(QLabel("背景音乐音量 (0.0 ~ 10.0):"))
        layout.addWidget(self.volume_input)
        layout.addWidget(QLabel("FFmpeg 路径:"))
        layout.addWidget(self.ffmpeg_input)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        layout.addWidget(btn_process)

        self.setLayout(layout)

        self.signals.progress.connect(self.progress.setValue)
        self.signals.finished.connect(lambda: (self.status_label.setText("处理完成！"), QMessageBox.information(self, "完成", "所有视频已处理完毕。")))

    def start_processing_thread(self):
        threading.Thread(target=self.process_all, daemon=True).start()

    def set_volume(self, value):
        try:
            self.audio_volume = float(value)
        except ValueError:
            self.audio_volume = 1.0

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择视频文件夹")
        if folder:
            self.video_folder = folder
            self.folder_label.setText(f"视频文件夹: {folder}")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_label.setText(f"输出文件夹: {folder}")

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择贴图", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if path:
            self.image_path = path
            self.image_label.setText(f"贴图: {path}")

    def select_music(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择背景音乐", "", "Audio (*.mp3 *.wav *.aac *.flac)")
        if path:
            self.music_path = path
            self.music_label.setText(f"音乐: {path}")

    def select_music_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择背景音乐文件夹")
        if folder:
            self.music_folder = folder
            self.music_folder_label.setText(f"音乐文件夹: {folder}")

    def toggle_random_music(self, state):
        self.random_music = state == Qt.Checked

    def get_random_music(self):
        if not self.music_folder:
            return None
        candidates = [os.path.join(self.music_folder, f) for f in os.listdir(self.music_folder) if f.endswith(('.mp3', '.wav', '.aac', '.flac'))]
        return random.choice(candidates) if candidates else None

    def process_all(self):
        if not self.video_folder or not self.image_path or not self.output_folder:
            QMessageBox.warning(self, "缺少信息", "请确保选择了视频文件夹、输出文件夹和贴图图片。")
            return

        videos = [f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
        if not videos:
            QMessageBox.information(self, "没有视频", "文件夹中未找到视频文件。")
            return

        self.progress.setMaximum(len(videos))
        self.progress.setValue(0)

        def process_and_update(index, video):
            try:
                self.process_single_video(video)
            except Exception as e:
                print(f"处理失败: {video} 错误: {e}")
            self.signals.progress.emit(index + 1)

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for idx, video in enumerate(videos):
                executor.submit(process_and_update, idx, video)

        self.signals.finished.emit()

    def process_single_video(self, filename):
        input_path = os.path.join(self.video_folder, filename)
        rand_prefix = str(random.randint(10000, 99999))
        output_path = os.path.join(self.output_folder, f"{rand_prefix}_processed_{filename}")
        music_file = self.get_random_music() if self.random_music else self.music_path

        if not os.path.isfile(self.ffmpeg_path):
            raise FileNotFoundError(f"FFmpeg 可执行文件未找到: {self.ffmpeg_path}")

        cmd = [self.ffmpeg_path, "-y", "-i", input_path]

        image_ext = os.path.splitext(self.image_path)[1].lower()
        if image_ext == ".gif":
            cmd += ["-ignore_loop", "0", "-i", self.image_path]
        else:
            cmd += ["-loop", "1", "-t", "9999", "-i", self.image_path]

        filter_complex = "[0:v][1:v] overlay=0:0:shortest=1[vout]"
        audio_inputs = []

        if music_file:
            cmd += ["-i", music_file]
            audio_inputs.append(f"[2:a]volume={self.audio_volume}[bgm]")

        if self.keep_original_audio and music_file:
            audio_inputs.append("[0:a][bgm]amix=inputs=2:duration=first[aout]")
            filter_complex += ";" + ";".join(audio_inputs)
            cmd += ["-filter_complex", filter_complex, "-map", "[vout]", "-map", "[aout]"]
        elif music_file:
            filter_complex += ";" + ";".join(audio_inputs)
            cmd += ["-filter_complex", filter_complex, "-map", "[vout]", "-map", "[bgm]"]
        else:
            cmd += ["-filter_complex", filter_complex, "-map", "[vout]"]

        if self.use_gpu:
            cmd += ["-c:v", "h264_nvenc"]
        else:
            cmd += ["-c:v", "libx264"]

        cmd += ["-shortest", output_path]

        si = None
        creationflags = 0
        if os.name == 'nt':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si, creationflags=creationflags)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print("FFmpeg 错误输出:\n", stderr.decode())

if __name__ == "__main__":
    print("启动应用...")
    app = QApplication(sys.argv)
    window = VideoBatchTool()
    window.show()
    sys.exit(app.exec_())
