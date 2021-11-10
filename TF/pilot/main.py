from machine import Pin,ADC,UART
import utime

switch_rud = ADC(Pin(27))

duty_base = const(65535)

RUD_MAX = duty_base*0.08846
RUD_MIN = duty_base*0.06281
RUD_NUETRAL = duty_base*0.07581505

sens = 10
convertion = sens*3.3/65535

SWITCH_MAX = 33
SWITCH_MIN = 0
SWITCH_NUETRAL = 17

step = 0.0001

uart = UART(0, 115200, tx=Pin(0), rx= Pin(1))

def map(input:int, in_max:int, in_min:int, out_max:int,out_min:int) -> int:
    res = (input-in_min)*(out_max-out_min)/(in_max-in_min) + out_min
    #print(input)
    return int(res)



def rudder():
    val = switch_rud.read_u16()*convertion
    if val>SWITCH_NUETRAL:
        dig = map(val,SWITCH_MAX,SWITCH_NUETRAL,RUD_MAX,RUD_NUETRAL)
    elif val<SWITCH_NUETRAL:
        dig = map(val,SWITCH_NUETRAL,SWITCH_MIN,RUD_NUETRAL,RUD_MIN)
    else:
        dig = RUD_NUETRAL

    return int(dig)

if __name__ == "__main__":
    while True:
        
        try:
            rud_dig = rudder()
            if rud_dig is not None:
                uart.write(str(rud_dig)+"\n")
                print(rud_dig)
        except:
            #uart.write(str(0000)+"\n")
            pass

        utime.sleep_ms(30)
