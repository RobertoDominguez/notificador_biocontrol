from services.MarcacionService import marcacion_service
from services.TerminalService import terminal_service

import threading
import time

import json
import subprocess
import os

class ReleService:
    def __init__(self):
        self.hilos = []
        self.config = None
        self.config = self.read_config()
        # self.iniciarHilos()



    def read_config(self):
        """Lee el archivo de configuración JSON"""
        config_file = "config_rele.json"
        
        if not os.path.exists(config_file):
            print(f"Creando archivo de configuración: {config_file}")
            default_config = {
                            "exe": "C:\\RelayCmd.exe",
                            "rele_version" : 1,
                            "rele": {
                                "1": {
                                    "1": {
                                        "serial_reloj" : "",
                                        "duracion_pulso" : 1
                                    },
                                    "2": {
                                        "serial_reloj" : "",
                                        "duracion_pulso" : 1
                                    }
                                    },
                                    "2": {
                                    "1": {
                                        "serial_reloj" : "",
                                        "duracion_pulso" : 1
                                    }
                                }
                            }
                        }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            print("Por favor edita config.json y vuelve a ejecutar el script")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("Configuración leída correctamente:")
            return config
        except Exception as e:
            print(f"Error leyendo config.json: {e}")
            return None

    def iniciarHilos(self):
        terminales = terminal_service.getTerminales()
        for t in terminales:
            #iniciar nuevo hilo para terminal
            hilo_terminal = threading.Thread(target=self.worker, args=(t['name'],))
            hilo_terminal.daemon = True  # Para que el hilo se cierre cuando el programa principal cierre
            hilo_terminal.start()
            self.hilos.append(hilo_terminal)
    
    def worker(self,terminalName):
        while True:
            marcacion = marcacion_service.verificarMarcacion(terminalName,relay=True, funcion = self.abrirRelay)
            time.sleep(1)  # Esperar 1 segundos

    def abrirRelay(self, marcacion):
        if marcacion != None:
            serial_reloj = ""
            duracion_pulso = 0
            ID_Rele = 0
            ReleN = 0

            if marcacion.habilitado == 0 or marcacion.habilitado == False or marcacion.habilitado == '0':
                return

            for ID in self.config['rele']:
                for ReleNumber in self.config['rele'][ID]:
                    if self.config['rele'][ID][ReleNumber]['serial_reloj'] == str(marcacion.terminalCode):
                        serial_reloj = self.config['rele'][ID][ReleNumber]['serial_reloj']
                        duracion_pulso = self.config['rele'][ID][ReleNumber]['duracion_pulso']
                        ID_Rele = ID
                        ReleN = ReleNumber

            if serial_reloj != "":
                try:

                    # RelayCmd
                    if self.config['rele_version'] == 1:
                        print("Abriendo Relay: "+ str(marcacion.terminalCode) + " t=" + str(ID_Rele) + " r="+str(ReleN) )

                        cmd = [
                            self.config['exe'],
                            f"ID={ID_Rele}", # ID=Nro Placa
                            f"ON={ReleN}"    # ON=1,2,3,4 abre los rele 1,2,3,4, tambien puede abrir uno solo
                        ]

                        process = subprocess.Popen(cmd)

                        time.sleep(duracion_pulso)

                        cmd = [
                            self.config['exe'],
                            f"ID={ID_Rele}",
                            f"OFF={ReleN}"
                        ]

                        process = subprocess.Popen(cmd)

                    # RelayOpener
                    if self.config['rele_version'] == 2:
                        print("Abriendo Relay: "+ str(marcacion.terminalCode) + " t=" + str(ID_Rele) + " r="+str(ReleN) )

                        cmd = [
                            self.config['exe'],
                            f"-t {ID_Rele}", # -t=type (1 o 2)
                            f"-r {ReleN}",    # -r=relay (1 o 2)
                            f"-s {duracion_pulso}" #seconds
                        ]

                        process = subprocess.Popen(cmd)

                        time.sleep(duracion_pulso)

                except Exception as e:
                    print(f"ERROR abriendo rele {ID_Rele}, {ReleN}: {e}")
            else:
                print("Error en configuracion, serial no encontrado " + str(marcacion.terminalCode))
        

    

rele_service = ReleService()

# RelayOpener.exe -r 1 -s 1 -t 2
# r = 1 o 2, s = segundos t = tipo