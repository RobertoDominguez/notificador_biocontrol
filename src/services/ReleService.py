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
            marcacion = marcacion_service.verificarMarcacion(terminalName,relay=True)
            self.abrirRelay(marcacion)
            time.sleep(1)  # Esperar 1 segundos

    def abrirRelay(self, marcacion):
        if marcacion != None:
            serial_reloj = ""
            duracion_pulso = 0
            ID_Rele = 0
            ReleN = 0
            for ID in self.config['rele']:
                for ReleNumber in self.config['rele'][ID]:
                    if self.config['rele'][ID][ReleNumber]['serial_reloj'] == marcacion.terminalCode:
                        serial_reloj = self.config['rele'][ID][ReleNumber]['serial_reloj']
                        duracion_pulso = self.config['rele'][ID][ReleNumber]['duracion_pulso']
                        ID_Rele = ID
                        ReleN = ReleNumber

            if serial_reloj != "":
                try:
                    print("Abriendo Relay: "+ marcacion.terminalCode + " ID=" +str(ID_Rele) + " NRO="+str(ReleN) )

                    cmd = [
                        self.config['exe'],
                        f"ID={ID_Rele}",
                        f"ON={ReleN}"
                    ]

                    process = subprocess.Popen(cmd)

                    time.sleep(duracion_pulso)

                    cmd = [
                        self.config['exe'],
                        f"ID={ID_Rele}",
                        f"OFF={ReleN}"
                    ]

                    process = subprocess.Popen(cmd)
                except Exception as e:
                    print(f"ERROR abriendo rele {ID_Rele}: {e}")
            else:
                print("Error en configuracion, serial no encontrado" + marcacion.terminalCode)
        

    

rele_service = ReleService()