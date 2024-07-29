import platform
import re
import subprocess
import sys
import os


from PyQt5.QtGui import QIcon, QPixmap, QPalette, QFont, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


def setup():
    """
    Simple method for some initial setup or imports based on specific operating systems, or other variables
    """
    if platform.system() == 'Windows':
        import resources_rc

    if hasattr(QApplication, 'setAttribute'):
        """
        Enable high dpi scaling
        """
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)


def customize_tooltips():
    """
    Customize the appearance of tooltips to make them look more dim/transparent.
    """
    palette = QToolTip.palette()
    palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50, 180))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255, 180))
    QToolTip.setPalette(palette)
    QToolTip.setFont(QFont('SansSerif', 10))


def get_ffmpeg_path():
    """
    Determines the path of the ffmpeg executable, whether the application runs bundled or in a Python environment.
    Only for Windows.

    Returns:
        str: Path to the ffmpeg executable.
    """
    if platform.system() == 'Windows':
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, 'ffmpeg.exe')
        else:
            return os.path.join(os.path.dirname(__file__), 'resources', 'ffmpeg.exe')
    else:
        return 'ffmpeg'


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

    This function checks for the presence of CUDA support in FFmpeg and
    the availability of an NVIDIA GPU using 'nvidia-smi'.

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
        result = subprocess.run(['ffmpeg', '-hwaccels'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        if 'cuda' in result.stdout:
            result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode == 0:
                return False # Should be set to true, currently temporarily disabled
        return False
    except FileNotFoundError:
        return False
    except Exception as e:
        print("CUDA availability check failed: {}".format(e))
        return False