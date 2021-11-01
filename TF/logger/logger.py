'''
----仕様----
・センサで読み取った値をSDカードにプログラム起動時からの時間とともに記録しそれをPCのshellに表示する
・パソコンに接続していない場合SDカードに保存だけする
・「FIND_'使うセンサ名' = True」 でそのセンサを使用でき、読み取ったデータを保存する
・True に設定したセンサが最初から接続できない場合そのセンサの値を0として実行する
・Falseに設定したセンサは最初から0を読み取った値として保存する
・SDカードをfalseとした場合データは記録されずshellにのみ表示される
・SDカードをTrueにしたがSDカードに接続できない場合プログラムは実行されずSDカードを探し続ける
・所得するデータは加速度(x,y,z), 角速度(x,y,z), 地磁気(x,y,z), 気圧, 温度, 湿度, トルク, 対気速度
'''


#ライブラリのインポート
from machine import Pin, SPI, I2C, freq, PWM, UART
import utime, uos, sys
import MPU9250, BME280, INA219, SDP6x, sdcard
​
​
​
#使うセンサ
FIND_MPU9250 = True
FIND_BME280 = True
FIND_INA219_a = True
FIND_INA219_b = False
FIND_SDP6x = False
FIND_SDCARD = False
​
​
​
#変数の定義
fileName = 'rog'
READ_MPU9250 = False
READ_BME280 = False
READ_INA219_a = False
READ_INA219_b = False
READ_SDP6x = False
WRITE_SDCARD = False
data = [0] * 16
acc = [0] * 3
gyr = [0] * 3
mag = [0] * 3
prs = 0
tem = 0
hum = 0
trq_a = 0
trq_b = 0
asp = 0
​
​
​
#確認用lチカ関数
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1)
    set(x, 31)                  [14]
    label("delay_high")
    nop()                       [28]
    nop()                       [31] 
    jmp(x_dec, "delay_high")
    
    set(pins, 0)
    set(x, 31)                  [14]
    label("delay_low")
    nop()                       [28]
    nop()                       [31]
    jmp(x_dec, "delay_low")
    wrap()
sm = rp2.StateMachine(0, blink, freq=10000, set_base=Pin(25))
​
​
​
#CPU周波数の設定
freq(273000000)
​
#ピン配置
led = Pin(25,Pin.OUT)
i2c_a = I2C(0,scl = Pin(13), sda = Pin(12), freq = 750000)
i2c_b = I2C(1,scl = Pin(27), sda = Pin(26), freq = 750000)
spi = SPI(0,sck = Pin(18),mosi = Pin(19),miso = Pin(16))
​uart = UART(1, 115200, tx = Pin(8), rx = Pin(9))
#時間の初期値取得
timeBase = utime.ticks_ms()
​
#起動時の確認, LEDが光る
led.value(1)
​
​
​
#-------------------SDcard とパスの確認-------------------#
if  FIND_SDCARD:
    
    #SDカードへのマウント
    while FIND_SDCARD:
        try:
            spi = SPI(0)
            sd = sdcard.SDCard(spi, Pin(28))
            uos.mount(sd, '/sd')
            uos.chdir('sd')
            uos.listdir()
            FIND_SDCARD = False
            WRITE_SDCARD = True
            dirpath = uos.getcwd() + '/data'
            
        except:
            print("no sdcard")
            utime.sleep_ms(10)

    #txtファイルを入れるディレクトリを作成
    try:
        uos.mkdir(dirpath)
    except :
        print('data folder is already exists')
    finally:
        uos.chdir(dirpath)
        
    #ログテクストファイルの生成, 300個まで
    count = False
    for i in range(1,300):
        try:
            filpath = uos.getcwd() + '/' + fileName + str(i) + '.txt'
            file = open(filpath, 'x')
            count = True
        except:
            i += 1
        finally:
            if count:
                break
    """if i == 300:
        print("datatext is over")
        sys.exit()"""
    print(filpath)
​
​
#-------------------センサの初期設定-------------------#
#MPU9250の初期設定
if FIND_MPU9250:
    for i in range(10):
        try:
            MPU9250.init(i2c_a)
            READ_MPU9250 = True
            FIND_MPU9250 = False
            break
        except:
            utime.sleep_ms(10)
            print("searching MPU9250")
​
#BME280の初期設定
if FIND_BME280:
    for i in range(10):
        try:
            BME280.init(i2c_a)
            READ_BME280 = True
            FIND_BME280 = False
            break
        except:
            utime.sleep_ms(10)
            print("searching BME280")
            
#INA219の初期設定
if FIND_INA219_a:
    for i in range(10):
        try:
            i = INA219.Shunt_V(i2c_b, 0x40)
            READ_INA219_a = True
            FIND_INA219_a = False
            break
        except:
            utime.sleep_ms(10)
            print("searching INA219_a")
            
if FIND_INA219_b:
    for i in range(10):
        try:
            i = INA219.Shunt_V(i2c_b, 0x41)
            READ_INA219_b = True
            FIND_INA219_b = False
            break
        except:
            utime.sleep_ms(10)
            print("searching INA219")
            
#SDP6xの初期設定
if FIND_SDP6x:
    for i in range(10):
        try:
            SDP6x.init(i2c_a)
            READ_SDP6x = True
            FIND_SDP6x = False
            break
        except:
            utime.sleep_ms(10)
            print("searching SDP6x")
​
​
#-------------------メインループ-------------------#
sm.active(1) #lチカ
​
for i in range(10):
        try:
            acc = MPU9250.accel(i2c_a)
            gyr = MPU9250.gyro(i2c_a)
            mag = MPU9250.magnet(i2c_a)
            break
        except:
            utime.sleep_ms(10)
            print("searching MPU9250")
​
​
while True:
    #センサ値の取得
    if READ_MPU9250:
        try:
            acc = MPU9250.accel(i2c_a)
            gyr = MPU9250.gyro(i2c_a)
            mag = MPU9250.magnet(i2c_a)
        except:
            print("can't find MPU9250")
            
    if READ_BME280:
        try:
            prs = BME280.press(i2c_a)
            tem = round(BME280.temp(i2c_a),1)
            hum = round(BME280.humid(i2c_a),1)
        except:
            print("can't find BME280")
            
    if READ_INA219_a:
        try:
            trq_a = INA219.torque(i2c_b, 0x40)
        except:
            print("can't find INA219_a")
            
    if READ_INA219_b:
        try:
            trq_b = INA219.torque(i2c_b, 0x41)
        except:
            print("can't find INA219_b")
            
    if READ_SDP6x:
        try:
            asp = SDP6x.airspeed(i2c_a, 25)
        except:
            print("can't find SDP6x")
            
    Time = utime.ticks_diff(utime.ticks_ms(), timeBase) / 1000
    
    data[0] = Time
    data[1] = acc[0]
    data[2] = acc[1]
    data[3] = acc[2]
    data[4] = gyr[0]
    data[5] = gyr[1]
    data[6] = gyr[2]
    data[7] = mag[0]
    data[8] = mag[1]
    data[9] = mag[2]
    data[10] = prs
    data[11] = round(tem, 1)
    data[12] = round(hum, 1)
    data[13] = trq_a
    data[14] = trq_b
    data[15] = round(asp, 2)
    print("機速:{:x}\n".format(data[15]))
    print(len("機速:{:x}\n".format(data[15])))
    #SDカードへの出力
    #output = str(Time) + "," + str(acc[0]) + "," + str(acc[1]) + "," + str(acc[2]) + "," + str(gyr[0]) + "," + str(gyr[1]) +"," + str(gyr[2]) + "," + str(mag[0]) + "," + str(mag[1]) + "," + str(mag[2]) + "," + str(prs) + "," + str(tem) + "," + str(hum) + "," + str(trq_a) +"," + str(trq_b) + "," + str(asp) + "\n"
    print(data)
    if WRITE_SDCARD:
        try:
            file.write(str(data) + "\n")
            file.flush()
        except:
            print("can't find SDCARD")
            
    #待機時間
    #utime.sleep_ms(100)