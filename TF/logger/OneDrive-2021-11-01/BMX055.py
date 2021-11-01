# BMX055
# http://akizukidenshi.com/catalog/g/gK-13010/
# https://docs.micropython.org/en/latest/library/pyb.I2C.html
# https://qiita.com/hurusu1006/items/f493ee4eb9998d5bd740

#ライブラリのインポート
from machine import SoftI2C
import utime

#グローバル変数の定義
addr_accel=0x19
addr_gyro=0x69
addr_mag=0x13

#初期化
def init(i2c):
    init_accel(i2c)
    init_gyro(i2c)
    init_mag(i2c)
def init_accel(i2c):
    i2c.writeto_mem(addr_accel, 0x0F, b'\x03') # Range = +/- 2g データシート28ページ参照
    i2c.writeto_mem(addr_accel, 0x10, b'\x08')  # Bandwidth = 7.81 Hz
    i2c.writeto_mem(addr_accel, 0x11, b'\x00')  # Normal mode, Sleep duration = 0.5ms
    utime.sleep_ms(2)
def init_gyro(i2c):
    i2c.writeto_mem(addr_gyro, 0x0F, b'\x04')  # Full scale = +/- 125 degree/s
    i2c.writeto_mem(addr_gyro, 0x10, b'\x07')  # ODR = 100 Hz
    i2c.writeto_mem(addr_gyro, 0x11, b'\x00')  # Normal mode, Sleep duration = 2ms
    utime.sleep_ms(2)
def init_mag(i2c):
    i2c.writeto_mem(addr_mag, 0x4B, b'\x83') # Soft reset
    i2c.writeto_mem(addr_mag, 0x4B, b'\x01') # Soft reset
    i2c.writeto_mem(addr_mag, 0x4C, b'\x00') # Normal Mode, ODR = 10 Hz
    i2c.writeto_mem(addr_mag, 0x4E, b'\x84') # X, Y, Z-Axis enabled
    i2c.writeto_mem(addr_mag, 0x51, b'\x04') # No. of Repetitions for X-Y Axis = 9
    i2c.writeto_mem(addr_mag, 0x52, b'\x16') # No. of Repetitions for Z-Axis = 15
    utime.sleep_ms(2)
    
#加速度
def accel(i2c):
    #配列の初期化
    data = [None] * 6
    #データの読み取り
    for i in range(6):
        readdata = i2c.readfrom_mem(addr_accel, 0x02 + i, 1)
        data[i] = int.from_bytes(readdata, 'big')
    #データの10進数化
    xAccl = ((data[1] * 256) + (data[0] & 0xF0)) / 16
    if xAccl > 2047:
        xAccl -= 4096
    yAccl = ((data[3] * 256) + (data[2] & 0xF0)) / 16
    if yAccl > 2047:
        yAccl -= 4096
    zAccl = ((data[5] * 256) + (data[4] & 0xF0)) / 16
    if zAccl > 2047:
        zAccl -= 4096
    #データの単位をｇ:重力加速度へ
    xAccl = xAccl * 0.00098  # renge +-2g
    yAccl = yAccl * 0.00098  # renge +-2g
    zAccl = zAccl * 0.00098  # renge +-2g
    #返り値
    return [xAccl, yAccl, zAccl]

#角速度
def gyro(i2c):
    data = [None] * 6
    for i in range(6):
        data[i] = int.from_bytes(i2c.readfrom_mem(addr_gyro,0x02 + i,1), 'big')
    xGyro = (data[1] * 256) + data[0]
    if xGyro > 32767:
        xGyro -= 65536
    yGyro = (data[3] * 256) + data[2]
    if yGyro > 32767:
        yGyro -= 65536
    zGyro = (data[5] * 256) + data[4]
    if zGyro > 32767:
        zGyro -= 65536
    xGyro = xGyro * 0.0038  # Full scale = +/- 125 degree/s
    yGyro = yGyro * 0.0038  # Full scale = +/- 125 degree/s
    zGyro = zGyro * 0.0038  # Full scale = +/- 125 degree/s
    return [xGyro, yGyro, zGyro]

#地磁気
def mag(i2c):
    data = [None] * 8
    for i in range(8):
        readdata = i2c.readfrom_mem(addr_mag, 0x42 + i, 1)
        data[i] = int.from_bytes(readdata, 'big')
    xMag = ((data[1] * 256) + (data[0] & 0xF8)) / 8
    if xMag > 4095:
        xMag -= 8192
    yMag = ((data[3] * 256) + (data[2] & 0xF8)) / 8
    if yMag > 4095:
        yMag -= 8192
    zMag = ((data[5] * 256) + (data[4] & 0xFE)) / 2
    if zMag > 16383:
        zMag -= 32768
    return [xMag, yMag, zMag]

"""サンプルコード

from machine import SoftI2C
import BMX055

i2c_sda=machine.Pin(12)
i2c_scl=machine.Pin(13)
i2c=SoftI2C(sda=i2c_sda, scl=i2c_scl)

BMX055.init(i2c)

a = BMX055.accel(i2c)

print(a)

"""