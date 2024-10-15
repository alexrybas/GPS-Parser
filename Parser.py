from PySide6.QtCore import QThread, Signal
from Data import Data
import serial.tools.list_ports

GNSS_SYSTEM_TYPE_GPS = 'GN'
GNSS_SYSTEM_TYPE_GLAN = 'GL'
GNSS_SYSTEM_TYPE_GALILEO = 'GA'
GNSS_SYSTEM_TYPE_UNKNOWN = 'UN'

GNSS_MESSAGE_TYPR_GSA = 'GSA'
GNSS_MESSAGE_TYPR_GGA = 'GGA'
GNSS_MESSAGE_TYPR_RMC = 'RMC'
GNSS_MESSAGE_TYPR_UNKNOWN = 'UNKNOWN'

class Parser(QThread):

    #defying signals
    data_signal = Signal(object)
    error_signal = Signal(int)
    
    def __init__(self, device_name, device_speed):
        super().__init__()

        self.device_name = device_name
        self.device_speed = device_speed
        self.collected_data = Data()

    def parse_GGA(self, message): # collects all GGA data from message 
        self.collected_data.time = message[1]
        self.collected_data.latitude = message[2]
        self.collected_data.lat_indicator = message[3]
        self.collected_data.longitude = message[4]
        self.collected_data.lon_indicator = message[5]
        self.collected_data.position_fix_indicator = message[6]
        self.collected_data.satellites_used = message[7]
        self.collected_data.hdop = message[8]
        self.collected_data.msl_altitude = message[9]
        self.collected_data.units = message[10]

    def get_value_GGA(self): # GGA getter
        return (
                self.collected_data.time, 
                self.collected_data.latitude, 
                self.collected_data.lat_indicator, 
                self.collected_data.longitude, 
                self.collected_data.lon_indicator, 
                self.collected_data.position_fix_indicator, 
                self.collected_data.satellites_used, 
                self.collected_data.hdop, 
                self.collected_data.msl_altitude, 
                self.collected_data.units
                )
    
    def parse_GSA(self, message): # collects all GSA data from message 
        self.collected_data.mod = message[3:15]
        self.collected_data.mod1 = sorted(self.collected_data.mod)
        self.collected_data.mod1 = list(filter(None, self.collected_data.mod1))
        self.collected_data.pdop = message[15]
        self.collected_data.hdop = message[16]
        self.collected_data.vdop = message[17]
        self.collected_data.vdop1 = self.collected_data.vdop[0:4]

    def get_value_GSA(self): #GSA getter
        return (
                self.collected_data.mod, 
                self.collected_data.mod1, 
                self.collected_data.pdop, 
                self.collected_data.hdop, 
                self.collected_data.vdop1
                )

    def parse_RMC(self, message): # collects all RMC data from message
        self.collected_data.time = message[1]
        self.collected_data.lat_dir = message[4]
        self.collected_data.long_dir = message[6]
        self.collected_data.date = message[9]
        self.collected_data.mag_dec = message[10]
        self.collected_data.der_mag = message[11]
        self.collected_data.calc_coor = message[12]
        self.collected_data.coor = self.collected_data.calc_coor[0]
    
    def get_value_RMC(self): # RMC getter
        return (
                self.collected_data.time, 
                self.collected_data.date, 
                self.collected_data.mag_dec, 
                self.collected_data.der_mag, 
                self.collected_data.coor
                )
    
    def all_sat(self): # collects all satellites into one variable 
        if self.collected_data.flag == 1:
                self.collected_data.id_slot1 = self.collected_data.mod1
                self.collected_data.flag = 0
        elif self.collected_data.flag == 0:
                self.collected_data.id_slot2 = self.collected_data.mod1
                self.collected_data.flag = 1

        return self.collected_data.all_satellite
  
    def get_satellite_type(self, line):
        """
            Функція для визначення до якої системи під'єнався модуль
            :param line: str - COMMENT 
        """
        if line[:3] == '$GN':
            self.system_type = GNSS_SYSTEM_TYPE_GPS
        elif line[:3] == '$GL':
            self.system_type = GNSS_SYSTEM_TYPE_GLAN
        elif line[:3] == '$GA':
            self.system_type = GNSS_SYSTEM_TYPE_GALILEO
        else:
            self.system_type = GNSS_SYSTEM_TYPE_UNKNOWN

        return self.system_type
    
    def output_messages(self, line): # функція що визначає тип рядка та якого характеру йогоінформація
        """
            Функція для визначення який тип повідомлення видає модуль
            param line: str - COMMENT 
        """
        if line[3:6] == 'GSA':
            self.output_mes= GNSS_MESSAGE_TYPR_GSA
        elif line[3:6] == 'GGA':
            self.output_mes = GNSS_MESSAGE_TYPR_GGA
        elif line[3:6] == 'RMC':
            self.output_mes = GNSS_MESSAGE_TYPR_RMC
        else:
            self.output_mes = GNSS_MESSAGE_TYPR_UNKNOWN
        
        return self.output_mes

    def read_uart(self): # intialazing and reading data from uart 

        # initialization of port
        usb_object = serial.Serial()
        usb_object.port     = self.device_name
        usb_object.parity   = serial.PARITY_NONE
        usb_object.baudrate = self.device_speed
        usb_object.stopbits = 1
        usb_object.bytesize = 8
        usb_object.open()

        # rading port 
        while(1):
            

            try:
                line = usb_object.readline()
            except serial.SerialException:
                self.error_signal.emit(1)
                break

            line_conv = line.decode()

            # writing messages to the file 
            with open("terminal.txt", "a") as f:
                f.write(line_conv)
            
            self.collected_data.text_message += line_conv
            items =line_conv.split(',')
            self.collected_data.message = line_conv

            # whatching type of satellite we connected to
            Gxx = items[0][-3:]
            satellite_type = self.get_satellite_type(line_conv)
            self.output_messages(line_conv)

            # defying message type
            if Gxx == 'GGA':
                self.parse_GGA(items)
                self.value = self.get_value_GGA()

            elif Gxx == 'GSA':
                self.parse_GSA(items)
                self.value = self.get_value_GSA()

                self.all_sat()
                self.collected_data.new_slot = self.collected_data.id_slot1 + self.collected_data.id_slot2
                self.collected_data.all_satellite = sorted(self.collected_data.new_slot)

            elif Gxx == 'RMC':
                self.parse_RMC(items)
                self.value = self.get_value_RMC()

            self.data_signal.emit(self.collected_data)
            
            
            f.close()
                
    def run(self):
        self.read_uart()
 