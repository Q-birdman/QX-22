from machine import Pin,ADC,UART
import utime

switch_ele = ADC(Pin(28))
switch_rud = ADC(Pin(27))

duty_base = const(65535)

ELE_MAX = duty_base*0.08000
ELE_MIN = duty_base*0.06000
RUD_MAX = duty_base*0.08846
RUD_MIN = duty_base*0.06281

dig_neutral = duty_base*0.07581505
ELE_NUETRAL = duty_base*0.07581505
RUD_NUETRAL = duty_base*0.07581505

sens = 10
convertion = sens*3.3/65535

SWITCH_MAX = 32
SWITCH_MIN = 1
SWITCH_NUETRAL = 16

step = 0.0001

uart = UART(0, tx=Pin(0), rx= Pin(1))

def map(input:int, in_max:int, in_min:int, out_max:int,out_min:int) -> int:
    res = (input-in_min)*(out_max-out_min)/(in_max-in_min) + out_min
    #print(input)
    return int(res)

def elevator():
    val = switch_ele.read_u16()*convertion
    if val>SWITCH_NUETRAL:
        dig = map(val,SWITCH_MAX,SWITCH_NUETRAL,ELE_MAX,ELE_NUETRAL)
    elif val<SWITCH_NUETRAL:
        dig = map(val,SWITCH_NUETRAL,SWITCH_MIN,ELE_NUETRAL,ELE_MIN)
    else:
        dig = ELE_NUETRAL

    return int(dig)
    #servo_ele.duty_u16(dig)

def rudder():
    val = switch_rud.read_u16()*convertion
    if val>SWITCH_NUETRAL:
        dig = map(val,SWITCH_MAX,SWITCH_NUETRAL,RUD_MAX,RUD_NUETRAL)
    elif val<SWITCH_NUETRAL:
        dig = map(val,SWITCH_NUETRAL,SWITCH_MIN,RUD_NUETRAL,RUD_MIN)
    else:
        dig = RUD_NUETRAL

    return int(dig)
    #servo_rud.duty_u16(dig)
    #print(val)
    #print(dig)

while True:
#     try:
#         ele_dig = elevator()
#         #print(type(rud_dig))
#         if ele_dig is not None:
#             uart.write("e"+str(ele_dig))
#     except:
#         print("error")
#         pass
    try:
        rud_dig = rudder()
        #print(type(rud_dig))
        if rud_dig is not None:
            #uart.write("asdfg")
            uart.write(str(rud_dig)+"\n")
            print((str(rud_dig)).encode("UTF-8"))
    except:
        pass
    #uart.write("asd")
    #print("a".encode("UTF-8").decode("UTF-8"))
    #print( str(ele_dig) + "," + str(rud_dig))
    

    utime.sleep_ms(10)











