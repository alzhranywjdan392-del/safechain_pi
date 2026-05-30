import paho.mqtt.client as mqtt#مكتبه هي تفتح قنوات الاتصال وترسل الرسائل 
import json
import time
import config  # استيراد الإعدادات

class MQTTHandler:
    def __init__(self):
        self.broker = config.MQTT_BROKER#ننشا بروكر 
        self.port = config.MQTT_PORT
        self.client_id = config.MQTT_CLIENT_ID#رقم الشاحنه 
        self.topic = config.MQTT_TOPIC# الموضوع 
        
        # إنشاء العميل
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:#0 يعني الاتصال ناجحغير كذا فاشل 
            print(f"[MQTT] Connected to {self.broker}")
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def start(self):
        """بدء الاتصال """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            time.sleep(1) # انتظار بسيط للاستقرار
        except Exception as e:
            print(f"[MQTT] Connection Error: {e}")

    def publish(self, data_dict):
        """إرسال البيانات والتحقق من النجاح"""
        try:
            payload = json.dumps(data_dict)
            info = self.client.publish(self.topic, payload)
            
            # التحقق: 0 يعني نجاح الإرسال
            info.wait_for_publish() # انتظار تأكيد الإرسال (اختياري لكن مفيد للدقة)
            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Data sent successfully.")
            else:
                print(f"[MQTT] Failed to send. Code: {info.rc}")
                
        except Exception as e:
            print(f"[MQTT] Publishing Error: {e}")

    def stop(self):
        """إيقاف """
        self.client.loop_stop()
        self.client.disconnect()
