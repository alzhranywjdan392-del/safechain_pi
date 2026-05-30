import time
import config

# استدعاء الدوال المعدلة من 
from sensor import read_sht31, read_gas_sensors, read_gps, read_door_status
from mqtt import MQTTHandler

def main():
    print(f"Starting SafeChain Node for {config.TRUCK_ID}...")

    # تشغيل الاتصال
    mqtt_handler = MQTTHandler()
    #يسوي اتصال عشان يرسل البيانات
    mqtt_handler.start()

    try:
        while True:
            #قراءه الحساسات
            temp, hum = read_sht31()
            mq135_alert, mq9_alert = read_gas_sensors()
            door_status = read_door_status()
            lat, lng = read_gps()

            # تحويل القيم الفارغة للحرارة والرطوبة إلى -1
            if temp is None:
                temp = -1
            if hum is None:
                hum = -1
            

            # تجهيز البيانات لارسالها عبر MQTT
            payload = {
                "truck_id": config.TRUCK_ID,
                "temperature": temp,
                "humidity": hum,
                "mq135_gas_alert": mq135_alert,
                "mq9_gas_alert": mq9_alert,
                "door_status": door_status,  
                "latitude": lat,
                "longitude": lng,
                "timestamp": int(time.time())
            }

         
            # إزالة المفاتيح التي قيمتها None أو نص فارغ ""
            clean_payload = {
                k: v for k, v in payload.items()
                if v is not None and v != ""
            }

           #طباعه البيانات في التيرمنال 
            print(f"[MAIN] Sensor Data: {clean_payload}")

            # الإرسال 
            mqtt_handler.publish(clean_payload)
#وقت الانتظار وبعدها يرسل كل 5 ثواني 
            time.sleep(5)
# هنا اذا ابغى اوقف بكنترول سي 
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
       #هنا اذا توقف باي شكل نوقف ال MQTT
        print("Shutting down connections...")
        mqtt_handler.stop()
       
        print("System stopped safely.")

if __name__ == "__main__":
    main()
