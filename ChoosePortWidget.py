from PySide6.QtWidgets import QGridLayout, QPushButton, QComboBox, QDialog, QMessageBox
from PySide6.QtGui import QFont
from MainWidget import MainWidget
import serial.tools.list_ports

class NullPortExeption(Exception):
    pass

class ChoosePortWidget(QDialog):
    def __init__(self):
        super().__init__()

        self.port_name = list()
        self.baudrate = ["110", "300", "600", "1200", "2400", "4800", "9600", 
                         "14400", "19200", "28800", "38400", "57600", "115200", 
                         "128000", "256000"]
        
        self.current_port = None
        self.first_time_run_flag = 1
        self.draw_ui()
        self.update_ports()

        try:
            if len(self.port_name) != 0:
                self.current_port = self.port_combobox.currentText()
                
            self.update_ports_button.clicked.connect(self.update_ports)
            self.save_port_button.clicked.connect(self.accept)

            self.port_combobox.currentTextChanged.connect(self.choose_port)
            self.baudrate_combobox.currentTextChanged.connect(self.choose_baudrate)

        except serial.SerialException:
            QMessageBox.critical(self, "Error", "Port is already in use. Try another one" )
            return
          
    def is_port_null(self):
        if len(self.port_name) == 0:
            raise NullPortExeption()
        
    def update_ports(self):

        self.ports = serial.tools.list_ports.comports()
        self.port_name.clear()
        self.port_combobox.clear()

        self.baudrate_combobox.addItems(self.baudrate)

        #writing ports names into port_name list and adding them to combobox
        if len(self.ports) != 0:

            for port in self.ports:
                self.port_name.append(port.device)

            self.port_combobox.addItems(self.port_name)
                
        else:
            if self.first_time_run_flag == 0:
                QMessageBox.critical(self, "Error", "No port available" )
        
                return
            self.first_time_run_flag = 0

        self.baudrate_combobox.setCurrentIndex(0)
        self.current_baudrate = self.baudrate_combobox.currentText()

    def draw_ui(self):

        self.setWindowTitle("Choose Com Port")

        #creating save button
        self.save_port_button = QPushButton("Save")
        self.save_port_button.setFont(QFont('Aerial', 10))
        self.save_port_button.setMinimumHeight(20)

        #creating update button
        self.update_ports_button = QPushButton("Update Ports")
        self.update_ports_button.setFont(QFont('Aerial', 10))
        self.update_ports_button.setMinimumHeight(20)

        #creating labels
        self.choose_port_label = MainWidget.create_label(self, " Choose COM Port:", "right", 15)
        self.choose_baudrate_label = MainWidget.create_label(self, " Choose Baudrate:", "right", 15)

        #creating list of ports
        self.port_combobox = QComboBox()
        self.port_combobox.setMinimumWidth(100)

        self.baudrate_combobox = QComboBox()
        self.baudrate_combobox.setMinimumWidth(100)

        #creating layout
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.choose_port_label, 0, 0)
        self.main_layout.addWidget(self.port_combobox, 0, 1)
        self.main_layout.addWidget(self.choose_baudrate_label, 1, 0)
        self.main_layout.addWidget(self.baudrate_combobox, 1, 1)
        self.main_layout.addWidget(self.update_ports_button, 2, 0)
        self.main_layout.addWidget(self.save_port_button, 2, 1)

        self.setLayout(self.main_layout)
        
    def choose_port(self):
        self.current_port = self.port_combobox.currentText()

    def choose_baudrate(self):
        self.current_baudrate = self.baudrate_combobox.currentText()

    def accept(self):

        try:
            self.is_port_null()
            
            self.device_name = self.current_port
            self.device_speed = self.current_baudrate

            super().accept()
        
        except NullPortExeption:
            QMessageBox.critical(self, "Error", "No port selected" )
            return
