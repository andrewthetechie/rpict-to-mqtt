import paho.mqtt.client as paho
import serial
import logging
import os

ser = serial.Serial(os.environ.get("SERIAL_PORT", "/dev/ttyAMA0"), 38400)
broker = os.environ.get("MQTT_HOST")
port = int(os.environ.get("MQTT_PORT", "1883"))

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()
VALUES_TO_AVERAGE = int(os.environ.get("VTA", 20))
MQTT_PATH = os.environ.get("MQTT_PATH", "rpict")
logging.basicConfig(level=LOGLEVEL)


def c_to_f(temp):
    return float((temp * 9 / 5) + 32)


def get_average(lst):
    return sum(lst) / len(lst)


def on_publish(**_):
    logging.debug("data published")


if __name__ == "__main__":
    client1 = paho.Client("control1")
    client1.on_publish = on_publish
    client1.connect(broker, port)

    logging.debug("getting %d values", VALUES_TO_AVERAGE)
    current_values = dict()

    temp_values = []
    for i in range(VALUES_TO_AVERAGE):
        # Read one line from the serial buffer
        line = ser.readline().decode("utf-8")
        # Remove the trailing carriage return line feed
        line = line[:-2]
        # Create an array of the data
        data = line.split(" ")

        # specifically for the RPICT3T1
        for i in range(3):
            sensor_address = i + 1
            if sensor_address not in current_values:
                current_values[sensor_address] = list()
            current_values[sensor_address].append(float(data[sensor_address]))
        temp_values.append(float(data[4]))
    ser.close()
    logging.debug("Got current vals and temp vals")
    logging.debug(current_values)
    logging.debug(temp_values)

    temp_avg = get_average(temp_values)
    logging.debug("Temp Avg %f", temp_avg)
    for i in range(3):
        sensor_address = i + 1
        client1.publish(
            f"{MQTT_PATH}/current/{sensor_address}",
            round(get_average(current_values[sensor_address]), 2),
        )
    client1.publish(f"{MQTT_PATH}/c", round(temp_avg, 2))
    client1.publish(f"{MQTT_PATH}/f", round(c_to_f(temp_avg), 2))
