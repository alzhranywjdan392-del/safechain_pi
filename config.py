# إعدادات الشاحنة
TRUCK_ID = "TRUCK_001"

# إعدادات MQTT
MQTT_BROKER = " 192.168.56.1"
MQTT_PORT = 1883
MQTT_TOPIC = f"safechain/{TRUCK_ID}/sensors"
MQTT_CLIENT_ID = f"{TRUCK_ID}_Client"

# إعدادات الأجهزة (GPIO Pins)
PIN_MQ135 = 17
PIN_MQ9 = 27

# إعدادات GPS
GPS_SERIAL_PORT = "/dev/serial0"
GPS_BAUDRATE = 9600
