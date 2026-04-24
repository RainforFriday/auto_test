import pyvisa as visa
class GPIB:
    def __init__(self,comport=6):
        self.PortNum = comport
        self.ser = None




