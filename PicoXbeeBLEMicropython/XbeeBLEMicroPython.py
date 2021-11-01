from xbee import relay
import sys
from sys import stdin, stdout
import time

class XbeeBLEMicroPython():
    __MSG_ON = "ON"
    __MSG_OFF = "OFF"
    __MSG_ACK = "OK"
    __RELAY_MSG = {}

    # Variables
    __running = False

    def __init__(self, MSG_ON = "ON", MSG_OFF = "OFF", MSG_ACK= "OK", **RERAY_MSG) -> None:
        self.__MSG_ON = MSG_ON
        self.__MSG_OFF = MSG_OFF
        self.__MSG_ACK = MSG_ACK
        self.__RELAY_MSG = RERAY_MSG
        self.__running = False

    def getMSG(self, MSG_KEY):
        return self.__RELAY_MSG.get(key=MSG_KEY)

    def setMSG(self, MSG_KEY, MSG_VALUE):
        self.__RELAY_MSG.update({MSG_KEY:MSG_VALUE})
        return self.__RELAY_MSG       

    def BLERelay(self, MSG_REQ, MSG_RES):
        relay_frame = relay.receive()
        if relay_frame is not None:
            data = relay_frame["message"].decode("utf-8")
            # If the message starts with MSG_REQ, parse the refresh rate.
            if data.startswith(MSG_REQ):
                # Send an ACK to confirm the reception.
                relay.send(relay.BLUETOOTH, MSG_RES)

    def SendBLE(self,data):
        if self.__running :
            try:
                relay.send(relay.BLUETOOTH, data)
            except:
                pass

    def ReceiveBLE(self):
        relay_frame = relay.receive()
        if relay_frame is not None:
            data = relay_frame["message"].decode("utf-8")
            # If the message starts with "ON", parse the refresh rate.
            if data.startswith(self.__MSG_ON):
                self.__running = True
                # Send an ACK to confirm the reception.
                relay.send(relay.BLUETOOTH, self.__MSG_ACK)
            elif data.startswith(self.__MSG_OFF):
                running = False
                # Send an ACK to confirm the reception.
                relay.send(relay.BLUETOOTH, self.__MSG_ACK)
            elif self.__running and data is not None:     
                return data["message"].decode("utf-8")
            else:
                return None

    def prefix_check(data:str, pr:str):
            if data.startswith(pr):
                return True
            else:
                return False

    def ReceiveUART(self, byte:int = -1, pr:str = ""):
        readbyte = byte
        #print(readbyte)
        data = stdin.buffer.read(readbyte).decode("UTF-8")
        prefix = data.find(pr)
        #print(prefix)
        if pr not in data:
            print("not in")
            return None
        if prefix>0 and data.startswith(pr) == False:
            data = data + stdin.buffer.read(prefix)
            #print(data)
        return data
    
    
            

    def SendUART(self,data):
        if data is not None:
            stdout.buffer.write(data)