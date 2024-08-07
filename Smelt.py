"""
SMELT: A GUI tool for video and audio file processing

This application provides functionalities for:
- Selecting and processing video and audio files
- Combining multichannel audio files
- Converting and processing video files using FFmpeg
"""
import glob
import platform
import queue
import re
import subprocess
import sys
import os
import threading
import time
import Utils
import ffmpeg_commands
import GUI

from PyQt5.QtWidgets import *


class Smelt(QWidget):
    """
    Smelt GUI application for video and audio processing.
    """

    def __init__(self):
        super(Smelt, self).__init__()

        """
        Initialize paths and filenames
        """
        self.output_folder_name = None
        self.output_folder = None
        self.log_file_name = None
        self.temp_mov = None
        self.process = None
        self.process_terminated = None
        self.ffmpeg_hardware_accel = None
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
        self.ffmpeg_path = None

        """
        Initialize UI elements
        """
        self.filLabel = None
        self.step_label = None
        self.cuda_indicator = None
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
        GUI.create_labels(self)
        GUI.create_checkboxes(self)
        GUI.create_buttons(self)
        GUI.create_text_output(self)
        GUI.create_combobox(self)
        GUI.create_progressbar(self)
        GUI.create_cuda_indicator(self)
        GUI.create_ffmpeg_indicator(self)
        GUI.create_empty_indicator(self)
        GUI.setup_layout(self)
        GUI.set_default_states(self)
        GUI.designate_button_methods(self)
        GUI.set_styling(self)
        GUI.center_window(self)

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
            self.ffmpeg_path,
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
            '.mxf': [f for f in glob.glob(os.path.join(folder_path, '*.mxf')) if
                     'AUDIO' not in os.path.basename(f).upper()],
            '.mov': glob.glob(os.path.join(folder_path, '*.mov'))
        }

        available_types = {ext: files for ext, files in file_types.items() if files}
        buttons = {ext: QPushButton("{} files".format(ext)) for ext in available_types}

        if len(available_types) > 1:
            file_desc = ' og '.join(available_types.keys())
            msg = Utils.create_file_selection_box(
                "Fant både {} filer. Vennligst velg ett av alternativene!".format(file_desc),
                list(buttons.values())
            )
        else:
            msg = None

        if msg:
            msg.exec_()
            for ext, button in buttons.items():
                if msg.clickedButton() == button:
                    self.selected_files = available_types[ext]
                    if len(self.selected_files) == 1:
                        self.mappe_input_field.setText(self.selected_files[0])
                    else:
                        selected_file = Utils.select_file_from_list(self.selected_files, ext.lstrip('.'))
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
                QMessageBox.warning(self, 'Advarsel',
                                    'Ingen .dpx, .mxf (FILM), eller .mov filer funnet i den valgte mappen.')

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
        Execute the Smelt process for converting video and audio files.

        This method orchestrates the entire Smelt process, including initial setup,
        video and audio processing, and error handling. The method updates the GUI
        elements to reflect the current status and locks down the interface to
        prevent user interaction during processing.

        Steps involved:
        1. Check the validity of input paths.
        2. Lock down the GUI and show initial setup status.
        3. Perform initial setup for the conversion process.
        4. Based on user selection, handle either video or audio operations.
        5. Display success or termination messages upon completion.
        6. Handle and display errors if any subprocess or general exceptions occur.
        7. Unlock the GUI and reset the status label to 'Idle' after processing.

        Raises:
            subprocess.CalledProcessError: If an error occurs during the subprocess execution.
            Exception: For any other exceptions that may occur during the process.
        """
        self.check_path_validity()
        GUI.lock_down(self, True)
        self.output_text.setHidden(False)
        self.step_label.setHidden(False)
        self.step_label.setText("Initial setup...")  # Initial step

        if not self.initial_setup():
            GUI.lock_down(self, False)
            self.step_label.setText('Idle')
            return

        self.process_terminated = False

        try:
            if not self.kunLydCheckBox.isChecked():
                self.handle_video_operations()
            else:
                self.handle_audio_operations()

            if not self.process_terminated:
                QMessageBox.information(self, 'Success', 'Konvertering fullført.')
                self.progress_bar.setValue(100)
                self.progress_bar.setFormat("100% - Done")
            else:
                QMessageBox.critical(self, 'Terminated', 'Prosessen ble avbrutt.')
                self.progress_bar.setValue(100)
                self.progress_bar.setFormat("100% - Terminated")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, 'Error', 'En feil oppstod: {}'.format(e))
            self.output_text.append('Error: ' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'En feil oppstod: {}'.format(e))
            self.output_text.append('Error: ' + str(e))
        finally:
            GUI.lock_down(self, False)
            self.step_label.setText("Idle")

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

        if self.folder_name == "images" or self.folder_name == "audio":
            output_folder = os.path.dirname(folder_path)
            output_folder_name = os.path.basename(output_folder)
        else:
            output_folder = folder_path
            output_folder_name = os.path.basename(output_folder)

        self.lossless_mov = os.path.join(output_folder, 'lossless', '{}.mov'.format(output_folder_name))
        self.prores_mov = os.path.join(output_folder, 'lossless', '{}_prores.mov'.format(output_folder_name))
        self.h264_mp4 = os.path.join(output_folder, 'lossless', 'nb-no_{}.mp4'.format(output_folder_name))
        self.temp_mov = os.path.join(output_folder, 'lossless', 'temp_{}.mov'.format(output_folder_name))

        os.makedirs(os.path.join(output_folder, 'lossless'), exist_ok=True)
        os.makedirs(os.path.join(output_folder, 'logs'), exist_ok=True)

        self.output_folder_name = output_folder_name
        self.output_folder = output_folder

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

        matching_files.sort(key=Utils.extract_number)
        self.images_path = matching_files[0]
        print('Found file: {}'.format(self.images_path))

        result = QMessageBox.question(self, 'Start konvertering', 'Fant {} i {}. Trykk ok for å gå videre.'.format(
            os.path.basename(self.images_path), folder_path), QMessageBox.Ok | QMessageBox.Cancel)
        return result == QMessageBox.Ok

    def toggle_execute_button(self):
        """
        Toggle the text and functionality of the execute button between 'Kjør' and 'Avbryt'.

        This method changes the button text and disconnects the current click event handler,
        then connects the appropriate handler based on the current state:
        - When the button text is 'Kjør' (Run),
         it changes to 'Avbryt' (Abort) and connects the button to the abort method.
        - When the button text is 'Avbryt' (Abort),
         it changes to 'Kjør' (Run) and connects the button to the run_smelt method.
        """
        if self.execButton.text() == 'Kjør':
            self.execButton.setText('Avbryt')
            self.execButton.clicked.disconnect()
            self.execButton.clicked.connect(self.abort)

        elif self.execButton.text() == 'Avbryt':
            self.execButton.setText('Kjør')
            self.execButton.clicked.disconnect()
            self.execButton.clicked.connect(self.run_smelt)

    def abort(self):
        """
        Handle the process abortion when the user requests to stop the ongoing operation.

        This method shows a confirmation dialog to the user. If the user confirms, it attempts to terminate the
        ongoing FFmpeg process. Any exception during the termination is caught and displayed as a critical error.
        Upon successful termination or if the process was aborted,
         an appropriate message is appended to the output text area.
        """
        reply = QMessageBox.question(self, 'Bekreft avbrytelse',
                                     'Er du sikker på at du vil avbryte prosessen?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.process.terminate()
                self.process_terminated = True
            except Exception as e:
                QMessageBox.critical(self, 'Error:', 'feil i termineringen av prosessen {}'.format(e))
            self.output_text.append('FFmpeg process aborted.')

    def handle_video_operations(self):
        """
        Handle video processing operations based on file type.
        """
        filetype = self.determine_file_type()
        if filetype == 'dpx':
            ffmpeg_commands.construct_dpx_commands(self)
        elif filetype in ['mxf', 'mov']:
            ffmpeg_commands.construct_mxf_mov_commands(self)

        if filetype == 'mxf':
            commands = []
            if self.mezzaninfilCheckBox.isChecked():
                commands.append('ffmpeg_dcp_cmd')
            if self.inkluderProresCheckBox.isChecked():
                commands.append('ffmpeg_dcp_prores')
            commands.append('ffmpeg_dcp_h264_cmd')
            self.execute_ffmpeg_commands(commands)
        elif filetype == 'mov':
            self.execute_ffmpeg_commands(['ffmpeg_h264_from_prores_cmd'])
        elif not self.mezzaninfilCheckBox.isChecked() and not self.inkluderProresCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_h264_cmd_direct'])
        elif not self.inkluderProresCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_lossless_cmd', 'ffmpeg_h264_cmd'])
        elif self.inkluderProresCheckBox.isChecked() and not self.mezzaninfilCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_prores_cmd', 'ffmpeg_h264_cmd_direct'])
        else:
            self.execute_ffmpeg_commands(['ffmpeg_lossless_cmd', 'ffmpeg_prores_cmd', 'ffmpeg_h264_cmd'])

    def handle_audio_operations(self):
        """
        Handle audio processing operations.
        """
        ffmpeg_commands.construct_audio_commands(self)
        if self.mezzaninfilCheckBox.isChecked():
            self.execute_ffmpeg_commands(['ffmpeg_lossless_audio_cmd', 'ffmpeg_audio_cmd'])
        else:
            self.execute_ffmpeg_commands(['ffmpeg_audio_cmd'])

    def execute_ffmpeg_commands(self, commands):
        """
        Execute a list of FFmpeg commands.

        Args:
            commands (list): A list of command attribute names to execute.
        """
        for i, cmd in enumerate(commands):
            log_path = os.path.join(self.output_folder, 'logs', '{}_log.log'.format(commands[i]))
            if platform.system() == 'Windows':
                log_path = os.path.normpath(log_path)
            ffreport_value = "file=" + log_path
            os.environ['FFREPORT'] = ffreport_value
            self.output_text.append(ffreport_value)
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
        Execute an FFmpeg command and update the GUI progress bar accordingly.

        This method runs the given FFmpeg command as a subprocess, captures its output,
        and updates the progress bar based on the command's progress. It also handles
        platform-specific settings to run FFmpeg in a non-interactive mode on Windows.

        Args:
            command (list): The FFmpeg command to run, provided as a list of strings.

        Returns:
            bool: True if the command executes successfully, False otherwise.

        Steps:
        1. Set up platform-specific startup information for the subprocess.
        2. Start the FFmpeg subprocess and capture its stdout and stderr outputs.
        3. Use separate threads to enqueue stdout and stderr outputs.
        4. Parse the stderr output to determine the total duration of the video.
        5. Update the progress bar based on the current processing time.
        6. Display estimated remaining time for the process to complete.
        7. Wait for the process and threads to finish.
        8. Check the return code to determine if the process was successful.

        Raises:
            subprocess.CalledProcessError: If the FFmpeg command returns a non-zero exit code.
            Exception: For any other exceptions that may occur during the process.
        """
        if platform.system() == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        startupinfo=startupinfo, universal_newlines=True)
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        def enqueue_output(pipe, queue):
            for line in iter(pipe.readline, ''):
                queue.put(line)
            pipe.close()

        stdout_thread = threading.Thread(target=enqueue_output, args=(self.process.stdout, stdout_queue))
        stderr_thread = threading.Thread(target=enqueue_output, args=(self.process.stderr, stderr_queue))
        stdout_thread.start()
        stderr_thread.start()

        total_duration = None
        start_time = time.time()
        stderr_output = []

        while True:
            try:
                line = stderr_queue.get_nowait()
            except queue.Empty:
                if self.process.poll() is not None:
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
                self.progress_bar.setFormat(
                    "{}% - Estimated time left: {}m {}s".format(int(progress), int(remaining_time // 60),
                                                                int(remaining_time % 60)))

        stdout_thread.join()
        stderr_thread.join()
        self.process.wait()

        if self.process.returncode != 0:
            self.output_text.append('Error: {}'.format('\n'.join(stderr_output)))
            return False
        return True


Utils.setup()
app = QApplication(sys.argv)
app.setStyle('Breeze')

window = Smelt()
window.show()

sys.exit(app.exec_())
