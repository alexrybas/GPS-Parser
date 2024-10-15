class Data():
    def __init__(self):

        #variables for GGA
        self.time = None 
        self.latitude= float() 
        self.lat_indicator = None 
        self.longitude= float() 
        self.lon_indicator= None 
        self.position_fix_indicator= None 
        self.satellites_used= None 
        self.hdop= None 
        self.msl_altitude= float()
        self.units= None

        #vaiables for GSA
        self.mod = None
        self.mod1 = list()
        self.pdop = None
        self.vdop = None
        self.vdop1 = None

        #variables for RMS
        self.lat_dir = str()
        self.long_dir = str()
        self.time = None
        self.date = None
        self.day = None
        self.month = None
        self.year = None
        self.mag_dec = None
        self.der_mag = None
        self.calc_coor = None
        self.coor = None

        #Other variables
        self.flag = 1
        self.id_slot1 = []
        self.id_slot2 = []
        self.all_satellite = []
        self.new_slot = []
        self.message = str()

        self.text_message = str()
 