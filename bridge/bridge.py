import serial
import time
import paho.mqtt.client as mqtt
import os
import json

# Environment Variables
MQTT_HOST = os.getenv("MQTT_HOST", "192.168.160.105")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "mqtt-user")
MQTT_PASS = os.getenv("MQTT_PASS", "123456")
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
BAUD_RATE = 115200

# MQTT Topics
STATE_TOPIC = "homeassistant/binary_sensor/pixel6_presence/state"
CONFIG_TOPIC = "homeassistant/binary_sensor/pixel6_presence/config"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    
    # Publish Home Assistant Auto-Discovery Config
    config_payload = {
        "name": "Pixel 6 Pro Presence",
        "state_topic": STATE_TOPIC,
        "payload_on": "home",
        "payload_off": "not_home",
        "device_class": "presence",
        "off_delay": 180, # 3 minutes without seeing the phone = Away
        "unique_id": "pixel6_wifi_presence",
        "device": {
            "identifiers": ["pixel6_wifi_presence"],
            "name": "Pixel 6 Pro (WiFi Sniffer)",
            "model": "Pixel 6 Pro",
            "manufacturer": "Google"
        }
    }
    client.publish(CONFIG_TOPIC, json.dumps(config_payload), retain=True)
    print("Published Home Assistant Auto-Discovery config")

def main():
    print("Starting Serial-to-MQTT Bridge...")
    
    # Setup MQTT
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    
    while True:
        try:
            print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_start()
            break
        except Exception as e:
            print(f"Failed to connect to MQTT: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    # Setup Serial
    def connect_serial():
        while True:
            try:
                print(f"Opening serial port {SERIAL_PORT}...")
                s = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                # ESP32-S3 Native USB requires DTR to be True to send logs!
                s.dtr = True
                s.rts = True
                print("Serial port opened successfully!")
                return s
            except serial.SerialException as e:
                print(f"Failed to open serial port: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    ser = connect_serial()

    # Main Loop
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # Log the raw line for debugging (commented out to save disk space)
                # print(f"Raw: {line}")
                
                if "TARGET_DETECTED" in line:
                    print(f"Phone detected! Raw string: {line}")
                    client.publish(STATE_TOPIC, "home")
                        
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(2)
            try:
                ser.close()
            except:
                pass
            ser = connect_serial()

if __name__ == "__main__":
    main()
