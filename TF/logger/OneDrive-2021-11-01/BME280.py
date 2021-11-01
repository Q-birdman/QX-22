# BME280
#https://elchika.com/article/89e2c4e6-5c5a-49f7-aad4-38e52c0836bd/ i2cコード引用元
#https://qiita.com/yukataoka/items/8f9046587c978e91f689 コード引用元
#http://trac.switch-science.com/wiki/BME280 日本語使い方
#https://www.souichi.club/raspberrypi/bme280/ ざっくりコード説明
#https://micropython-docs-ja.readthedocs.io/ja/latest/library/machine.I2C.html machineのI2Cの説明

#ライブラリのインポート
from machine import I2C
import utime

#グローバル変数の定義
addr = 0x76
digT = []
digP = []
digH = []
t_fine = 0.0

#初期化
def init(i2c):
    osrs_t = 1            #Temperature oversampling x 1
    osrs_p = 1            #Pressure oversampling x 1
    osrs_h = 1            #Humidity oversampling x 1
    mode   = 3            #Normal mode
    t_sb   = 1           #Tstandby 1000ms  めちゃめちゃ重要
    filter = 0            #Filter off
    spi3w_en = 0            #3-wire SPI Disable
    ctrl_meas_reg = bytearray(1)
    config_reg    = bytearray(1)
    ctrl_hum_reg  = bytearray(1)
    ctrl_meas_reg[0] = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg[0]    = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg[0]  = osrs_h
    i2c.writeto_mem(addr,0xF2,ctrl_hum_reg)
    i2c.writeto_mem(addr,0xF4,ctrl_meas_reg)
    i2c.writeto_mem(addr,0xF5,config_reg)

#調整パラメータ取得
def get_calib_param(i2c):
    global digT, digP, digH, t_fine
    calib = []
    for i in range (0x88,0x88+24):
        readdata = i2c.readfrom_mem(addr,i,1)
        calib.append(int.from_bytes(readdata,'big'))
    readdata = i2c.readfrom_mem(addr,0xA1,1)
    calib.append(int.from_bytes(readdata,'big'))
    for i in range (0xE1,0xE1+7):
        readdata = i2c.readfrom_mem(addr,i,1)
        calib.append(int.from_bytes(readdata,'big'))
    teststr = calib[1] << 8
    teststr = calib[1] | calib[0]
    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11]<< 8) | calib[10])
    digP.append((calib[13]<< 8) | calib[12])
    digP.append((calib[15]<< 8) | calib[14])
    digP.append((calib[17]<< 8) | calib[16])
    digP.append((calib[19]<< 8) | calib[18])
    digP.append((calib[21]<< 8) | calib[20])
    digP.append((calib[23]<< 8) | calib[22])
    digH.append( calib[24] )
    digH.append((calib[26]<< 8) | calib[25])
    digH.append( calib[27] )
    digH.append((calib[28]<< 4) | (0x0F & calib[29]))
    digH.append((calib[30]<< 4) | ((calib[29] >> 4) & 0x0F))
    digH.append( calib[31] )
    for i in range(1,2):
        if digT[i] & 0x8000:
            digT[i] = (-digT[i] ^ 0xFFFF) + 1
    for i in range(1,8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1
    for i in range(0,6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1
#気圧
def press(i2c):
    global t_fine
    data = [None] * 3
    for i in range(3):
        readdata = i2c.readfrom_mem(addr,0xF7 + i,1)
        data[i] = int.from_bytes(readdata, 'big')
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    press = 0.0
    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8)  + ((digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768
    if v1 == 0:
        return 0
    press = ((1048576 - pres_raw) - (v2 / 4096)) * 3125
    if press < 0x80000000:
        press = (press * 2.0) / v1
    else:
        press = (press / v1) * 2
    v1 = (digP[8] * (((press / 8.0) * (press / 8.0)) / 8192.0)) / 4096
    v2 = ((press / 4.0) * digP[7]) / 8192.0
    press = (press + ((v1 + v2 + digP[6]) / 16.0)) / 100
    return press

#温度
def temp(i2c):
    global t_fine
    data = [None] * 3
    for i in range(3):
        readdata = i2c.readfrom_mem(addr,0xFA + i,1)
        data[i] = int.from_bytes(readdata, 'big')
    temp_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    v1 = (temp_raw / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (temp_raw / 131072.0 - digT[0] / 8192.0) * (temp_raw / 131072.0 - digT[0] / 8192.0) * digT[2]
    t_fine = v1 + v2
    temp = t_fine / 5120.0
    return temp

#湿度
def humid(i2c):
    global t_fine
    data = [None] * 2
    for i in range(2):
        readdata = i2c.readfrom_mem(addr,0xFD + i,1)
        data[i] = int.from_bytes(readdata, 'big')
    hum_raw  = (data[0] << 8)  |  data[1]
        
    humid = t_fine - 76800.0
    if humid != 0:
        humid = (hum_raw - (digH[3] * 64.0 + digH[4]/16384.0 * humid)) * (digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * humid * (1.0 + digH[2] / 67108864.0 * humid)))
    else:
        return 0
    humid = humid * (1.0 - digH[0] * humid / 524288.0)
    if humid > 100.0:
        humid = 100.0
    elif humid < 0.0:
        humid = 0.0
    return humid

"""サンプルコード
from machine import SoftI2C
import BME280
import utime

i2c_sda=machine.Pin(12)
i2c_scl=machine.Pin(13)
i2c=machine.SoftI2C(sda=i2c_sda, scl=i2c_scl)

BME280.init(i2c)
BME280.get_calib_param(i2c)

a = BME280.press(i2c)
b = BME280.temp(i2c)
c = BME280.humid(i2c)

print(a,b,c)
"""