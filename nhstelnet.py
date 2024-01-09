from pickle import FALSE
import telnetlib
import sys
import time
import re
import json
import os
from types import SimpleNamespace
import paho.mqtt.client as mqtt

debug = True

class Mqtt:
    def __init__(self, host, port, clientName, user="", password=""):

        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.client = mqtt.Client(clientName)

        if self.user and self.password:
            self.client.username_pw_set(self.user, self.password)

    def publish(self, topic, payload, retain=False):
        self.client.publish(topic, payload, retain=retain)

    def willSet(self, topic, payload, retain=False):
        self.client.will_set(topic, payload=payload, retain=retain)

    def stop(self):
        self.client.loop_stop()

    def start(self):
        try:
            self.client.connect(self.host, self.port)
            self.client.loop_start()
        except Exception as e:
            print(e)
            sys.exit()

class Telnet:
    def __init__(self, host, port, username, password) -> None:
        self.connect(host, port, username, password)
    
    def connect(self, host, port, username, password):
        try:
            self.tn = telnetlib.Telnet(host, port)
            self.tn.read_until(b"Usuario: ")
            self.tn.write(username.encode('ascii') + b"\r\n")
            if password:
                self.tn.read_until(b"Senha:")
                self.tn.write(password.encode('ascii') + b"\r\n")
            
            time.sleep(1)
            self.tn.read_very_eager().decode('ascii') # "clean"
        except Exception as e:
            print("Erro ao realizar a conexao!")
            print(e)

    
    def isConnected(self):
        return self.tn.sock.fileno()
    
    def executCommand(self, command):
        self.tn.write(command.encode('ascii') + b"\r\n")
        time.sleep(1)
        self.tn.read_until(command.encode('ascii'))
        output = self.tn.read_very_eager().decode('ascii')
        return output.replace(">", "")
    def close(self):
        self.tn.close()

class HomeAssistantDevice:

    discoveryTopic = "homeassistant/{sensorType}/{deviceName}/{sensorName}/config"
    discoveryStateTopic = "{deviceName}/{sensorType}/{sensorName}/state"

    def __init__(self, data, mqttHost, mqttPort, mqttUser, mqttPass) -> None:
        if mqttHost and mqttPort:
            self.mqtt_client = Mqtt(mqttHost, mqttPort, "NHS", mqttUser, mqttPass )            
            self.homeAssistantDiscovery(data)
            self.mqtt_client.start()
        else:
            self.mqtt_client = None

    def start(self):
        self.mqtt_client.start()

    def homeAssistantDiscovery(self, data):
        if self.mqtt_client:
            deviceName = data["Identificacao do equipamento"]["Modelo"].replace(" ","")
            self.createDeviceSensor(deviceName, ["Equipamento", "sim"])
            self.will(deviceName,"binary_sensor", "Equipamento", "OFF")
            for key in data["Dados do equipamento"].items():
                self.createDeviceSensor(deviceName, key)

    def updateStatus(self, status):
        if self.mqtt_client:
            self.mqtt_client.publish(self.stateTopic, status)

    def updateAttributes(self, attr):
        if self.mqtt_client:
            self.mqtt_client.publish(self.attrTopic, attr)

    def getSensorType(self, data):

        if result['Dados do equipamento']['Rede em falha'] == 'sim':
            state = 'OFF'
        elif result['Dados do equipamento']['Rede em falha'] == 'nao':
            state = 'ON'
        else:
            state = 'UNKNOW'

        return(state)
    
    def will(self, deviceName, sensorType, sensorName, value):
        topic = self.discoveryStateTopic.replace("{deviceName}", deviceName).replace("{sensorType}", sensorType).replace("{sensorName}", "NHS_"+ sensorName )
        self.mqtt_client.willSet(topic, value)

    def sendValue(self, deviceName, sensorType, sensorName, value):
        topic = self.discoveryStateTopic.replace("{deviceName}", deviceName).replace("{sensorType}", sensorType).replace("{sensorName}", "NHS_"+ sensorName )
        self.mqtt_client.publish(topic, value)
        
        if debug:
                print(topic, value)
    
    def sendAllValues(self, data):
        deviceName = data["Identificacao do equipamento"]["Modelo"].replace(" ","")
    
        for key in data["Dados do equipamento"].items():
            
            sensorType = "sensor"
            if key[1] == "nao":
                sensorType = "binary_sensor"
                valor = "OFF"
            if key[1] == "sim":
                sensorType = "binary_sensor"
                valor = "ON"

            if(sensorType == "sensor"):
                valor, simbolo1 = self.splitNumberAndSymbol(key[1])

                
            sensorName = key[0].title().replace(" ","")
            self.sendValue(deviceName, sensorType, sensorName, valor)    

        self.sendValue(deviceName, sensorType, "Equipamento", "ON")   
        

    def createDeviceSensor(self, deviceName, sensorValue):
        if self.mqtt_client:
            sensorType = "sensor"
            if sensorValue[1] == "nao" or sensorValue[1] == "sim":
                sensorType = "binary_sensor"

            sensor = {}
            sensor["device"] = {}
            sensor["device"]["configuration_url"]="http://192.168.1.20:2001"
            sensor["device"]["model"] = deviceName
            sensor["device"]["name"] = "NHS"
            sensor["device"]["identifiers"] = deviceName,
            sensor["device"]["manufacturer"] = "NHS – Nobreaks"
            sensor["unique_id"] = "NHS_"+ sensorValue[0].title().replace(" ","")
            sensor["state_topic"] = self.discoveryStateTopic.replace("{deviceName}", deviceName).replace("{sensorType}", sensorType).replace("{sensorName}", sensor["unique_id"] )
            sensor["name"] = sensorValue[0]

            if sensorType == "sensor":
                numero1, simbolo1 = self.splitNumberAndSymbol(sensorValue[1])
                if simbolo1 == "C":
                    simbolo1 = "°C"
                sensor["unit_of_measurement"] = simbolo1
            # else:
            #     sensor["value_template"] = "{{ value_json.temperature}}",

            topic = self.discoveryTopic.replace("{deviceName}", deviceName).replace("{sensorType}", sensorType).replace("{sensorName}", sensor["unique_id"] )
                
            # print(json.dumps(sensor, indent=4))
            # print(topic)
            if debug:
                print(json.dumps(sensor, indent=4))
            self.mqtt_client.publish(topic, json.dumps(sensor, indent=4), True)

    def splitNumberAndSymbol(self, data):
        match = re.match(r"([0-9.]+)\s*([A-Za-z%]+)", data)

        if match:
            number = float(match.group(1))
            symbol = match.group(2)
            return number, symbol
        else:
            return None, None

class Control:
    def __init__(self):
        # mqttHost = os.getenv("MQTT_HOST")
        # mqttPort = os.getenv("MQTT_PORT")
        # mqttTopic = os.getenv("MQTT_TOPIC")
        # mqttUser = os.getenv("MQTT_USER")
        # mqttPass = os.getenv("MQTT_PASS")

        mqttHost = "192.168.1.20"
        mqttPort = 1883
        mqttUser = "ruizivo"
        mqttPass = "naodigonao"

        try:
            telnetHost = "192.168.1.20"
            telnetUsername = "admin"
            telnetPassword = "admin"
            telnetPort = 2000
            tn = Telnet(telnetHost, telnetPort, telnetUsername, telnetPassword)

            data = self.getInfo(tn.executCommand("estado"))
            self.device = HomeAssistantDevice(data, mqttHost, mqttPort, mqttUser, mqttPass )
        
            while (True):
                if debug:
                    print("----- begin of send -----")
                texto = tn.executCommand("estado")

                dados = self.getInfo(texto)
                self.device.sendAllValues(dados);

                if debug:
                    print("----- end of send -----")
                time.sleep(10)
                
            tn.close() #close the connection
        except Exception as e:
            print(e)
            sys.exit()

    def getInfo(self, texto):

        sections = re.split(r'\r\n\r\n+', texto.strip())

        # Convert into dictionary
        data = {}
        for section in sections:
            # linhas = secao.split('\n')
            rows = section.split('\r\n')
            category = rows[0].strip(':')
            data[category] = {}
            for linha in rows[1:]:
                key, value = linha.split(':', 1)
                data[category][key.strip()] = value.strip()

        # Convertendo para JSON
        jsonResult = json.dumps(data, indent=4)

        # print the result
        # print(jsonResult)     
        return data   


if __name__ == "__main__":
    teste = Control()
