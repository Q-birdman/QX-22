from machine import Pin,PWM,UART
import utime

servo_rud = PWM(Pin(11))

servo_rud.freq(50)

duty_base = const(65535)

RUD_MAX = duty_base*0.08846
RUD_MIN = duty_base*0.06281

uart = UART(0, 115200, tx = Pin(16), rx = Pin(17))

rud_array = []

#配列に格納する
def read():
  
  if uart.any()>4:
      readdata = uart.readline().decode("UTF-8")
      #print(uart.any())
      #print(readdata)
      if len(readdata) == 5 :
          rud_array.append(int(readdata))
          #print(rud_array)

#ラダーの配列から値を取得し、サーボを動かす
def rudder():
  if len(rud_array) > 0:
    rud_dig = rud_array.pop(0)
    servo_rud.duty_u16(int(rud_dig))
    print("rudder:"+str(rud_dig))

#たまり過ぎたら削除してラグを小さくする
def check(array):
    if len(array) > 3:
        array = []
    else:
        pass


while True:
    
    try:
        check(rud_array)
#         print(RUD_MAX)
#         print(RUD_MIN)
        read()
    except:
        print("read error")
        pass
    
    try:
      rudder()
    except:
        print("servo error")
        pass
  
    utime.sleep_ms(15)