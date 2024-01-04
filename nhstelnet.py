import telnetlib
import sys
import time

class TelnetFunction:
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

            self.executCommand("")
        except Exception as e:
            print("Erro ao realizar a conexao!")
            print(e)

    
    def isConnected(self):
        return self.tn.sock.fileno()
    
    def executCommand(self, command):
        self.tn.write(command.encode('ascii') + b"\r\n")
        self.tn.read_until(command.encode('ascii'))
        output = self.tn.read_very_eager().decode('ascii')  # self.tn.read_until(b">", 6).decode('utf-8')
        # print tn.read_until("!!!end!!!\r\n",3)
        return output
    def close(self):
        self.tn.close()



if __name__ == "__main__":


    try:
        host = "192.168.1.20" #example 192.168.1.12
        username = "admin" #username of your machine on Ubuntu you can use "whoami" in CLI
        password = "admin"#password of your machin
        port = 2000 #the used port
        tn = TelnetFunction(host, port, username, password)
        # tn.executCommand(input('estado')+'\b') #execute your command in the server
        while (True):
            time.sleep(10)
            print(tn.executCommand("estado"))

        tn.close() #close the connection with the server
    except Exception as e:
        print(e)
        sys.exit()


