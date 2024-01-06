import telnetlib
import sys
import time
import re
import json
import os
import paho.mqtt.client as mqtt


class Mqtt:

    def __init__(self, host, port, clientName, user="", password=""):

        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.client = mqtt.Client(clientName)

        if self.user and self.password:
            self.client.username_pw_set(self.user, self.password)

        try:
            self.client.connect(self.host, self.port)
        except Exception as e:
            print(e)
            sys.exit()

        self.start()

    def publish(self, topic, status):
        self.client.publish(topic, payload=status)

    def stop(self):
        self.client.loop_stop()
    def start(self):
        self.client.loop_start()



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
            print(self.tn.read_very_eager().decode('ascii'))
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
        return output
    def close(self):
        self.tn.close()

class HomeAssistantDevice:
    mqttHost = "192.168.1.20"
    mqttPort = 1883
    mqttUser = "ruizivo"
    mqttPass = "naodigonao"
    
    deviceBaseTopic = "home/ups"
    stateTopic = deviceBaseTopic + '/state'
    attrTopic = deviceBaseTopic + '/attributes'
    lwtTopic = deviceBaseTopic + '/LWT'
    # discoveryTopic = "homeassistant/sensor/esp32iotsensor/" + g_deviceName + "_temp" + "/config";

    def __init__(self) -> None:
        if self.mqttHost and self.mqttPort and self.deviceBaseTopic:
            self.mqtt_client = Mqtt(self.mqttHost, self.mqttPort, self.deviceBaseTopic, self.mqttUser, self.mqttPass )
        else:
            self.mqtt_client = None


    def homeAssistantDiscovery(self):
        if self.mqtt_client:
            self.mqtt_client.publish()

    def updateStatus(self, status):
        if self.mqtt_client:
            self.mqtt_client.publish(self.stateTopic, status)

    def updateAttributes(self, attr):
        if self.mqtt_client:
            self.mqtt_client.publish(self.attrTopic, attr)

class Control:
    def __init__(self):
        # mqttHost = os.getenv("MQTT_HOST")
        # mqttPort = os.getenv("MQTT_PORT")
        # mqttTopic = os.getenv("MQTT_TOPIC")
        # mqttUser = os.getenv("MQTT_USER")
        # mqttPass = os.getenv("MQTT_PASS")

        

        # if mqttHost and mqttPort and mqttTopic:
        #     self.mqtt_client = Mqtt(mqttHost, mqttPort, mqttTopic, mqttUser, mqttPass )
        # else:
        #     self.mqtt_client = None

        self.device = HomeAssistantDevice()


        try:
            telnetHost = "192.168.1.20"
            telnetUsername = "admin"
            telnetPassword = "admin"
            telnetPort = 2000
            tn = Telnet(telnetHost, telnetPort, telnetUsername, telnetPassword)
        
            while (True):
                texto = tn.executCommand("estado").replace(">", "")

                # print(texto)

                # Separando as seções
                secoes = re.split(r'\r\n\r\n+', texto.strip())

                # Convertendo cada seção em um dicionário
                dados = {}
                for secao in secoes:
                    # linhas = secao.split('\n')
                    linhas = secao.split('\r\n')
                    categoria = linhas[0].strip(':')
                    dados[categoria] = {}
                    for linha in linhas[1:]:
                        chave, valor = linha.split(':', 1)
                        dados[categoria][chave.strip()] = valor.strip()

                # Convertendo para JSON
                json_resultado = json.dumps(dados, indent=4)

                # Imprimindo o resultado
                #print(json_resultado)
                
                self.device.updateAttributes(json_resultado)
                self.device.updateStatus(self.getState(dados))


                time.sleep(10)
            tn.close() #close the connection
        except Exception as e:
            print(e)
            sys.exit()

    def getState(self, result):

        if result['Dados do equipamento']['Rede em falha'] == 'sim':
            state = 'OFF'
        elif result['Dados do equipamento']['Rede em falha'] == 'nao':
            state = 'ON'
        else:
            state = 'UNKNOW'

        return(state)




if __name__ == "__main__":
    teste = Control()