from tb_device_mqtt import TBDeviceMqttClient
import time
import serial
from random import randint

# Paramètres USB série
SENSOR_DATA_SOURCE = "file"
SERIAL_PORT = "COM9"
SERIAL_BAUDRATE = 9600
ser = None

# Configuration du client ThingsBoard
TB_SERVER = "thingsboard.cloud"
TB_PORT = 1883
DEVICE_TOKEN = "59gGlyr0WAf8hrzvQypb"

def config_serial(serial_port, baud_rate=9600):
    return serial.Serial(serial_port, baudrate=baud_rate)

def read_serial(ser):
    return ser.readline().strip().decode()

def get_sensor_data(ser):
    raw_sensor = read_serial(ser)
    print(raw_sensor)
    if raw_sensor.startswith("#"):
        sensors_data = raw_sensor.strip().split("#")[1]
        distance = sensors_data
        return  float(distance)
    else:
        print('ERROR: Obtention des valeurs du capteur Arduino via le port série')
        return None

def read_file():
    file_path = "C:/Users/Mariéta/Documents/Projet_IOT_2024/Station_nettoyage/device_data1.txt"
    try:
        with open(file_path, "r") as fd:
            sensor_data = fd.readlines()
            return sensor_data
    except FileNotFoundError:
        print(f"Le fichier '{file_path}' n'a pas été trouvé.")
        return None

def get_sensor_data_from_file(line):
    if line.startswith("#"):
        sensors_data = line.strip().split("#")[1]
        values = sensors_data
        if len(values) == 1:
            distance = values
            return float(distance)
        else:
            print('ERROR: Données du capteur non valides, nombre de valeurs incorrect.')
            return None
    else:
        print('ERROR: Données du capteur non valides')
        return None

def tb_connect(addr, port, device_token):
    return TBDeviceMqttClient(addr, port, device_token)

def send_sensor_data(client, timestamp, distance):
    telemetry_with_ts = {"ts": timestamp, "values": {"distance": distance}}
    print(f"Envoi des télémesures {telemetry_with_ts}")
    result = client.send_telemetry(telemetry_with_ts)
    if result.get() == 0:
        print("OK")
    else:
        print(f"ERREUR --> {result.get()}")

def main():
    global ser
    if SENSOR_DATA_SOURCE == "serial":
        ser = config_serial(SERIAL_PORT, SERIAL_BAUDRATE)
    elif SENSOR_DATA_SOURCE == "file":
        sensor_data_from_file = read_file()
        if sensor_data_from_file is None:
            print("Aucune donnée de capteur disponible.")
            return
        number = 0

    print(f"Connexion à {TB_SERVER}...")
    tb_client = tb_connect(TB_SERVER, TB_PORT, DEVICE_TOKEN)
    tb_client.max_inflight_messages_set(100)
    tb_client.connect()
    time.sleep(5)

    while True:
        timestamp = int(round(time.time() * 1000))
        distance = None

        if SENSOR_DATA_SOURCE == "serial":
            distance = get_sensor_data(ser)
        elif SENSOR_DATA_SOURCE == "file":
            if number < len(sensor_data_from_file):
                distance = get_sensor_data_from_file(sensor_data_from_file[number])
                print(f"Données du fichier :  Distance={distance}")
                number += 1
                if number >= len(sensor_data_from_file):
                    number = 0
            else:
                print("Fichier de données terminé. Redémarrage de la lecture des données.")
                number = 0
        elif SENSOR_DATA_SOURCE == "random":
            distance = 1 + randint(0, 1)
        if  distance is not None :
            send_sensor_data(tb_client, timestamp,  distance)

        time.sleep(5)

if __name__ == "__main__":
    main()
