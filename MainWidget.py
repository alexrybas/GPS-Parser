from PySide6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout, QPlainTextEdit, QPushButton, QMessageBox
from PySide6 import QtCore
from geopy.distance import geodesic
from PySide6.QtGui import QFont
from Data import Data
from Parser import Parser

class MainWidget(QWidget):

    def __init__(self, device_name, device_speed):
        super().__init__()

        #variables for COM port
        self.device_name = device_name
        self.device_speed = device_speed


        self.gps_num = 0
        self.glonass_num = 0
        self.galileo_num = 0

        self.saved_latitude = 0.0
        self.saved_longitude = 0.0
        self.saved_height = None

        self.lat_difference = 0.0
        self.long_difference = 0.0
        self.height_diff = 0.0

        self.converted_lat = 0.0
        self.converted_long = 0.0
        self.distance_num = None


        self.data = Data()
        self.info = Parser(self.device_name, self.device_speed)

        #getting info from Parser
        self.info.data_signal.connect(self.update_data)
        self.info.error_signal.connect(self.show_error)

        self.draw_ui()

        #start of Parser thread
        self.info.start()
       
        #button functionality
        self.button.clicked.connect(self.save_coordinates)
     
    def calculate_distance(self): # calculates distance between saved and current coordinates

        self.current_coordinates = (round(self.converted_lat, 4), round(self.converted_long, 4))
        self.saved_coordinates = (round(self.saved_latitude, 4), round(self.saved_longitude, 4))
        self.distance_num = geodesic(self.current_coordinates, self.saved_coordinates).m
  
    def convert_coordinates(self, coordinates = 0.0, stype = str()): # converts coordinates to right format
        coordinates_str = str(coordinates)
        degrees_str = str("000")
        minutes_str = str("00.0000")

        if stype == 'lat':
            degrees_str = coordinates_str[:2]
            minutes_str = coordinates_str[2:]

        elif stype == 'long':
            degrees_str = coordinates_str[:3]
            minutes_str = coordinates_str[3:]

        if degrees_str:
            degrees = float(degrees_str)
        else:
            degrees = 0
        if minutes_str:
            minutes = float(minutes_str)
        else:
            minutes = 0


        degree_bits = minutes * 0.0167
        degrees += degree_bits
        return degrees

    def count_satellites(self, data : Data): #counting number of each satellite type

        self.gps_num = 0
        self.glonass_num = 0
        if data.all_satellite != None:
            for satellite in data.all_satellite:

                if (int(satellite) < 64):
                    self.gps_num += 1

                elif (int(satellite) >= 64):
                    self.glonass_num += 1 

    def create_label(self, text, alignment, font_size=20): 
        label = QLabel(text)
        label.setFont(QFont('Arial', font_size))

        if alignment == "center":
            label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)  # type: ignore
        elif alignment == "left":
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)    # type: ignore
        elif alignment == "right":
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)   # type: ignore
        elif alignment == "justify":
            label.setAlignment(QtCore.Qt.AlignJustify | QtCore.Qt.AlignVCenter) # type: ignore
        else:
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)    # type: ignore

        return label

    def update_data(self, data : Data): # gets data from Parser signal and writes it to UI 

        # preparing data before showing
        self.count_satellites(data)

        if self.distance_num != None:
            self.calculate_distance()

        self.altitude = data.msl_altitude

        #satellites count
        self.gps_number.setText(str(self.gps_num))

        #без костиля ніяк
        self.gps_number.setFont(QFont("Aerial", 50))
        self.gps_number.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter) # type: ignore
        #кінець костиля

        #satellites count 
        self.glonass_number.setText(str(self.glonass_num))
        self.galileo_number.setText(str(self.galileo_num))

        #coordinates
        self.converted_lat = self.convert_coordinates(data.latitude, 'lat')
        self.converted_long = self.convert_coordinates(data.longitude, 'long')

        self.latitude_num.setText(str(self.converted_lat) + ' ' + data.lat_dir)
        self.longitude_num.setText(str(self.converted_long) + ' ' + data.long_dir)
        self.height_num.setText(str(data.msl_altitude))

        #saved coordinates
        self.saved_latitude_num.setText(str(self.saved_latitude))
        self.saved_longitude_num.setText(str(self.saved_longitude))
        self.saved_height_num.setText(str(self.saved_height))

        #distance
        self.distance_number.setText(str(self.distance_num))
        
        #accuracy
        self.horizontal_accuracy_num.setText(str(data.hdop))
        self.vertical_accuracy_num.setText(str(data.vdop1))
        self.general_accuracy_num.setText(str(data.pdop))

        #satellite ID`s
        self.sat_num.setText(str(data.all_satellite))

        

        #time/date

        #calculating
        time = str(data.time)
        hh = time[0:2]
        mm = time[2:4]
        ss = time[4:9]
        self.formated_time = hh + ':' + mm + ':' + ss

        date = str(data.date)
        day = date[0:2]
        month = date[2:4]
        year = date[4:6]
        self.formated_date = day + '.' + month + '.' + year

        self.time_label.setText(self.formated_time)
        self.date_label.setText(self.formated_date)

        #terminal window
        self.msg_window.setPlainText(data.text_message)
        self.msg_window.moveCursor(self.msg_window.textCursor().End)

    def save_coordinates(self): # saves and writes coordinates by pressing button
        self.saved_latitude = self.converted_lat
        self.saved_longitude = self.converted_long
        self.saved_height = self.altitude

        self.saved_latitude_num.setText(str(self.saved_latitude))
        self.saved_longitude_num.setText(str(self.saved_longitude))
        self.saved_height_num.setText(str(self.saved_height))        
            
    def draw_ui(self): # creates UI of programm

    #creating upper part

        #GPS
        self.gps_label = self.create_label("GPS", "center", 50)
        self.gps_number = self.create_label(self, "Empty" "center", 50)

        self.gps_label.setMaximumSize(300, 150)
        self.gps_number.setMaximumSize(300, 150)
 
        #GLONASS
        self.glonass_label = self.create_label("GLO", "center", 50)
        self.glonass_number = self.create_label("Empty", "center", 50)

        self.glonass_label.setMaximumSize(300, 150)
        self.glonass_number.setMaximumSize(300, 150)

        #GALILEO
        self.galileo_label = self.create_label("GAL", "center", 50)
        self.galileo_number = self.create_label("Empty", "center", 50)

        self.galileo_label.setMaximumSize(300, 150)
        self.galileo_number.setMaximumSize(300, 150)


        #creating button
        self.button = QPushButton('Save', self)
        self.button.setFont(QFont('Aerial', 20))
        self.button.setMinimumHeight(50)


    #creating middle part

        # creating coordinates
        self.coordinates_label = self.create_label(" Coordinates: ", "left",  20)
        self.coordinates_label.setMaximumWidth(200)

        # latitude 
        self.latitude_label = self.create_label("lat:", "right", 20)
        self.latitude_num = self.create_label("Empty", "left", 20)

        # longitude
        self.longitude_label = self.create_label("long:", "right", 20)
        self.longitude_num = self.create_label("Empty", "left", 20)

        # height
        self.height_label = self.create_label("height:", "right", 20)
        self.height_num = self.create_label("Empty", "left", 20)

 
        # saved coordinates
        self.saved_coordinates_label = self.create_label(" S. Coordinates: ", "left",  20)
        self.saved_coordinates_label.setMaximumWidth(200)

        # saved latitude
        self.saved_latitude_label = self.create_label("lat:", "right", 20)
        self.saved_latitude_num = self.create_label("Empty", "left", 20)

        # saved longitude
        self.saved_longitude_label = self.create_label("long:", "right", 20)
        self.saved_longitude_num = self.create_label("Empty", "left", 20)

        # saved height
        self.saved_height_label = self.create_label("height:", "right", 20)
        self.saved_height_num = self.create_label("Empty", "left", 20)


        # distance
        self.distance_label = self.create_label(" Distance:", "left", 20)
        self.distance_number = self.create_label("Empty", "center", 20)
        self.meters_label = self.create_label(" meters", "left", 20)


        # accuracy
        self.accuracy_label = self.create_label(" Accuracy: ", "left", 20)
        self.accuracy_label.setMaximumWidth(200)

        # horizontal accuracy
        self.horizontal_accuracy_label = self.create_label("hor:", "right", 20)
        self.horizontal_accuracy_num = self.create_label("Empty", "left", 20)

        # vertical accuracy
        self.vertical_accuracy_label = self.create_label("vert:", "right", 20)
        self.vertical_accuracy_num = self.create_label("Empty", "left", 20)

        # general accuracy
        self.general_accuracy_label = self.create_label("gen:", "right", 20)
        self.general_accuracy_num = self.create_label("Empty", "left", 20)


        # list of sattelites
        self.sat_num_label = self.create_label(" Sat ID:", "left", 20)
        self.sat_num_label.setMaximumWidth(200)

        # satellite array
        self.sat_num = self.create_label("Empty","", 20)


        # date/time label
        self.time_name_label = self.create_label(" Time/date:", "left", 20)
        self.time_name_label.setMaximumWidth(200)

        # time
        self.time_label = self.create_label("00:00:00" "center", 20)

        # date
        self.date_label = self.create_label("01/01/01", "center", 20)

    #creating lower part

        # terminal window
        self.msg_window = QPlainTextEdit()

        self.msg_window.setReadOnly(True)

        self.msg_window.setMinimumHeight(350)

        self.msg_window.setFont(QFont('Arial', 20))

        self.msg_label = self.create_label("Message window:", "center", 20)




#creating layouts

    #upper part
        sat_layout = QGridLayout()

        sat_layout.addWidget(self.gps_label, 0, 0)
        sat_layout.addWidget(self.glonass_label, 0, 1)
        sat_layout.addWidget(self.galileo_label, 0, 2)

        sat_layout.addWidget(self.gps_number, 1, 0)
        sat_layout.addWidget(self.glonass_number, 1, 1)
        sat_layout.addWidget(self.galileo_number, 1, 2)

        
        # adding frame to upper layout
        frameGPS = QFrame()
        frameGPS.setFrameShape(QFrame.Box)
        sat_layout.addWidget(frameGPS, 0, 0, 2, 1)

        frameGLO = QFrame()
        frameGLO.setFrameShape(QFrame.Box)
        sat_layout.addWidget(frameGLO, 0, 1, 2, 1)

        frameGAL = QFrame()
        frameGAL.setFrameShape(QFrame.Box)
        sat_layout.addWidget(frameGAL, 0, 2, 2, 1)

    #middle part
        info_layout = QGridLayout()

        #adding coordinaes widgets
        info_layout.addWidget(self.coordinates_label, 0, 0)
        info_layout.addWidget(self.latitude_label, 0, 1)
        info_layout.addWidget(self.latitude_num, 0, 2)
        info_layout.addWidget(self.longitude_label, 0, 3)
        info_layout.addWidget(self.longitude_num, 0, 4)
        info_layout.addWidget(self.height_label, 0, 5)
        info_layout.addWidget(self.height_num, 0, 6)

        #adding coordinates frame
        frame_coordinates = QFrame()
        frame_coordinates.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_coordinates, 0, 0, 1, 7)
        
        # adding saved coordinates widget
        info_layout.addWidget(self.saved_coordinates_label, 1, 0)
        info_layout.addWidget(self.saved_latitude_label, 1, 1)
        info_layout.addWidget(self.saved_latitude_num, 1, 2)
        info_layout.addWidget(self.saved_longitude_label, 1, 3)
        info_layout.addWidget(self.saved_longitude_num, 1, 4)
        info_layout.addWidget(self.saved_height_label, 1, 5)
        info_layout.addWidget(self.saved_height_num, 1, 6)

        # adding saved coordinates frame
        frame_coordinates = QFrame()
        frame_coordinates.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_coordinates, 1, 0, 1, 7)

        



        # adding distance line
        info_layout.addWidget(self.distance_label, 2, 0)
        info_layout.addWidget(self.distance_number, 2, 1, 1, 3)
        info_layout.addWidget(self.distance_label, 2, 5)

        # adding distance frame
        frame_distance = QFrame()
        frame_distance.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_distance, 2, 0, 1, 7)

        # adding accuracy widgets
        info_layout.addWidget(self.accuracy_label, 3, 0)
        info_layout.addWidget(self.horizontal_accuracy_label, 3, 1)
        info_layout.addWidget(self.horizontal_accuracy_num, 3, 2)
        info_layout.addWidget(self.vertical_accuracy_label, 3, 3)
        info_layout.addWidget(self.vertical_accuracy_num, 3, 4)
        info_layout.addWidget(self.general_accuracy_label, 3, 5)
        info_layout.addWidget(self.general_accuracy_num, 3, 6)

        # adding accuracy frame
        frame_accuracy = QFrame()
        frame_accuracy.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_accuracy, 3, 0, 1, 7)


        # adding sat ID line
        info_layout.addWidget(self.sat_num_label, 4, 0)
        info_layout.addWidget(self.sat_num, 4, 1, 1, 6)

        # adding ID frame
        frame_ID = QFrame()
        frame_ID.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_ID, 4, 0, 1, 7)


        # adding time widgets
        info_layout.addWidget(self.time_name_label, 5, 0)
        info_layout.addWidget(self.time_label, 5, 1, 1, 2)
        info_layout.addWidget(self.date_label, 5, 3, 1, 2)

        # adding time frame
        frame_time = QFrame()
        frame_time.setFrameShape(QFrame.Box)
        info_layout.addWidget(frame_time, 5, 0, 1, 7)



    #lower layout

        #adding message window
        info_layout.addWidget(self.msg_label, 6, 0)
        info_layout.addWidget(self.button, 6, 5, 1, 2)
        info_layout.addWidget(self.msg_window, 7, 0, 3, 7)

        
    # creating general layout

        general_layout = QVBoxLayout()
        general_layout.addLayout(sat_layout)
        general_layout.addLayout(info_layout)
        self.setLayout(general_layout)

    def show_error(self, error_status): # error of disconnected COM port  
        if error_status == 1:
            QMessageBox.critical(self,"Error", "Error with COM port read.")
            self.close()
