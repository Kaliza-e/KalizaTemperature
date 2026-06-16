import serial
import time
import json
import paho.mqtt.client as mqtt

SERIAL_PORT = "COM6"   # ⚠️ CHANGE THIS
BAUD_RATE = 9600

MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 1883
MQTT_TOPIC = "/work_group_01/room_temp/temperature"

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print("Serial connected")

    except Exception as e:
        print("Serial error:", e)
        return

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    print("Sensor → MQTT Started")

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()

            if not line:
                continue

            print("RAW:", line)

            if "TEMP:" not in line:
                continue

            # safer parsing
            temp_part = line.split(",")[0]
            temp = float(temp_part.split(":")[1])

            payload = {
                "temperature": temp,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            client.publish(MQTT_TOPIC, json.dumps(payload))

            print("Sent:", payload)

        except Exception as e:
            print("Error:", e)

        time.sleep(0.1)

if __name__ == "__main__":
    main()