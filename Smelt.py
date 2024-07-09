"""
SMELT: A GUI tool for video and audio file processing

This application provides functionalities for:
- Selecting and processing video and audio files
- Combining multichannel audio files
- Converting and processing video files using FFmpeg

Usage:
1. Run `setup.sh` or `setup.bat` to set up the environment.
2. Use the GUI to select files and start processing.

"""
import glob
import queue
import re
import subprocess
import sys
import os
import threading
import time

from PyQt5.QtWidgets import *


def create_file_selection_box(text, buttons):
    """
    Create a file selection message box with multiple buttons.

    Args:
        text (str): The message to display.
        buttons (list): A list of buttons to include in the message box.

    Returns:
        QMessageBox: The created message box.
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Flere filtyper funnet")
    msg.setText(text)
    for button in buttons:
        msg.addButton(button, QMessageBox.ActionRole)
    msg.addButton(QMessageBox.Cancel)
    return msg


def select_file_from_list(files, file_type_description):
    """
    Open a file selection dialog to select a file from a list.

    Args:
        files (list): A list of file paths to select from.
        file_type_description (str): A description of the file type.

    Returns:
        str: The selected file path, or None if no file was selected.
    """
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter("{} Files (*.{})".format(file_type_description, file_type_description))
    dialog.setViewMode(QFileDialog.Detail)
    dialog.setDirectory(os.path.dirname(files[0]))

    if dialog.exec_():
        selected_file = dialog.selectedFiles()[0]
        return selected_file
    return None


def extract_number(filename):
    """
    Extract the first number found in a filename.

    Args:
        filename (str): The filename to extract the number from.

    Returns:
        int: The extracted number, or float('inf') if no number was found.
    """
    base = os.path.basename(filename)
    match = re.search(r'(\d+)', base)
    return int(match.group(1)) if match else float('inf')


def cuda_available():
    """
    Check if CUDA is available on the system.

    This function checks for the presence of CUDA support in FFmpeg and the availability of an NVIDIA GPU using 'nvidia-smi'.

    Returns:
        bool: True if CUDA is available, False otherwise.

    The function performs the following checks:
    1. Runs `ffmpeg -hwaccels` to check if CUDA is listed among available hardware accelerations.
    2. If CUDA is found in the FFmpeg output, runs `nvidia-smi` to check for the presence of an NVIDIA GPU.
    3. Returns True if both checks pass, otherwise returns False.

    Exceptions:
        - Handles FileNotFoundError if 'nvidia-smi' is not found.
        - Catches and prints any other exceptions that occur during the checks.
    """
    try:
        # Check if ffmpeg has CUDA support
        result = subprocess.run(['ffmpeg', '-hwaccels'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if 'cuda' in result.stdout:
            # Check if nvidia-smi is available (indicates presence of NVIDIA GPU)
            result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode == 0:
                return True
        return False
    except FileNotFoundError:
        # Handle case where 'nvidia-smi' is not found
        return False
    except Exception as e:
        print("CUDA availability check failed: {}".format(e))
        return False


class Smelt(QWidget):
    """
    Smelt GUI application for video and audio processing.
    """

    def __init__(self):
        super(Smelt, self).__init__()

        # Initialize paths and filenames
        self.ffmpeg_dcp_prores = None
        self.ffmpeg_encoder = None
        self.video_encoder = None
        self.ffmpeg_lossless_audio_cmd = None
        self.ffmpeg_audio_cmd = None
        self.ffmpeg_h264_from_prores_cmd = None
        self.ffmpeg_dcp_h264_cmd = None
        self.ffmpeg_dcp_cmd = None
        self.ffmpeg_h264_cmd = None
        self.ffmpeg_prores_cmd = None
        self.ffmpeg_h264_cmd_direct = None
        self.ffmpeg_lossless_cmd = None
        self.ffmpeg_base = None
        self.step_label = None
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

        # Initialize UI elements
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

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.
        """
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
        """
        Create labels for the UI.
        """
        self.filLabel = QLabel('Lydfil:', self)
        self.mappeLabel = QLabel('Mappe/fil:', self)
        self.fpsLabel = QLabel('FPS:', self)
        self.step_label = QLabel('Processing Step:', self)
        self.step_label.setHidden(True)

    def create_checkboxes(self):
        """
        Create checkboxes for the UI.
        """
        self.inkluderLydCheckBox = QCheckBox('Lyd', self)
        self.inkluderProresCheckBox = QCheckBox('Prores 422 HQ', self)
        self.kunLydCheckBox = QCheckBox('Kun lydfil', self)
        self.mezzaninfilCheckBox = QCheckBox('Mezzaninfil', self)

    def create_buttons(self):
        """
        Create buttons for the UI.
        """
        self.mappeButton = QPushButton('Velg Mappe...', self)
        self.filmButton = QPushButton('Velg fil...')
        self.filButton = QPushButton('Velg lydfil...', self)
        self.execButton = QPushButton('Kjør', self)

    def create_combobox(self):
        """
        Create a combobox for FPS selection.
        """
        self.fpsCounter = QComboBox(self)
        for i in range(1, 61):
            self.fpsCounter.addItem(str(i))
        self.fpsCounter.setCurrentIndex(23)
        self.fpsCounter.view().parentWidget().setMaximumHeight(200)
        self.fpsCounter.setMaximumSize(50, 30)

    def create_text_output(self):
        """
        Create a text output area for logs.
        """
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setHidden(True)

    def create_progressbar(self):
        """
        Create a progress bar for indicating process progress.
        """
        self.progress_bar = QProgressBar(self)

    def setup_layout(self):
        """
        Set up the layout of the UI components.
        """
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
        layout.addWidget(self.step_label, 11, 0, 1, 5)
        self.setLayout(layout)

    def set_default_states(self):
        """
        Set the default states of checkboxes and other UI elements.
        """
        self.inkluderLydCheckBox.setChecked(True)
        self.inkluderProresCheckBox.setChecked(True)
        self.kunLydCheckBox.setChecked(False)
        self.mezzaninfilCheckBox.setChecked(True)

    def designate_button_methods(self):
        """
        Designate methods to buttons and other UI elements.
        """
        self.execButton.clicked.connect(self.run_smelt)
        self.filButton.clicked.connect(lambda: self.select_file_or_folder('audio'))
        self.mappeButton.clicked.connect(lambda: self.select_file_or_folder('mappe'))
        self.filmButton.clicked.connect(lambda: self.select_file_or_folder('film'))
        self.inkluderLydCheckBox.clicked.connect(lambda: self.check_box_logic('lyd'))
        self.kunLydCheckBox.clicked.connect(lambda: self.check_box_logic('kunlyd'))
        self.inkluderProresCheckBox.clicked.connect(lambda: self.check_box_logic('prores'))

    def set_styling(self):
        """
        Set the styling of the UI elements.
        """
        self.fil_input_field.setStyleSheet("border: 1px solid gray;")
        self.mappe_input_field.setStyleSheet('border: 1px solid gray;')
        self.setStyleSheet("background-color: #2B2B2B; color: white;")
        self.setWindowTitle('SMELT')
        self.resize(550, 200)

    def select_file_or_folder(self, file_type):
        """
        Open a file selection dialog based on the file type.

        Args:
            file_type (str): The type of file to select ('mappe', 'film', 'audio').
        """
        dialog = QFileDialog()

        def select_mappe():
            self.check_box_logic('')
            folder_path = dialog.getExistingDirectory(None, "Velg Mappe")
            if folder_path:
                self.folder_path = folder_path
                self.mappe_input_field.setText(folder_path)
                self.mappe_sok(folder_path)

        def select_film():
            self.check_box_logic('')
            file_filter = 'Movie files (*.mov *.mxf);;All Files (*)'
            file_path, _ = dialog.getOpenFileName(None, 'Velg Filmfil', '', file_filter)
            if file_path:
                self.film_file_path = file_path
                file_name = os.path.basename(file_path)
                self.folder_path = os.path.dirname(file_path)
                self.mappe_input_field.setText(file_name)

        def select_audio():
            self.inkluderLydCheckBox.setChecked(True)
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

        switch = {
            'mappe': select_mappe,
            'film': select_film,
            'audio': select_audio
        }

        switch.get(file_type, lambda: None)()

    def recognize_and_combine_audio_files(self, selected_audio_file):
        """
        Recognize and combine multichannel audio files into a single file.

        Args:
            selected_audio_file (str): The path of the selected audio file.

        Returns:
            str: The path of the combined audio file, or None if the process fails.
        """
        base_name = re.sub(r'\.[A-Za-z]+\.\w+$', '', os.path.basename(selected_audio_file))
        directory = os.path.dirname(selected_audio_file)

        suffixes = {
            'L': 'left',
            'R': 'right',
            'C': 'center',
            'LFE': 'lfe',
            'Ls': 'left_surround',
            'Rs': 'right_surround'
        }

        matching_files = {}
        for suffix in suffixes.keys():
            potential_file = os.path.join(directory, "{}.{}.wav".format(base_name, suffix))
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

        combined_audio_file = os.path.join(directory, "{}_combined.wav".format(base_name))
        proceed_combine = self.exist_check(combined_audio_file)

        ffmpeg_combine_audio_cmd = [
            'ffmpeg',
            '-i', matching_files['L'],
            '-i', matching_files['R'],
            '-i', matching_files['C'],
            '-i', matching_files['LFE'],
            '-i', matching_files['Ls'],
            '-i', matching_files['Rs'],
            '-filter_complex', '[0][1][2][3][4][5]amerge=inputs=6,pan=6c|c0<c0|c1<c1|c2<c2|c3<c3|c4<c4|c5<c5',
            '-ac', '6',
            '-c:a', 'pcm_s16le',
            combined_audio_file,
            proceed_combine
        ]

        self.output_text.append('Running command: ' + ' '.join(ffmpeg_combine_audio_cmd))
        if not self.run_ffmpeg_command(ffmpeg_combine_audio_cmd):
            return None
        self.progress_bar.reset()
        return combined_audio_file

    def mappe_sok(self, folder_path):
        """
        Search through the folder for acceptable file types.

        Args:
            folder_path (str): The path of the folder to search in.
        """
        file_types = {
            '.dpx': glob.glob(os.path.join(folder_path, '*.dpx')),
            '.mxf': [f for f in glob.glob(os.path.join(folder_path, '*.mxf')) if 'AUDIO' not in os.path.basename(f).upper()],
            '.mov': glob.glob(os.path.join(folder_path, '*.mov'))
        }

        available_types = {ext: files for ext, files in file_types.items() if files}
        buttons = {ext: QPushButton(f"{ext} files") for ext in available_types}

        if len(available_types) > 1:
            file_desc = ' og '.join(available_types.keys())
            msg = create_file_selection_box(
                f"Fant både {file_desc} filer. Vennligst velg ett av alternativene!",
                list(buttons.values())
            )
        else:
            msg = None

        if msg:
            retval = msg.exec_()
            for ext, button in buttons.items():
                if msg.clickedButton() == button:
                    self.selected_files = available_types[ext]
                    if len(self.selected_files) == 1:
                        self.mappe_input_field.setText(self.selected_files[0])
                    else:
                        selected_file = select_file_from_list(self.selected_files, ext.lstrip('.'))
                        if selected_file:
                            self.selected_files = [selected_file]
                            self.mappe_input_field.setText(selected_file)
                    break
        else:
            if '.dpx' in available_types:
                self.selected_files = available_types['.dpx']
            elif '.mxf' in available_types:
                self.selected_files = available_types['.mxf']
                self.mappe_input_field.setText(self.selected_files[0])
            elif '.mov' in available_types:
                self.selected_files = available_types['.mov']
                self.mappe_input_field.setText(self.selected_files[0])
            else:
                self.selected_files = []
                QMessageBox.warning(self, 'Advarsel', 'Ingen .dpx, .mxf (FILM), eller .mov filer funnet i den valgte mappen.')

    def check_box_logic(self, knapp):
        """
        Prevent illegal operation combinations by enabling/disabling checkboxes.
        Also toggles between kunLydCheckBox and inkluderProresCheckBox.
        """
        if knapp == 'kunlyd' and self.kunLydCheckBox.isChecked():
            self.fpsCounter.setEnabled(False)
            self.inkluderProresCheckBox.setChecked(False)
            self.inkluderLydCheckBox.setChecked(True)
            self.mappe_input_field.setText('')
            return
        elif knapp == 'lyd' and not self.inkluderLydCheckBox.isChecked():
            self.fil_input_field.setText('')
        self.fpsCounter.setEnabled(True)
        self.kunLydCheckBox.setChecked(False)

    def lock_down(self, lock):
        """
        Lock or unlock the interface based on the 'lock' parameter.

        Args:
            lock (bool): True to lock the interface, False to unlock.
        """
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

    def drop_down_list_fix(self):
        """
        Attempt to fix the dropdown box styling.
        """
        view = self.fpsCounter.view()
        if self.fpsCounter.currentIndex() % 2 == 0:
            view.setStyleSheet("border: 2px solid gray;")
        else:
            view.setStyleSheet("border: 2px solid red;")
        view.updateGeometry()
        view.update()

    def determine_file_type(self):
        """
        Determine the file type based on the mappe_input_field text.

        Returns:
            str: The file type ('mxf', 'mov', 'dpx') or None if unsupported.
        """
        file_path = self.mappe_input_field.text().strip()
        if not file_path:
            if not self.kunLydCheckBox.isChecked:
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

    def check_path_validity(self):
        """
        Check the validity of the paths in the input fields and update attributes accordingly.
        """
        mappe_input_text = self.mappe_input_field.text().strip()
        fil_input_text = self.fil_input_field.text().strip()

        if os.path.isdir(mappe_input_text):
            self.folder_path = mappe_input_text
        elif os.path.isfile(mappe_input_text):
            self.folder_path = os.path.dirname(mappe_input_text)
            self.film_file_path = mappe_input_text

        if os.path.isfile(fil_input_text):
            self.audio_file_path = fil_input_text
        elif fil_input_text == '':
            self.audio_file_path = ''
            self.inkluderLydCheckBox.setChecked(False)

        if self.audio_file_path != '' and not (os.path.isdir(mappe_input_text) | os.path.isfile(mappe_input_text)):
            if not self.kunLydCheckBox.isChecked():
                self.kunLydCheckBox.setChecked(True)
                self.inkluderProresCheckBox.setChecked(False)

    def run_smelt(self):
        """
        Main method to run the Smelt process.
        """
        self.check_path_validity()
        self.lock_down(True)
        self.output_text.setHidden(False)
        self.step_label.setHidden(False)
        self.step_label.setText("Initial setup...")  # Initial step

        if not self.initial_setup():
            self.lock_down(False)
            self.step_label.setText('Idle')
            return

        try:
            if not self.kunLydCheckBox.isChecked():
                self.handle_video_operations()
            else:
                self.handle_audio_operations()

            QMessageBox.information(self, 'Success', 'Konvertering fullført.')
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, 'Error', 'En feil oppstod: {}'.format(e))
            self.output_text.append('Error: ' + str(e))
        finally:
            self.lock_down(False)
            self.step_label.setText("Idle")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("100% - Done")

    def initial_setup(self):
        """
        Perform initial setup and validation before running the main process.

        Returns:
            bool: True if setup is successful, False otherwise.
        """
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

        if cuda_available():
            self.ffmpeg_hardware_accel = [
                '-hwaccel', 'cuda',
            ]
            self.ffmpeg_encoder = [
                '-c:v', 'hevc_nvenc',
                '-pix_fmt', 'yuv422p10le',
            ]
        else:
            self.ffmpeg_hardware_accel = [
                '-hwaccel', 'auto',
            ]
            self.ffmpeg_encoder = [
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv422p10le',
            ]

        self.fps = self.fpsCounter.currentText()
        self.folder_name = os.path.basename(folder_path)
        self.audio_file = self.audio_file_path or ''

        self.lossless_mov = os.path.join(folder_path, 'lossless', '{}.mov'.format(self.folder_name))
        self.prores_mov = os.path.join(folder_path, 'lossless', '{}_prores.mov'.format(self.folder_name))
        self.h264_mp4 = os.path.join(folder_path, 'lossless', 'nb-no_{}.mp4'.format(self.folder_name))

        os.makedirs(os.path.join(folder_path, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'lossless'), exist_ok=True)

        self.proceed_h264 = self.exist_check(self.h264_mp4)
        self.proceed_lossless = self.exist_check(self.lossless_mov) if self.mezzaninfilCheckBox.isChecked() else '-n'
        self.proceed_prores = self.exist_check(self.prores_mov) if self.inkluderProresCheckBox.isChecked() else '-n'

        return True

    def check_dpx_files(self, folder_path):
        """
        Check for DPX files in the specified folder.

        Args:
            folder_path (str): The path of the folder to check.

        Returns:
            bool: True if DPX files are found and confirmed, False otherwise.
        """
        pattern = os.path.join(folder_path, '*.dpx')
        matching_files = glob.glob(pattern)

        if not matching_files:
            QMessageBox.warning(self, 'Error', 'Finner ingen .dpx filer i {}.'.format(folder_path))
            return False

        matching_files.sort(key=extract_number)
        self.images_path = matching_files[0]
        print('Found file: {}'.format(self.images_path))

        result = QMessageBox.question(self, 'Start konvertering', 'Fant {} i {}. Trykk ok for å gå videre.'.format(
            os.path.basename(self.images_path), folder_path), QMessageBox.Ok | QMessageBox.Cancel)
        return result == QMessageBox.Ok

    def handle_video_operations(self):
        """
        Handle video processing operations based on file type.
        """
        filetype = self.determine_file_type()
        if filetype == 'dpx':
            self.construct_dpx_commands()
        elif filetype in ['mxf', 'mov']:
            self.construct_mxf_mov_commands()

        if filetype == 'mxf':
            self.execute_ffmpeg_commands(['ffmpeg_dcp_cmd', 'ffmpeg_dcp_prores', 'ffmpeg_dcp_h264_cmd'])
        elif filetype == 'mov':
            self.execute_ffmpeg_commands(['ffmpeg_h264_from_prores_cmd'])
        elif not self.mezzaninfilCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_h264_cmd_direct'])
        else:
            self.execute_ffmpeg_commands(['ffmpeg_lossless_cmd', 'ffmpeg_prores_cmd', 'ffmpeg_h264_cmd'])

    def handle_audio_operations(self):
        """
        Handle audio processing operations.
        """
        self.construct_audio_commands()
        self.execute_ffmpeg_commands(['ffmpeg_lossless_audio_cmd', 'ffmpeg_audio_cmd'])

    def construct_dpx_commands(self):
        """
        Construct FFmpeg commands for DPX file processing.
        """
        base_filename = os.path.basename(self.images_path)
        prefix = re.match(r'^\D*', base_filename).group()
        ffmpeg_input_pattern = os.path.join(self.folder_path, '{}%06d.dpx'.format(prefix))

        self.ffmpeg_base = [
            'ffmpeg', '-v',
            'info', '-stats',
            '-progress', '-',
        ]

        ffmpeg_dpx = [
            '-f', 'image2',
            '-vsync', '0',
            '-framerate', self.fps,
            '-start_number', '0',
            '-i', ffmpeg_input_pattern,
        ]

        if self.inkluderLydCheckBox.isChecked() and os.path.exists(self.audio_file):
            ffmpeg_dpx.extend(['-i', self.audio_file])
            audio_cmd = ['-c:a', 'copy']
        else:
            audio_cmd = []

        self.ffmpeg_lossless_cmd = self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx + self.ffmpeg_encoder + audio_cmd + [
                '-qp', '0',
                self.lossless_mov,
                self.proceed_lossless
            ]

        if self.inkluderLydCheckBox.isChecked():
            self.ffmpeg_h264_cmd_direct = self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx + audio_cmd + [
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=-2:1080',
                '-preset', 'slow',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '224k',
                '-map', '0:v:0',
                '-map', '1:a:0',
                self.h264_mp4,
                self.proceed_h264
            ]
        else:
            self.ffmpeg_h264_cmd_direct = self.ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_dpx + [
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=-2:1080',
                '-preset', 'slow',
                '-crf', '23',
                '-map', '0:v:0',
                self.h264_mp4,
                self.proceed_h264
            ]

        self.ffmpeg_prores_cmd = self.ffmpeg_base + self.ffmpeg_hardware_accel + [
            '-i', self.lossless_mov,
            '-c:v', 'prores',
            '-profile:v', '3',
            '-vf', 'scale=-2:1080',
            '-c:a', 'pcm_s16le',
            self.prores_mov,
            self.proceed_prores
        ]

        self.ffmpeg_h264_cmd = self.ffmpeg_base + self.ffmpeg_hardware_accel + [
            '-i', self.lossless_mov,
        ] + self.ffmpeg_encoder + [
                                   '-vf', 'scale=-2:1080',
                                   '-pix_fmt', 'yuv420p',
                                   '-preset', 'slow',
                                   '-crf', '23',
                                   '-c:a', 'aac',
                                   '-b:a', '224k',
                                   self.h264_mp4,
                                   self.proceed_h264
                               ]

    def construct_mxf_mov_commands(self):
        """
        Construct FFmpeg commands for MXF and MOV file processing.
        """
        ffmpeg_base = ['ffmpeg',]

        if self.inkluderLydCheckBox.isChecked and self.audio_file:
            ffmpeg_video_audio = ['-i', self.video, '-i', self.audio_file, ]
            ffmpeg_audio_param = [
                '-c:a', 'aac',
                '-b:a', '224k',
            ]
        else:
            ffmpeg_video_audio = ['-i', self.video,]
            ffmpeg_audio_param = []
        self.ffmpeg_dcp_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + self.ffmpeg_encoder + [
            '-preset', 'slow',
            '-qp', '0',
            '-c:a', 'copy',
            '-v', 'info',
            self.lossless_mov,
            self.proceed_lossless
        ]
        self.ffmpeg_dcp_prores = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
            '-c:v', 'prores',
            '-profile:v', '3',
            '-pix_fmt', 'yuv422p10le',
            '-vf', 'scale=-2:1080',
            '-c:a', 'pcm_s16le',
            self.prores_mov,
            self.proceed_prores
        ]
        self.ffmpeg_dcp_h264_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'slow',
            '-crf', '21',
            '-ac', '2',
        ] + ffmpeg_audio_param + [
                                       '-v', 'info',
                                       self.h264_mp4,
                                       self.proceed_h264
                                   ]
        self.ffmpeg_h264_from_prores_cmd = ffmpeg_base + self.ffmpeg_hardware_accel + ffmpeg_video_audio + [
            '-c:v', 'libx264',
            '-vf', 'scale=-2:1080',
            '-pix_fmt', 'yuv420p',
            '-preset', 'slow',
            '-crf', '23',
            '-v', 'info',
            self.h264_mp4,
            self.proceed_h264
        ]

    def construct_audio_commands(self):
        """
        Construct FFmpeg commands for audio file processing.
        """
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
        """
        Execute a list of FFmpeg commands.

        Args:
            commands (list): A list of command attribute names to execute.
        """
        for i, cmd in enumerate(commands):
            step_text = "Step {}/{}: Running {}".format(i + 1, len(commands), cmd.replace('_', ' ').title())
            self.step_label.setText(step_text)
            if hasattr(self, cmd):
                command = getattr(self, cmd)
                self.output_text.append('Running command: ' + ' '.join(command))
                if not self.run_ffmpeg_command(command):
                    break

    def update_output(self, text):
        """
        Update the output text area with new text.

        Args:
            text (str): The text to append to the output area.
        """
        self.output_text.append(text)

    def exist_check(self, filtype):
        """
        Check if a file exists and prompt the user to overwrite if it does.

        Args:
            filtype (str): The file path to check.

        Returns:
            str: '-y' to overwrite, '-n' to skip.
        """
        if os.path.exists(filtype):
            overwrite = QMessageBox.question(self, 'Filen eksisterer!',
                                             '{} Eksisterer allerede. Overskriv?'.format(filtype),
                                             QMessageBox.Yes | QMessageBox.No)
            if overwrite == QMessageBox.No:
                self.output_text.append('Avbrutt. {} eksiterer allerede.'.format(filtype))
                return '-n'
        return '-y'

    def run_ffmpeg_command(self, command):
        """
        Run an FFmpeg command and update the progress bar.

        Args:
            command (list): The FFmpeg command to run.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        def enqueue_output(pipe, queue):
            for line in iter(pipe.readline, ''):
                queue.put(line)
            pipe.close()

        stdout_thread = threading.Thread(target=enqueue_output, args=(process.stdout, stdout_queue))
        stderr_thread = threading.Thread(target=enqueue_output, args=(process.stderr, stderr_queue))
        stdout_thread.start()
        stderr_thread.start()

        total_duration = None
        start_time = time.time()
        stderr_output = []

        while True:
            try:
                line = stderr_queue.get_nowait()
            except queue.Empty:
                if process.poll() is not None:
                    break
                time.sleep(0.1)
                continue

            self.output_text.append(line.strip())
            stderr_output.append(line.strip())
            QApplication.processEvents()

            if total_duration is None:
                duration_match = re.search(r'Duration: (\d+):(\d+):(\d+).(\d+)', line)
                if duration_match:
                    hours = int(duration_match.group(1))
                    minutes = int(duration_match.group(2))
                    seconds = int(duration_match.group(3))
                    total_duration = hours * 3600 + minutes * 60 + seconds
                    start_time = time.time()

            time_match = re.search(r'time=(\d+):(\d+):(\d+).(\d+)', line)
            if time_match and total_duration:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = int(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / total_duration) * 100
                elapsed_time = time.time() - start_time
                remaining_time = elapsed_time * (100 - progress) / progress if progress > 0 else 0
                self.progress_bar.setValue(int(progress))
                self.progress_bar.setFormat("{}% - Estimated time left: {}m {}s".format(int(progress), int(remaining_time // 60), int(remaining_time % 60)))

        stdout_thread.join()
        stderr_thread.join()
        process.wait()

        if process.returncode != 0:
            self.output_text.append('Error: {}'.format('\n'.join(stderr_output)))
            return False
        return True


app = QApplication(sys.argv)

window = Smelt()
window.show()

sys.exit(app.exec_())
