import time
import config

# استدعاء الدوال المعدلة من sensor.py
from sensor import read_sht31, read_gas_sensors, read_gps, read_door_status
from mqtt import MQTTHandler

def main():
    print(f"Starting SafeChain Node for {config.TRUCK_ID}...")

    # تشغيل الاتصال
    mqtt_handler = MQTTHandler()
    mqtt_handler.start()

    try:
        while True:
            # ========= 1. قراءة الحساسات (تم التعديل) =========
            temp, hum = read_sht31()
            mq135_alert, mq9_alert = read_gas_sensors()
            door_status = read_door_status()  # تمت إضافة قراءة الباب
            lat, lng = read_gps()

            # ========= 2. التعديل المطلوب: حماية لو الحساس رجّع None =========
            # تحويل القيم الفارغة للحرارة والرطوبة إلى -1
            if temp is None:
                temp = -1
            if hum is None:
                hum = -1
            
            # ملاحظة: الـ GPS نتركه كما هو (None) لأن إرسال -1, -1 قد يعتبر موقعاً صالحاً خاطئاً
            # وسيتم حذفه لاحقاً عبر دالة التنظيف

            # ========= 3. تجهيز البيانات =========
            payload = {
                "truck_id": config.TRUCK_ID,
                "temperature": temp,
                "humidity": hum,
                "mq135_gas_alert": mq135_alert,
                "mq9_gas_alert": mq9_alert,
                "door_status": door_status,  # تمت إضافة حالة الباب هنا
                "latitude": lat,
                "longitude": lng,
                "timestamp": int(time.time())
            }

            # ========= 4. التعديل المطلوب: تنظيف البيانات بشكل أقوى =========
            # إزالة المفاتيح التي قيمتها None أو نص فارغ ""
            clean_payload = {
                k: v for k, v in payload.items()
                if v is not None and v != ""
            }

            # ========= 5. التعديل المطلوب: تحسين الطباعة =========
            print(f"[MAIN] Sensor Data: {clean_payload}")

            # ========= 6. الإرسال =========
            mqtt_handler.publish(clean_payload)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # ========= 7. التعديل المطلوب: الإغلاق الصحيح =========
        print("Shutting down connections...")
        mqtt_handler.stop()
        # تم حذف cleanup_sensors() لأن الدالة غير موجودة الآن
        print("System stopped safely.")

if __name__ == "__main__":
    main()