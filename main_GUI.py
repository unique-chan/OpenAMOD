from src import *

import sys
import warnings
import os
import subprocess # for running multiple missions.

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout,
                             QComboBox, QFrame, QPushButton, QSpinBox, QScrollArea, QTextEdit, QDateEdit)

warnings.filterwarnings("ignore")


class DataGenGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # ====================< Layer 0 >====================
        try:
            pixmap = QPixmap('figs/AMOD-DataGen-Logo.png')
            target_height = 130
            target_width = int(pixmap.width() * (target_height / pixmap.height()))
            pixmap = pixmap.scaled(target_width, target_height)
            line_layout = QHBoxLayout()
            label = QLabel('Window', self)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            line_layout.addWidget(label)
            self.layout.addLayout(line_layout)
        except Exception as e:
            print(e)
            pass

        # ====================< layer 1 >====================
        mode_label = QLabel('Imagery', self)
        self.mode_combobox = QComboBox(self)
        for mode in list_options['modes']: self.mode_combobox.addItem(mode)
        self.mode_combobox.setFixedSize(100, 25)

        map_label = QLabel('Map in ARMA', self)
        self.map_combobox = QComboBox(self)
        for map_ in list_options['map_names']: self.map_combobox.addItem(map_)
        self.map_combobox.setFixedSize(200, 25)

        weather_label = QLabel('Weather in ARMA', self)
        self.weather_combobox = QComboBox(self)
        for weather in list_options['weathers']: self.weather_combobox.addItem(weather)
        self.weather_combobox.setFixedSize(200, 25)

        line_layout = QHBoxLayout()
        line_layout.addWidget(mode_label)
        # line_layout.addSpacing(-80)
        line_layout.addWidget(self.mode_combobox)
        line_layout.addSpacing(50)
        line_layout.addWidget(map_label)
        # line_layout.addSpacing(-80)
        line_layout.addWidget(self.map_combobox)
        line_layout.addSpacing(50)
        line_layout.addWidget(weather_label)
        # line_layout.addSpacing(-40)
        line_layout.addWidget(self.weather_combobox)

        self.layout.addLayout(line_layout)

        # ====================< layer 2 >====================
        date_label = QLabel('Date', self)
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate(2024, 6, 6))
        self.date_edit.setFixedSize(200, 25)

        start_hour_label = QLabel('Start hour', self)
        self.start_hour_combobox = QComboBox(self)
        for hour in range(0, 23): self.start_hour_combobox.addItem(f'{hour}')
        self.start_hour_combobox.setFixedSize(80, 25)

        end_hour_label = QLabel('End hour in ARMA', self)
        self.end_hour_combobox = QComboBox(self)
        for hour in range(1, 24): self.end_hour_combobox.addItem(f'{hour}')
        self.end_hour_combobox.setFixedSize(80, 25)

        camera_moving_label = QLabel('Camera moving', self)
        self.camera_moving_combobox = QComboBox(self)
        for camera_moving in list_options['camera_movings']: self.camera_moving_combobox.addItem(camera_moving)
        self.camera_moving_combobox.setFixedSize(120, 25)

        line_layout = QHBoxLayout()
        line_layout.addWidget(date_label)
        line_layout.addWidget(self.date_edit)
        line_layout.addSpacing(20)
        line_layout.addWidget(start_hour_label)
        line_layout.addWidget(self.start_hour_combobox)
        line_layout.addSpacing(20)
        line_layout.addWidget(end_hour_label)
        line_layout.addWidget(self.end_hour_combobox)
        line_layout.addSpacing(20)
        line_layout.addWidget(camera_moving_label)
        line_layout.addWidget(self.camera_moving_combobox)

        self.layout.addLayout(line_layout)

        # ====================< layer 3 >====================
        class_path_label = QLabel('Class path', self)
        self.class_path_edit = QLineEdit('classes/CLASSES.csv', self)
        self.class_path_edit.setFixedSize(200, 25)

        invalid_bbox_path_label = QLabel('Invalid bbox path', self)
        self.invalid_bbox_path_edit = QLineEdit('classes/INVALID_BBOX.csv', self)
        self.invalid_bbox_path_edit.setFixedSize(300, 25)

        line_layout = QHBoxLayout()
        line_layout.addWidget(class_path_label)
        line_layout.addWidget(self.class_path_edit)
        line_layout.addSpacing(75)
        line_layout.addWidget(invalid_bbox_path_label)
        line_layout.addWidget(self.invalid_bbox_path_edit)

        self.layout.addLayout(line_layout)

        # ====================< layer 4 >====================
        username_label = QLabel('Username', self)
        self.username_edit = QLineEdit(os.getlogin(), self)
        self.username_edit.setFixedSize(250, 25)

        n_times_label = QLabel('Target number of scenes', self)
        self.n_times_edit = QLineEdit('500', self)
        self.n_times_edit.setFixedSize(200, 25)
        self.n_times_edit.setValidator(QIntValidator(self))

        line_layout = QHBoxLayout()
        line_layout.addWidget(username_label)
        line_layout.addSpacing(-25)
        line_layout.addWidget(self.username_edit)
        line_layout.addSpacing(20)
        line_layout.addWidget(n_times_label)
        line_layout.addSpacing(-5)
        line_layout.addWidget(self.n_times_edit)

        self.layout.addLayout(line_layout)

        # ====================< layer 5 >====================
        arma_root_path_label = QLabel('Arma root path', self)
        self.arma_root_path_edit = QLineEdit(f'C:/Users/{os.getlogin()}/Documents/Arma 3', self)

        line_layout = QHBoxLayout()
        line_layout.addWidget(arma_root_path_label)
        line_layout.addSpacing(20)
        line_layout.addWidget(self.arma_root_path_edit)

        self.layout.addLayout(line_layout)

        # ====================< layer 6 >====================
        save_root_path_label = QLabel('Save root path', self)
        self.save_root_path_edit = QLineEdit(f'C:/Users/{os.getlogin()}/Desktop/AMOD_{os.getlogin()}', self)

        line_layout = QHBoxLayout()
        line_layout.addWidget(save_root_path_label)
        line_layout.addSpacing(22)
        line_layout.addWidget(self.save_root_path_edit)

        self.layout.addLayout(line_layout)

        # ====================< layer 7 >====================
        min_label = QLabel('Look angles: min', self)
        self.min_spinbox = QSpinBox(self)
        self.min_spinbox.setRange(-180, 180)
        self.min_spinbox.setValue(0)
        self.min_spinbox.setFixedSize(50, 25)

        max_label = QLabel('max', self)
        self.max_spinbox = QSpinBox(self)
        self.max_spinbox.setRange(-180, 180)
        self.max_spinbox.setValue(2)
        self.max_spinbox.setFixedSize(50, 25)

        interval_label = QLabel('interval', self)
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setRange(-180, 180)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setFixedSize(50, 25)

        line_layout = QHBoxLayout()
        line_layout.addWidget(min_label)
        line_layout.addSpacing(10)
        line_layout.addWidget(self.min_spinbox)
        line_layout.addSpacing(140)
        line_layout.addWidget(max_label)
        line_layout.addSpacing(0)
        line_layout.addWidget(self.max_spinbox)
        line_layout.addSpacing(140)
        line_layout.addWidget(interval_label)
        line_layout.addSpacing(20)
        line_layout.addWidget(self.interval_spinbox)

        self.layout.addLayout(line_layout)

        # ====================< layer 8 >====================
        spatial_resolution_label = QLabel('Spatial resolution (m/pix)', self)
        self.spatial_resolution_edit = QLineEdit('0.3', self)
        self.spatial_resolution_edit.setFixedSize(100, 25)
        self.spatial_resolution_edit.setValidator(QDoubleValidator(self))

        z_atl_label = QLabel('Camera height (Z_atl)', self)
        self.z_atl_edit = QLineEdit('120', self)
        self.z_atl_edit.setFixedSize(100, 25)
        self.z_atl_edit.setValidator(QIntValidator(self))

        cam_fov_label = QLabel('Camera FOV in ARMA', self)
        self.cam_fov_edit = QLineEdit('0.8', self)
        self.cam_fov_edit.setFixedSize(100, 25)
        self.cam_fov_edit.setValidator(QDoubleValidator(self))

        line_layout = QHBoxLayout()
        line_layout.addWidget(spatial_resolution_label)
        line_layout.addWidget(self.spatial_resolution_edit)
        line_layout.addSpacing(5)
        line_layout.addWidget(z_atl_label)
        line_layout.addWidget(self.z_atl_edit)
        line_layout.addSpacing(5)
        line_layout.addWidget(cam_fov_label)
        line_layout.addWidget(self.cam_fov_edit)

        self.layout.addLayout(line_layout)

        # ====================< layer 9 >====================
        sampling_label = QLabel('Sampling (scaling) in ARMA', self)
        self.sampling_combobox = QComboBox(self)
        for sampling_ in list_options['samplings']: self.sampling_combobox.addItem(sampling_)
        self.sampling_combobox.setFixedSize(100, 25)

        screen_height_label = QLabel('Screen height', self)
        self.screen_height_edit = QLineEdit('480', self)
        self.screen_height_edit.setFixedSize(65, 25)
        self.screen_height_edit.setValidator(QIntValidator(self))

        screen_width_label = QLabel('Screen width', self)
        self.screen_width_edit = QLineEdit('640', self)
        self.screen_width_edit.setFixedSize(65, 25)
        self.screen_width_edit.setValidator(QIntValidator(self))

        line_layout = QHBoxLayout()
        line_layout.addWidget(sampling_label)
        line_layout.addWidget(self.sampling_combobox)
        line_layout.addSpacing(20)
        line_layout.addWidget(screen_height_label)
        line_layout.addWidget(self.screen_height_edit)
        line_layout.addSpacing(20)
        line_layout.addWidget(screen_width_label)
        line_layout.addWidget(self.screen_width_edit)

        self.layout.addLayout(line_layout)

        # --------------------< Separation >--------------------
        separator = QFrame(self)
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        self.layout.addWidget(separator)

        # ====================< layer 10 & 11 >====================
        script_data_button = QPushButton('🖊️️ Script generation && data creation', self)
        script_data_button.clicked.connect(lambda: self.command_window.setText(self.get_command()))
        # script_data_button.clicked.connect(lambda: pyperclip.copy(self.command_window.toPlainText()))

        self.data_button = QPushButton('🖊️ Data creation with pre-generated script', self)
        self.data_button.setEnabled(False)
        self.data_button.clicked.connect(lambda: self.command_window.setText(self.get_command() + ' -data_creation_only'))
        # data_button.clicked.connect(lambda: pyperclip.copy(self.command_window.toPlainText()))
        script_data_button.clicked.connect(self.enable_data_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(QLabel('(1) Generate command for', self))
        button_layout.addSpacing(5)
        button_layout.addWidget(script_data_button)
        button_layout.addWidget(self.data_button)

        self.layout.addLayout(button_layout)

        ############################################################
        self.command_window = QTextEdit() # QLabel(self)
        self.command_window.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.command_window)

        # =================< layer 12 & 13 >========================
        self.run_cmd_button = QPushButton('🏃 Click to Run', self)
        self.run_cmd_button.setEnabled(False)
        self.run_cmd_button.clicked.connect(self.run_command)

        script_data_button.clicked.connect(self.enable_run_cmd_button)
        self.data_button.clicked.connect(self.enable_run_cmd_button)

        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(QLabel('(2) Run the command?', self))
        button_layout2.addSpacing(20)
        button_layout2.addWidget(self.run_cmd_button)
        self.layout.addLayout(button_layout2)

        # ====================< layer 14 >=====================
        self.notice_window = None

        # ====================< Create GUI >====================
        self.central_widget.setLayout(self.layout)
        self.setGeometry(100, 100, 700, 500)
        self.setWindowTitle('AMOD-DataGen')
        self.show()

    def enable_data_button(self):
        self.data_button.setEnabled(True)

    def enable_run_cmd_button(self):
        self.run_cmd_button.setEnabled(True)

    def get_command(self):
        return ' '.join([
            f'python main.py',
            f'-mode "{self.mode_combobox.currentText()}" '
            f'-map_name "{self.map_combobox.currentText()}"',
            f'-weather "{self.weather_combobox.currentText()}"',
            f'-start_hour {self.start_hour_combobox.currentText()}',
            f'-end_hour {self.end_hour_combobox.currentText()}',
            f'-n_times {self.n_times_edit.text()}',
            f'-camera_moving "{self.camera_moving_combobox.currentText()}"',
            f'-class_path "{self.class_path_edit.text()}"',
            f'-invalid_bbox_path "{self.invalid_bbox_path_edit.text()}"',
            f'-look_angle_min {self.min_spinbox.value()}',
            f'-look_angle_max {self.max_spinbox.value()}',
            f'-look_angle_interval {self.interval_spinbox.value()}',
            f'-arma_root_path "{self.arma_root_path_edit.text()}"',
            f'-save_root_path "{self.save_root_path_edit.text()}"',
            f'-z_atl {self.z_atl_edit.text()}',
            f'-spatial_resolution {self.spatial_resolution_edit.text()}',
            f'-screen_h {self.screen_height_edit.text()}',
            f'-screen_w {self.screen_width_edit.text()}',
            # f'-spatial_resolution {round(float(self.spatial_resolution_edit.text())/(int(self.sampling_combobox.currentText()[:-1])/100), 2)}', # automatically change spatial rate due to sampling
            # f'-screen_h {round(int(self.screen_height_edit.text())*(int(self.sampling_combobox.currentText()[:-1])/100))}',
            # f'-screen_w {round(int(self.screen_width_edit.text())*(int(self.sampling_combobox.currentText()[:-1])/100))}',
            f'-sampling "{self.sampling_combobox.currentText()}"',
            f'-date "{self.date_edit.date().toString("yyyy-MM-dd")}"',
            f'-fov {self.cam_fov_edit.text()}',
        ])

    def run_command(self):
        if sys.platform == "win32":
            # os.system('start')
            # os.system(f'start {self.command_window.toPlainText()}') # Use subprocess instead of os.system
            subprocess.run(f'start {self.command_window.toPlainText()}', shell=True)
            if self.notice_window is None:
                self.notice_window = QTextEdit()
                self.layout.addWidget(self.notice_window)
            self.notice_window.setText(f'{self.notice_window.toPlainText()}'
                                       f'📢 The [Run] button was clicked '
                                       f'on {datetime.now().strftime("%y-%m-%d %H:%M:%S")} \n')
            if self.sampling_combobox.currentText() != '100%':
                spatial_resolution = round(float(self.spatial_resolution_edit.text())/
                                           (int(self.sampling_combobox.currentText()[:-1])/100), 2)
                self.notice_window.setText(f'{self.notice_window.toPlainText()}'
                                           f' ↳ Now the spatial resolution is {spatial_resolution} m/pix '
                                           f'due to your request to virtually rescale the ARMA resolution '
                                           f'by {self.sampling_combobox.currentText()} \n')
        else:
            raise NotImplementedError("Unsupported platform, Only Windows supported")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('figs/AMOD-DataGen-Icon.svg'))
    viewer = DataGenGUI()
    sys.exit(app.exec_())
