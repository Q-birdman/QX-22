
"""サンプルコード
from machine import SoftI2C
import utime
import INA219

i2c_sda = machine.Pin(12)
i2c_scl = machine.Pin(13)
i2c = SoftI2C(sda=i2c_sda, scl=i2c_scl)

a = INA219.torque(i2c)

print(a)

"""

#グローバル変数の定義
addr = 0x40 #4種類くらいから選択できる
alpha = 1.5 #キャリブレーション
beta = -33 #キャリブレーション

def Shunt_V(i2c): #返り値はシャント電圧[mV]
    readdata = i2c.readfrom_mem(addr, 0x01, 2)
    data = int.from_bytes(readdata, 'big')
    data *= 0.01 #LSB:0.01
    return data

def Shunt_I(i2c): #返り値はシャント電流[mA]
    readdata = i2c.readfrom_mem(addr, 0x01, 2)
    data = int.from_bytes(readdata, 'big')
    data *= 0.01 #LSB:0.01
    data /= 0.1 #シャント抵抗:0.1
    return data

def torque(i2c): #返り値はトルク[cm・kg]
    readdata = i2c.readfrom_mem(addr, 0x01, 2)
    data = int.from_bytes(readdata, 'big')
    data = data*alpha + beta
    return data
