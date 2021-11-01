import math

#グローバル変数の定義
addr=0x40

#初期化
def init(i2c):
    i2c.writeto(addr,b'\xE5')
    i2c.writeto(addr,b'\xF1')

#差圧
def deff_presure(i2c):
    data = i2c.readfrom(addr,2)
    data = int.from_bytes(data, 'big')
    if data > 32767:
        data -= 65535
    data /= 240
    return data

#大気速度
def airspeed(i2c, temp):
    data = i2c.readfrom(addr,2)
    data = int.from_bytes(data, 'big')
    if data > 32767:
        data -= 65535
    data /= 240
    data = math.sqrt(2 * data / (1.251 - temp * 0.004))
    return data

