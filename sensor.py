import time
import json

#  I2C وحساس الحرارة
import board
import busio
import adafruit_sht31d

#  قراءة المداخل الرقمية (GPIO)
from gpiozero import InputDevice

#  GPS
import serial
import pynmea2


TRUCK_ID = "TRUCK_001"


# تهيئة ناقل I2C
i2c = busio.I2C(board.SCL, board.SDA)

# --- حساس الحرارة والرطوبة ---
try:
    sht = adafruit_sht31d.SHT31D(i2c)
except Exception as e:
    print(f"Error initializing SHT31: {e}")
    sht = None 

# --- حساسات الغاز والباب ---
try:
    # تأكد من توصيل حساسات الغاز للمنافذ 17 و 27
    mq135_do = InputDevice(17, pull_up=False)
    mq9_do = InputDevice(27, pull_up=False)

    # حساس الباب (متصل بالمنفذ 22)

    door_sensor = InputDevice(22, pull_up=True)

except Exception as e:
    print(f"Error initializing GPIO Sensors: {e}")

# ---يقرا خطوط الطول والعرض  GPS ---
try:
    # المسار\سرعه نقل البيانات 9600\وقت الانتظار 
    gps_serial = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.5)
except Exception as e:
    print(f"Error initializing GPS: {e}")
    gps_serial = None


#داله حساس الحراره والرطوبه
def read_sht31():
    try:
        if sht:
            #هنا يقراء الحراره وال طوبه ويقرب ال 2 رقم بعد الفاصله 
            return round(sht.temperature, 2), round(sht.relative_humidity, 2)
    except Exception:
        pass
    return None, None

def read_gas_sensors():
    try:
        #   0 يعني تنبيه
        mq135_alert = bool(mq135_do.value == 0)
        mq9_alert = bool(mq9_do.value == 0)
        return mq135_alert, mq9_alert
    except Exception:
        return None, None

# داله الباب 
def read_door_status():
    try:
        print("Door Raw Value:", door_sensor.value)

#مفتوح 1 مغلق 0
        if door_sensor.value == 1:
            return "OPEN"
        else:
            return "CLOSED"

    except Exception:
        return None
#داله الموقع
def read_gps():
    latitude, longitude = None, None
    try:
        if gps_serial and gps_serial.is_open:
            line = gps_serial.readline().decode('ascii', errors='replace').strip()
#هذي الي بتجيب لي بيانات الموقع فقط 
            if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
                msg = pynmea2.parse(line)

                if msg.latitude != 0 and msg.longitude != 0:
                    latitude = msg.latitude
                    longitude = msg.longitude

    except Exception:
        pass

    return latitude, longitude


def main():
    print(f"Starting SafeChain Sensor Node for {TRUCK_ID}...")

    try:
        while True:

            #  قراءة البيانات
            temp, hum = read_sht31()
            mq135_alert, mq9_alert = read_gas_sensors()
            door_status = read_door_status()
            lat, lng = read_gps()

            # تجميع البيانات في قاموس
            payload = {
                "truck_id": TRUCK_ID,
                "temperature": temp,
                "humidity": hum,
                "mq135_gas_alert": mq135_alert,
                "mq9_gas_alert": mq9_alert,
                "door_status": door_status,
                "latitude": lat,
                "longitude": lng,
                "timestamp": int(time.time())
            }

            # تنظيف البيانات حذف القيم الفارغة
            clean_payload = {
                k: v for k, v in payload.items()
                if v is not None
            }

            #  طباعة النتيجة
            print(f"Data: {json.dumps(clean_payload)}")

            #  الانتظار 5 ثواني
            time.sleep(5)
#اذا بوقف ٍٍ
    except KeyboardInterrupt:
        print("\nStopping script...")

    finally:
        if gps_serial and gps_serial.is_open:
            gps_serial.close()

if __name__ == "__main__":
    main()
