import time
import json

# مكتبات I2C وحساس الحرارة
import board
import busio
import adafruit_sht31d

# مكتبة قراءة المداخل الرقمية (GPIO) لحساسات الغاز
from gpiozero import InputDevice

# مكتبات GPS
import serial
import pynmea2

# ==========================================
# 1. إعدادات عامة
# ==========================================
TRUCK_ID = "TRUCK_001"

# ==========================================
# 2. تهيئة الأجهزة (Hardware Initialization)
# ==========================================
i2c = busio.I2C(board.SCL, board.SDA)

# تهيئة حساس الحرارة والرطوبة SHT31
try:
    sht = adafruit_sht31d.SHT31D(i2c)
except Exception as e:
    print(f"Error initializing SHT31: {e}")

# تهيئة حساسات الغاز عبر GPIO (Digital Input)
try:
    mq135_do = InputDevice(17, pull_up=False)
    mq9_do = InputDevice(27, pull_up=False)
except Exception as e:
    print(f"Error initializing Gas Sensors GPIO: {e}")

# تهيئة GPS
try:
    gps_serial = serial.Serial("/dev/serial0", baudrate=9600, timeout=0.5)
except Exception as e:
    print(f"Error initializing GPS: {e}")


# ==========================================
# 3. دوال قراءة الحساسات
# ==========================================

def read_sht31():
    try:
        return round(sht.temperature, 2), round(sht.relative_humidity, 2)
    except Exception:
        return None, None

def read_gas_sensors():
   
    try:
        mq135_alert = bool(mq135_do.value == 0)
        mq9_alert = bool(mq9_do.value == 0)
        return mq135_alert, mq9_alert
    except Exception:
        return None, None

def read_gps():
    latitude, longitude = None, None
    try:
        line = gps_serial.readline().decode('ascii', errors='replace').strip()
        if line.startswith('$GPGGA') or line.startswith('$GNGGA'):
            msg = pynmea2.parse(line)
            if msg.latitude != 0 and msg.longitude != 0:
                latitude = msg.latitude
                longitude = msg.longitude
    except Exception:
        pass
    return latitude, longitude


# ==========================================
# 4. الحلقة الرئيسية (Main Loop)
# ==========================================
def main():
    print("Starting SafeChain Sensor Node (Digital Gas Mode)...")

    try:
        while True:
            temp, hum = read_sht31()
            mq135_alert, mq9_alert = read_gas_sensors()
            lat, lng = read_gps()

            payload = {
                "truck_id": TRUCK_ID,
                "temperature": temp,
                "humidity": hum,
                "mq135_gas_alert": mq135_alert,
                "mq9_gas_alert": mq9_alert,
                "latitude": lat,
                "longitude": lng,
                "timestamp": int(time.time())
            }

            clean_payload = {k: v for k, v in payload.items() if v is not None}

            print(f"Read: {json.dumps(clean_payload)}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping script...")
    finally:
        if 'gps_serial' in globals() and gps_serial.is_open:
            gps_serial.close()

if __name__ == "__main__":
    main()