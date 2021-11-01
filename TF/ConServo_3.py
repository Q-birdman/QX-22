from machine import Pin,PWM,UART
import utime

servo_ele = PWM(Pin(28))
servo_rud = PWM(Pin(27))

servo_ele.freq(50)
servo_rud.freq(50)

uart = UART(0, tx = Pin(16), rx = Pin(17))
#servo_ele.duty_u16(int(4968))

rud_array = []
ele_array = []

#配列に格納する
def read():
  if uart.any()>0:
      readdata = uart.read(0x05).decode("UTF-8")
      #print(readdata)
  if "e" in readdata:
    ele_array.append(int(readdata.replace("e","")))
    #print(readdata.replace("e",""))
    #print(ele_array)
  elif "r" in readdata:
    rud_array.append(int(readdata.replace("r","")))
    #print(rud_array)

#エレベータの配列から値を取得し、サーボを動かす
def elevator():
  if len(ele_array) > 0:
    ele_dig = ele_array.pop(0)
    #print(type(ele_dig))
    #print(ele_array)
    servo_ele.duty_u16(int(ele_dig))
    print("elevator:"+str(ele_dig))
  else:
    pass

#ラダーの配列から値を取得し、サーボを動かす
def rudder():
  if len(rud_array) > 0:
    rud_dig = rud_array.pop(0)
    servo_rud.duty_u16(int(rud_dig))
    print("rudder:"+str(rud_dig))
  else:
    pass

#たまり過ぎたら削除してラグを小さくする
def check(array):
    if len(array) > 10:
        array = []
    else:
        pass
        
while True:
    try:  
        check(ele_array)
        check(rud_array)
        read()
    except:
        print("read error")
        pass
    
    try:
      elevator()
      rudder()
    except:
        print("servo error")
        pass
  
    utime.sleep_ms(10)