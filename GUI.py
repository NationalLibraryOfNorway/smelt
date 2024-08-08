import platform
import sys

import Utils

from PyQt5.QtGui import QIcon, QPixmap, QPalette, QFont, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class GUI:
    def __init__(self, smelt_instance):
        self.smelt = smelt_instance


def center_window(self):
    """
    Center the window on the screen.
    """
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


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

    self.mappeButton.setToolTip('Velg en mappe med .dpx-er, .mxf eller .mov filer.')
    self.filmButton.setToolTip('Velg en .mxf eller en .mov fil.')
    self.filButton.setToolTip('Velg en lydfil.')
    self.execButton.setToolTip('Start konverteringen.')
    Utils.customize_tooltips()


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


def create_cuda_indicator(self):
    """
    Create an indicator light to show the status of the CUDA check.
    """
    self.cuda_indicator = QLabel(self)
    self.cuda_indicator.setFixedSize(22, 22)
    #
    # if getattr(sys, 'frozen', False):
    #     icon_path = ":/cuda.png"
    # else:
    #     icon_path = "resources/cuda.png"
    # pixmap = QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #
    # if Utils.cuda_available():
    #     self.cuda_indicator.setStyleSheet("""
    #             QLabel {
    #                 background-color: green;
    #                 border: 4px solid green;
    #                 padding: 18px;
    #                 border-radius: 6px;
    #                 font-size: 12px;
    #             }
    #             QLabel[toolTip] {
    #                 font-size: 12px;
    #             }
    #         """)
    #     self.cuda_indicator.setToolTip("CUDA Hardware Akselerasjon Tilgjengelig.")
    # else:
    #     self.cuda_indicator.setStyleSheet("""
    #             QLabel {
    #                 background-color: red;
    #                 border: 4px solid red;
    #                 padding: 18px;
    #                 border-radius: 6px;
    #                 font-size: 12px;
    #             }
    #             QLabel[toolTip] {
    #                 font-size: 12px;
    #             }
    #         """)
    #     self.cuda_indicator.setToolTip("CUDA Hardware Akselerasjon IKKE Tilgjengelig.")
    #
    # self.cuda_indicator.setPixmap(pixmap)
    self.cuda_indicator.setAlignment(Qt.AlignCenter)
    self.cuda_indicator.setToolTipDuration(0)


def create_ffmpeg_indicator(self):
    """
    Create an indicator to show the status of FFmpeg, and calls the method to use either the newest version of ffmpeg
    or packaged version
    """
    self.ffmpeg_indicator = QLabel(self)
    self.ffmpeg_indicator.setFixedSize(22, 22)

    if getattr(sys, 'frozen', False):
        icon_path = ":/ffmpeg.png"
    else:
        icon_path = "resources/ffmpeg.png"
    pixmap = QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    ffmpeg_path, is_packaged_version = Utils.get_ffmpeg_path(include_packaged_version=True)
    self.ffmpeg_path = ffmpeg_path

    if is_packaged_version:
        self.ffmpeg_indicator.setStyleSheet("""
                QLabel { 
                    background-color: blue; 
                    border: 4px solid blue; 
                    padding: 18px; 
                    border-radius: 6px; 
                    font-size: 12px;  
                }
                QLabel[toolTip] { 
                    font-size: 12px;  
                }
            """)
        self.ffmpeg_indicator.setToolTip("Medpakket versjon av FFmpeg.")
    elif is_packaged_version is None:
        self.ffmpeg_indicator.setStyleSheet("""
                QLabel { 
                    background-color: red; 
                    border: 4px solid red; 
                    padding: 18px; 
                    border-radius: 6px; 
                    font-size: 12px;  
                }
                QLabel[toolTip] { 
                    font-size: 12px;  
                }
            """)
        self.ffmpeg_indicator.setToolTip("Ingen versjon av FFmpeg funnet.")
    else:
        self.ffmpeg_indicator.setStyleSheet("""
                QLabel { 
                    background-color: green; 
                    border: 4px solid green; 
                    padding: 18px; 
                    border-radius: 6px; 
                    font-size: 12px;  
                }
                QLabel[toolTip] { 
                    font-size: 12px;  
                }
            """)
        self.ffmpeg_indicator.setToolTip("Lokal versjon av FFmpeg.")

    self.ffmpeg_indicator.setPixmap(pixmap)
    self.ffmpeg_indicator.setAlignment(Qt.AlignCenter)
    self.ffmpeg_indicator.setToolTipDuration(0)


def create_empty_indicator(self):
    """
    Create an indicator light to show the status of the (empty) check.
    """
    self.empty_indicator = QLabel(self)
    self.empty_indicator.setFixedSize(22, 22)
    # This is where you can fill in the options for a third indicator of some kind for future expansion
    self.empty_indicator.setAlignment(Qt.AlignCenter)
    self.empty_indicator.setToolTipDuration(0)


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

    indicators_layout = QHBoxLayout()
    indicators_layout.addWidget(self.cuda_indicator)
    indicators_layout.addWidget(self.ffmpeg_indicator)
    indicators_layout.addWidget(self.empty_indicator)
    indicators_layout.setSpacing(0)

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
    layout.addLayout(indicators_layout, 6, 4)

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
    if platform.system() == 'Windows':
        self.setStyleSheet("""
                QWidget {
                    background-color: #2B2B2B; 
                    color: white; 
                    font-family: 'Segoe UI'; 
                    font-size: 10pt;
                }
                QPushButton {
                    background-color: #3A3A3A; 
                    color: white; 
                    border: 1px solid #5A5A5A;
                    padding: 5px;
                }
                QLineEdit {
                    background-color: #3A3A3A;
                    color: white;
                    border: 1px solid #5A5A5A;
                    padding: 3px;
                }
                QTextEdit {
                    background-color: #3A3A3A;
                    color: white;
                    border: 1px solid #5A5A5A;
                    padding: 5px;
                }
                QLabel {
                    padding: 2px;
                }
                QProgressBar {
                    border: 1px solid #5A5A5A;
                    text-align: center;
                    background: #3A3A3A;
                    color: white;
                    height: 15px;
                }
                QComboBox {
                    background-color: #3A3A3A;
                    color: white;
                    border: 1px solid #5A5A5A;
                }
            """)
        self.setWindowIcon(QIcon('resources/icon.ico'))
        self.setWindowIcon(QIcon(':/icon.ico'))
    else:
        self.setStyleSheet("background-color: #2B2B2B; color: white;")

    self.fil_input_field.setStyleSheet("border: 1px solid gray;")
    self.mappe_input_field.setStyleSheet('border: 1px solid gray;')
    self.setStyleSheet("background-color: #2B2B2B; color: white;")
    self.setWindowTitle('SMELT')
    self.resize(550, 200)


def lock_down(self, lock):
    """
    Lock or unlock the interface based on the 'lock' parameter.

    Args:
        lock (bool): True to lock the interface, False to unlock.
        :param lock:
        :param self:
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
        self.filButton,
        self.filmButton
    ]
    for widget in widgets_to_lock:
        widget.setEnabled(not lock)

    self.toggle_execute_button()