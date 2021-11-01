"""
from micropython import const
from machine import Pin, I2C, time_pulse_us
import rp2, time
import HCSR04

while True:
    x=HCSR04.distance(0,1,20)
    print(x)
"""

from micropython import const
from machine import Pin, I2C, time_pulse_us
import rp2, time

def distance(trig_PIN,echo_PIN,temperature):
    sound_speed=331.5+0.61*temperature
#trigger とechoのGPIO
    _TRIG=trig_PIN
    _ECHO=echo_PIN

#trigger とechoのGPIOの初期化
    trig=Pin(_TRIG, Pin.OUT)        #triggerを出力に
    trig.value(0)
    echo=Pin(_ECHO, Pin.IN)       #echoを入力に

    #20マイクロ秒のTriggerパルスを出す
    trig.value(1)
    time.sleep_us(20)
    trig.value(0)

    #ehcoで音波が反射して戻ってくるまでの時間を測定
    duration=time_pulse_us(echo,1,60*1000)/2      #反射時間を2で割り、片道時間に（マイクロ秒）
    distance=duration*sound_speed*100/1000000                  #片道時間かける音速で距離を出す(cm)
    time.sleep(0.1)
    return distance