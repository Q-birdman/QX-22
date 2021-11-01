from machine import UART, Pin
import utime

BAUT_RATE = 115200

uart = UART(1, BAUT_RATE, tx = Pin(8), rx = Pin(9))
data = 1000000
while True:
    data = 1 + data#utime.ticks_ms() 
    uart.write("data:" + str(data) + "data:" + str(data) + "data:" + str(data)+"\n")
    #print("data:" + str(data))
    #print(len("data:" + str(data) + "data:" + str(data) + "data:" + str(data)+"\n"))
    try:
        print(uart.read())
    except:
        pass
    if data > 5000000:
        data = 1000000
    utime.sleep_ms(1000)