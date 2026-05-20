import time
import config

# استدعاء الدوال من sensor.py + دالة التنظيف cleanup_sensors
from sensor import get_environment_data, get_gas_status, get_location, cleanup_sensors
from mqtt import MQTTHandler

def main():
    print(f"Starting SafeChain Node for {config.TRUCK_ID}...")

    # تشغيل الاتصال
    mqtt_handler = MQTTHandler()
    mqtt_handler.start()

    try:
        while True:
            # ========= 1. قراءة الحساسات =========
            temp, hum = get_environment_data()
            mq135_alert, mq9_alert = get_gas_status()
            lat, lng = get_location()

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
        cleanup_sensors()
        print("System stopped safely.")

if __name__ == "__main__":
    main()