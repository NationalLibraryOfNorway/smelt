import glob
import re
import subprocess
import sys
import os
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def create_file_selection_box(text, buttons):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Flere filtyper funnet")
    msg.setText(text)
    for button in buttons:
        msg.addButton(button, QMessageBox.ActionRole)
    msg.addButton(QMessageBox.Cancel)
    return msg


def select_file_from_list(files, file_type_description):
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter(f"{file_type_description} Files (*.{file_type_description})")
    dialog.setViewMode(QFileDialog.Detail)
    dialog.setDirectory(os.path.dirname(files[0]))

    if dialog.exec_():
        selected_file = dialog.selectedFiles()[0]
        return selected_file
    return None


def extract_number(filename):
    base = os.path.basename(filename)
    match = re.search(r'(\d+)', base)
    return int(match.group(1)) if match else float('inf')


class Smelt(QWidget):
    def __init__(self):
        super().__init__()

        self.images_path = None
        self.proceed_prores = None
        self.proceed_lossless = None
        self.proceed_h264 = None
        self.h264_mp4 = None
        self.prores_mov = None
        self.lossless_mov = None
        self.audio_file = None
        self.folder_name = None
        self.fps = None
        self.selected_files = None
        self.video = None
        self.audio_file_path = None
        self.folder_path = None
        self.film_file_path = None

        self.filLabel = None
        self.mappeLabel = None
        self.fpsLabel = None
        self.inkluderLydCheckBox = None
        self.inkluderProresCheckBox = None
        self.kunLydCheckBox = None
        self.mezzaninfilCheckBox = None
        self.mappeButton = None
        self.filmButton = None
        self.filButton = None
        self.execButton = None
        self.fpsCounter = None
        self.output_text = None
        self.progress_bar = None
        self.dialog = QFileDialog()
        self.mappe_input_field = None
        self.fil_input_field = None

        self.initUI()

    def initUI(self):
        self.create_labels()
        self.create_checkboxes()
        self.create_buttons()
        self.create_text_output()
        self.create_combobox()
        self.create_progressbar()
        self.setup_layout()
        self.set_default_states()
        self.designate_button_methods()
        self.set_styling()

    def create_labels(self):
        self.filLabel = QLabel('Lydfil:', self)
        self.mappeLabel = QLabel('Mappe/fil:', self)
        self.fpsLabel = QLabel('FPS:', self)

    def create_checkboxes(self):
        self.inkluderLydCheckBox = QCheckBox('Lyd', self)
        self.inkluderProresCheckBox = QCheckBox('Prores 422 HQ', self)
        self.kunLydCheckBox = QCheckBox('Kun lydfil', self)
        self.mezzaninfilCheckBox = QCheckBox('Mezzaninfil', self)

    def create_buttons(self):
        self.mappeButton = QPushButton('Velg Mappe...', self)
        self.filmButton = QPushButton('Velg fil...')
        self.filButton = QPushButton('Velg lydfil...', self)
        self.execButton = QPushButton('Kjør', self)

    def create_combobox(self):
        self.fpsCounter = QComboBox(self)
        for i in range(1, 61):  # Determines range of the fps options (1-60)
            self.fpsCounter.addItem(str(i))
        self.fpsCounter.setCurrentIndex(23)
        self.fpsCounter.view().parentWidget().setMaximumHeight(200)
        self.fpsCounter.setMaximumSize(50, 30)

    def create_text_output(self):
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setHidden(True)

    def create_progressbar(self):
        self.progress_bar = QProgressBar(self)

    def setup_layout(self):
        self.mappe_input_field = QLineEdit(self)
        self.fil_input_field = QLineEdit(self)

        layout = QGridLayout()
        layout.addWidget(self.mappeLabel, 0, 0)
        layout.addWidget(self.mappe_input_field, 0, 1, 1, 3)
        layout.addWidget(self.mappeButton, 0, 4)
        layout.addWidget(self.filmButton, 4, 4)
        layout.addWidget(self.filLabel, 7, 0)
        layout.addWidget(self.fil_input_field, 7, 1, 1, 3)
        layout.addWidget(self.filButton, 7, 4)
        layout.addWidget(self.inkluderLydCheckBox, 6, 0)
        layout.addWidget(self.inkluderProresCheckBox, 6, 1)
        layout.addWidget(self.kunLydCheckBox, 6, 3)
        layout.addWidget(self.mezzaninfilCheckBox, 6, 2)
        layout.addWidget(self.fpsLabel, 4, 0)
        layout.addWidget(self.fpsCounter, 4, 1)
        layout.addWidget(self.output_text, 12, 0, 1, 5)
        layout.addWidget(self.progress_bar, 10, 0, 1, 4)
        layout.addWidget(self.execButton, 10, 4)
        self.setLayout(layout)

    def set_default_states(self):
        self.inkluderLydCheckBox.setChecked(True)  # Generer Audio
        self.inkluderProresCheckBox.setChecked(True)  # Generer Prores
        self.kunLydCheckBox.setChecked(False)  # Generer KUN lydfil
        self.mezzaninfilCheckBox.setChecked(True)  # Generer Mezzaninfil

    def designate_button_methods(self):
        self.execButton.clicked.connect(self.run_smelt)
        self.kunLydCheckBox.clicked.connect(self.check_box_logic)
        self.filButton.clicked.connect(lambda: self.select_file_or_folder('audio'))
        self.mappeButton.clicked.connect(lambda: self.select_file_or_folder('mappe'))
        self.filmButton.clicked.connect(lambda: self.select_file_or_folder('film'))

    def set_styling(self):
        self.fil_input_field.setStyleSheet("border: 1px solid gray;")
        self.mappe_input_field.setStyleSheet('border: 1px solid gray;')
        self.setStyleSheet("background-color: #2B2B2B; color: white;")
        self.setWindowTitle('SMELT')
        self.resize(550, 200)

    def select_file_or_folder(self, file_type):
        dialog = QFileDialog()
        if file_type == 'mappe':
            folder_path = dialog.getExistingDirectory(None, "Velg Mappe")
            if folder_path:
                self.folder_path = folder_path
                self.mappe_input_field.setText(folder_path)
                self.mappe_sok(folder_path)
        elif file_type == 'film':
            file_filter = 'Movie files (*.mov *.mxf);;All Files (*)'
            file_path, _ = dialog.getOpenFileName(None, 'Velg Filmfil', '', file_filter)
            if file_path:
                self.film_file_path = file_path
                file_name = os.path.basename(file_path)
                self.folder_path = os.path.dirname(file_path)
                self.mappe_input_field.setText(file_name)
        elif file_type == 'audio':
            file_filter = 'Audio Files (*.wav *.mxf);;All Files (*)'
            file_path, _ = dialog.getOpenFileName(None, 'Velg Lydfil', self.folder_path, file_filter)
            if file_path:
                self.audio_file_path = file_path
                file_name = os.path.basename(file_path)
                self.fil_input_field.setText(file_name)
                if not self.folder_path:
                    self.folder_path = os.path.dirname(file_path)
                if re.search(r'\.(R|Rs|C|L|Ls|LFE)\.wav$', file_name):
                    combined_audio_file = self.recognize_and_combine_audio_files(file_path)
                    if combined_audio_file:
                        self.audio_file_path = combined_audio_file
                        self.fil_input_field.setText(os.path.basename(combined_audio_file))

    def recognize_and_combine_audio_files(self, selected_audio_file):
        base_name = re.sub(r'\.[A-Za-z]+\.\w+$', '', os.path.basename(selected_audio_file))
        directory = os.path.dirname(selected_audio_file)

        # Define the possible suffixes and their respective order
        suffixes = {
            'L': 'left',         # Left — Music & Effects
            'R': 'right',        # Right — Music & Effects
            'C': 'center',       # Center — Dialog
            'LFE': 'lfe',        # Low Frequency Effects (LFE) — Subwoofer
            'Ls': 'left_surround',  # Left Surround — Surround Effects
            'Rs': 'right_surround'  # Right Surround — Surround Effects
        }

        matching_files = {}
        for suffix in suffixes.keys():
            potential_file = os.path.join(directory, f"{base_name}.{suffix}.wav")
            if os.path.exists(potential_file):
                matching_files[suffix] = potential_file

        reply = QMessageBox.question(self, 'Confirm Combination',
                                     'Flere lydfiler (.L, .R, .C, .LFE, .Ls, .Rs) oppdaget. '
                                     'Vil du kombinere disse til én fil?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return selected_audio_file

        if len(matching_files) != len(suffixes):
            QMessageBox.warning(self, 'Error', 'Ikke alle nødvendige lydfiler (.L, .R, .C, .LFE, .Ls, .Rs) ble funnet.')
            return None

        combined_audio_file = os.path.join(directory, f"{base_name}_combined.wav")
        proceed_combine = self.exist_check(combined_audio_file)

        # FFmpeg command to combine the audio files into one using amerge
        ffmpeg_combine_audio_cmd = [
            'ffmpeg',
            '-i', matching_files['L'],  # Left — Music & Effects
            '-i', matching_files['R'],  # Right — Music & Effects
            '-i', matching_files['C'],  # Center — Dialog
            '-i', matching_files['LFE'],  # Low Frequency Effects (LFE) — Subwoofer
            '-i', matching_files['Ls'],  # Left Surround — Surround Effects
            '-i', matching_files['Rs'],  # Right Surround — Surround Effects
            '-filter_complex', '[0][1][2][3][4][5]amerge=inputs=6,pan=6c|c0<c0|c1<c1|c2<c2|c3<c3|c4<c4|c5<c5',
            '-ac', '6',  # Ensure output is 6 channels
            '-c:a', 'pcm_s16le',
            combined_audio_file,
            proceed_combine
        ]

        self.output_text.append('Running command: ' + ' '.join(ffmpeg_combine_audio_cmd))
        if not self.run_ffmpeg_command(ffmpeg_combine_audio_cmd):
            return None
        self.progress_bar.reset()
        return combined_audio_file

    def mappe_sok(self, folder_path):  # Searches through the folder for acceptable filetypes
        dpx_files = glob.glob(os.path.join(folder_path, '*.dpx'))
        mxf_files = [f for f in glob.glob(os.path.join(folder_path, '*.mxf')) if 'AUDIO' not in os.path.basename(f).upper()]
        mov_files = glob.glob(os.path.join(folder_path, '*.mov'))
        # optional_files = glob.glob(os.path.join(folder_path, '*.optional'))

        dpx_button = QPushButton(".dpx files")
        mxf_button = QPushButton(".mxf files")
        mov_button = QPushButton(".mov files")
        # optional_button = QPushButton('.optional files')

        if dpx_files and mxf_files and mov_files:
            msg = create_file_selection_box(
                "Fant både .dpx, .mov og .mxf (FILM) filer. Vennligst velg ett av alternativene!",
                [dpx_button, mov_button, mxf_button]
            )
        elif dpx_files and mxf_files:
            msg = create_file_selection_box(
                "Både .dpx and .mxf (FILM) filer funnet. Vennligst velg ett av alternativene!",
                [dpx_button, mxf_button]
            )
        elif dpx_files and mov_files:
            msg = create_file_selection_box(
                "Både .dpx and .mov files funnet. Vennligst velg ett av alternativene!",
                [dpx_button, mov_button]
            )
        elif mxf_files and mov_files:
            msg = create_file_selection_box(
                "Både .mxf (FILM) and .mov files funnet. Vennligst velg ett av alternativene!",
                [mxf_button, mov_button]
            )
        else:
            msg = None

        if msg:
            retval = msg.exec_()
            if msg.clickedButton() == dpx_button:
                self.selected_files = dpx_files
            elif msg.clickedButton() == mxf_button:
                if len(mxf_files) > 1:
                    selected_file = select_file_from_list(mxf_files, "mxf")
                    if selected_file:
                        self.selected_files = [selected_file]
                        self.mappe_input_field.setText(selected_file)
                else:
                    self.selected_files = mxf_files
                    self.mappe_input_field.setText(mxf_files[0])
            elif msg.clickedButton() == mov_button:
                if len(mov_files) > 1:
                    selected_file = select_file_from_list(mov_files, "mov")
                    if selected_file:
                        self.selected_files = [selected_file]
                        self.mappe_input_field.setText(selected_file)
                else:
                    self.selected_files = mov_files
                    self.mappe_input_field.setText(mov_files[0])
            else:
                self.selected_files = []
        elif dpx_files:
            self.selected_files = dpx_files
        elif mxf_files:
            self.selected_files = mxf_files
            self.mappe_input_field.setText(mxf_files[0])
        elif mov_files:
            self.selected_files = mov_files
            self.mappe_input_field.setText(mov_files[0])
        else:
            self.selected_files = []
            QMessageBox.warning(self, 'Advarsel', 'Ingen .dpx, .mxf (FILM), eller .mov filer funnet i den valgte mappen.')

    def check_box_logic(self):  # This method prevents illegal operation combinations
        if self.kunLydCheckBox.isChecked():
            self.inkluderLydCheckBox.setChecked(True)
            self.inkluderLydCheckBox.setEnabled(False)
            self.inkluderProresCheckBox.setChecked(False)
            self.inkluderProresCheckBox.setEnabled(False)
            self.fpsCounter.setEnabled(False)

        elif not self.kunLydCheckBox.isChecked() & self.inkluderLydCheckBox.isEnabled():
            self.inkluderLydCheckBox.setEnabled(True)
            self.inkluderProresCheckBox.setEnabled(True)
            self.fpsCounter.setEnabled(True)

    def lock_down(self, lock):  # Locks or unlocks the interface based on the 'lock' parameter
        widgets_to_lock = [
            self.inkluderLydCheckBox,
            self.inkluderProresCheckBox,
            self.kunLydCheckBox,
            self.mezzaninfilCheckBox,
            self.fpsCounter,
            self.mappeButton,
            self.fil_input_field,
            self.mappe_input_field,
            self.execButton,
            self.filButton,
            self.filmButton
        ]
        for widget in widgets_to_lock:
            widget.setEnabled(not lock)

    def DropDownListFix(self):  # Attempts to fix the god-damn dropdown box
        # Get the view of the combo box
        view = self.fpsCounter.view()
        if self.fpsCounter.currentIndex() % 2 == 0:
            view.setStyleSheet("border: 2px solid gray;")
        else:
            view.setStyleSheet("border: 2px solid red;")
        # Ensure the view updates its geometry
        view.updateGeometry()
        view.update()

    def determine_file_type(self):
        file_path = self.mappe_input_field.text().strip()
        if not file_path:
            QMessageBox.warning(self, 'Error', 'No file selected.')
            return None

        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        if file_extension == '.mxf':
            return 'mxf'
        elif file_extension == '.mov':
            return 'mov'
        elif file_extension == '':
            return 'dpx'
        else:
            QMessageBox.warning(self, 'Error', 'Unsupported file type selected.')
            return None

    def run_smelt(self):
        self.lock_down(True)
        self.output_text.setHidden(False)

        if not self.initial_setup():
            self.lock_down(False)
            return

        try:
            if not self.kunLydCheckBox.isChecked():
                self.handle_video_operations()
            else:
                self.handle_audio_operations()

            QMessageBox.information(self, 'Success', 'Konvertering fullført.')
            self.progress_bar.setValue(100)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, 'Error', f'En feil oppstod: {e}')
            self.output_text.append('Error: ' + str(e))
        finally:
            self.lock_down(False)

    def initial_setup(self):
        filetype = self.determine_file_type()
        folder_path = self.folder_path

        if not self.kunLydCheckBox.isChecked():
            if not folder_path:
                QMessageBox.warning(self, 'Error', 'Ingen mappe valgt')
                return False

            if filetype == 'dpx':
                if not self.check_dpx_files(folder_path):
                    return False
            else:
                self.video = self.mappe_input_field.text()

        self.fps = self.fpsCounter.currentText()
        self.folder_name = os.path.basename(folder_path)
        self.audio_file = self.audio_file_path or ''

        self.lossless_mov = os.path.join(folder_path, 'lossless', f'{self.folder_name}.mov')
        self.prores_mov = os.path.join(folder_path, 'lossless', f'{self.folder_name}_prores.mov')
        self.h264_mp4 = os.path.join(folder_path, 'lossless', f'nb-no_{self.folder_name}.mp4')

        os.makedirs(os.path.join(folder_path, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'lossless'), exist_ok=True)

        self.proceed_h264 = self.exist_check(self.h264_mp4)
        self.proceed_lossless = self.exist_check(self.lossless_mov) if self.mezzaninfilCheckBox.isChecked() else '-n'
        self.proceed_prores = self.exist_check(self.prores_mov) if self.inkluderProresCheckBox.isChecked() else '-n'

        return True

    def check_dpx_files(self, folder_path):
        pattern = os.path.join(folder_path, '*.dpx')
        matching_files = glob.glob(pattern)

        if not matching_files:
            QMessageBox.warning(self, 'Error', f'Finner ingen .dpx filer i {folder_path}.')
            return False

        matching_files.sort(key=extract_number)
        self.images_path = matching_files[0]
        print(f'Found file: {self.images_path}')

        result = QMessageBox.question(self, 'Start konvertering', f'Fant {os.path.basename(self.images_path)} i {folder_path}. Trykk ok for å gå videre.', QMessageBox.Ok | QMessageBox.Cancel)
        return result == QMessageBox.Ok

    def handle_video_operations(self):
        filetype = self.determine_file_type()
        if filetype == 'dpx':
            self.construct_dpx_commands()
        elif filetype in ['mxf', 'mov']:
            self.construct_mxf_mov_commands()

        if filetype == 'mxf':
            self.execute_ffmpeg_commands(['ffmpeg_dcp_cmd', 'ffmpeg_dcp_h264_cmd'])
        elif filetype == 'mov':
            self.execute_ffmpeg_commands(['ffmpeg_h264_from_prores_cmd'])
        elif not self.mezzaninfilCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_h264_cmd_direct'])
        else:
            self.execute_ffmpeg_commands(['ffmpeg_lossless_cmd', 'ffmpeg_prores_cmd', 'ffmpeg_h264_cmd'])

    def handle_audio_operations(self):
        self.construct_audio_commands()
        self.execute_ffmpeg_commands(['ffmpeg_lossless_audio_cmd', 'ffmpeg_audio_cmd'])

    def construct_dpx_commands(self):
        base_filename = os.path.basename(self.images_path)
        prefix = re.match(r'^\D*', base_filename).group()
        ffmpeg_input_pattern = os.path.join(self.folder_path, f'{prefix}%06d.dpx')
    
        self.ffmpeg_base_cmd = [
            'ffmpeg',
            '-v', 'error',
            '-stats',
            '-progress', '-',
            '-f', 'image2',
            '-vsync', '0',
            '-framerate', self.fps,
            '-start_number', '0',
            '-i', ffmpeg_input_pattern,
        ]

        if self.inkluderLydCheckBox.isChecked() and os.path.exists(self.audio_file):
            self.ffmpeg_base_cmd.extend(['-i', self.audio_file])
            audio_cmd = ['-c:a', 'copy']
        else:
            audio_cmd = []
    
        self.ffmpeg_lossless_cmd = self.ffmpeg_base_cmd + audio_cmd + [
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv422p10le',
            '-qp', '0',
            '-v', 'info',
            self.lossless_mov,
            self.proceed_lossless
        ]
        if not self.inkluderLydCheckBox:
            self.ffmpeg_h264_cmd_direct = self.ffmpeg_base_cmd + [
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=-2:1080',
                '-preset', 'slow',
                '-crf', '23',
                '-map', '0:v:0',
                '-v', 'info',
                self.h264_mp4,
                self.proceed_h264
            ]
        else:
            self.ffmpeg_h264_cmd_direct = self.ffmpeg_base_cmd + [
                '-i', self.audio_file,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=-2:1080',
                '-preset', 'slow',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '224k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-v', 'info',
                self.h264_mp4,
                self.proceed_h264
            ]
    
        self.ffmpeg_prores_cmd = [
            'ffmpeg',
            '-i', self.lossless_mov,
            '-c:v', 'prores',
            '-profile:v', '3',
            '-vf', 'scale=-2:1080',
            '-c:a', 'pcm_s16le',
            '-v', 'info',
            self.prores_mov,
            self.proceed_prores
        ]
    
        self.ffmpeg_h264_cmd = [
            'ffmpeg',
            '-i', self.lossless_mov,
            '-c:v', 'libx264',
            '-vf', 'scale=-2:1080',
            '-pix_fmt', 'yuv420p',
            '-preset', 'slow',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '224k',
            '-v', 'info',
            self.h264_mp4,
            self.proceed_h264
        ]
    
    def construct_mxf_mov_commands(self):
        self.ffmpeg_dcp_cmd = [
            'ffmpeg',
            '-i', self.video,
            '-i', self.audio_file if self.inkluderLydCheckBox.isChecked() else '',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv422p10le',
            '-preset', 'slow',
            '-qp', '0',
            '-c:a', 'copy',
            '-v', 'info',
            self.lossless_mov,
            self.proceed_lossless
        ]
        self.ffmpeg_dcp_h264_cmd = [
            'ffmpeg',
            '-i', self.video,
            '-i', self.audio_file if self.inkluderLydCheckBox.isChecked() else '',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'slow',
            '-crf', '21',
            '-ac', '2',
            '-v', 'info',
            self.h264_mp4,
            self.proceed_h264
        ]
        self.ffmpeg_h264_from_prores_cmd = [
            'ffmpeg',
            '-i', self.video,
            '-i', self.audio_file if self.audio_file else '',
            '-c:v', 'libx264',
            '-vf', 'scale=-2:1080',
            '-pix_fmt', 'yuv420p',
            '-preset', 'slow',
            '-crf', '23',
            '-c:a', 'aac' if self.audio_file else '',
            '-b:a', '224k' if self.audio_file else '',
            '-v', 'info',
            self.h264_mp4,
            self.proceed_h264
        ]
    
    def construct_audio_commands(self):
        self.ffmpeg_audio_cmd = [
            'ffmpeg',
            '-i', self.audio_file,
            '-c:a', 'aac',
            '-b:a', '192k',
            '-vn',
            '-v', 'info',
            self.h264_mp4,
            self.proceed_h264
        ]
        self.ffmpeg_lossless_audio_cmd = [
            'ffmpeg',
            '-i', self.audio_file,
            '-c:a', 'pcm_s16le',
            '-vn',
            '-v', 'info',
            self.lossless_mov,
            self.proceed_lossless
        ]
    
    def execute_ffmpeg_commands(self, commands):
        for cmd in commands:
            if hasattr(self, cmd):
                command = getattr(self, cmd)
                self.output_text.append('Running command: ' + ' '.join(command))
                if not self.run_ffmpeg_command(command):
                    break

    def update_output(self, text):
        self.output_text.append(text)

    def exist_check(self, filtype):
        if os.path.exists(filtype):
            overwrite = QMessageBox.question(self, 'Filen eksisterer!', f'{filtype} Eksisterer allerede. Overskriv?', QMessageBox.Yes | QMessageBox.No)
            if overwrite == QMessageBox.No:
                self.output_text.append(f'Avbrutt. {filtype} eksiterer allerede.')
                return '-n'
        return '-y'

    def run_ffmpeg_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        total_duration = None

        for line in iter(process.stderr.readline, ''):
            self.output_text.append(line.strip())
            QApplication.processEvents()

            if total_duration is None:
                duration_match = re.search(r'Duration: (\d+):(\d+):(\d+).(\d+)', line)
                if duration_match:
                    hours = int(duration_match.group(1))
                    minutes = int(duration_match.group(2))
                    seconds = int(duration_match.group(3))
                    total_duration = hours * 3600 + minutes * 60 + seconds

            time_match = re.search(r'time=(\d+):(\d+):(\d+).(\d+)', line)
            if time_match and total_duration:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / total_duration) * 100
                self.progress_bar.setValue(int(progress))

        process.wait()

        if process.returncode != 0:
            error_output = process.stderr.read()
            self.output_text.append(f'Error: {error_output}')
            return False
        return True


app = QApplication(sys.argv)

window = Smelt()
window.show()

sys.exit(app.exec_())
