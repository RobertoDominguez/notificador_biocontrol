from models.Terminal import Terminal
import json
import os

class TerminalService:
    def __init__(self):
        self.conndbbioapp = None
        self.config = self.read_config()

    def read_config(self):
        """Lee el archivo de configuración JSON"""
        config_file = "config_qr.json"
        
        if not os.path.exists(config_file):
            print(f"Creando archivo de configuración: {config_file}")
            default_config = {
                            "qr": {
                                "1": {
                                    "nombre": "Terminal 1",
                                    "vid": "", 
                                    "pid": "",
                                },
                                "2": {
                                    "nombre": "Terminal 2",
                                    "vid": "", 
                                    "pid": "",
                                }
                            }
                        }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            print("Por favor edita config_qr.json y vuelve a ejecutar el script")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("Configuración leída correctamente:")
            return config
        except Exception as e:
            print(f"Error leyendo config.json: {e}")
            return None


    def getTerminales(self):
        terminales = []

        for nro in self.config['qr']:
                terminal = Terminal(self.config['qr'][nro]['nombre'],self.config['qr'][nro]['pid'],self.config['qr'][nro]['vid'])
                print(terminal.to_dict())
                terminales.append(terminal.to_dict())

        return terminales
    
terminal_service = TerminalService()