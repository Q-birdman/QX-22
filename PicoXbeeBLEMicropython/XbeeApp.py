import XbeeBLEMicroPython
import utime
xbeeBLE = XbeeBLEMicroPython.XbeeBLEMicroPython()

array = []

while True:
    try:
        data_uart = xbeeBLE.ReceiveUART(byte = 37, pr = "d")
        if data_uart is not None:
            array.append(data_uart)
    except:
        print("UART error")
        pass
    
    if len(array)>0:
        send_data=array.pop(0)
        try:
            xbeeBLE.SendBLE(send_data)
            print(send_data)
        except:
            print("BLE error")
            pass     
    try:
        datable = xbeeBLE.ReceiveBLE()
        #xbeeBLE.SendUART(datable)
    except:
        pass
                
    utime.sleep_ms(1000)
    


