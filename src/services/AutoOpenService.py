import json
import subprocess
import time
import os
from screeninfo import get_monitors
import pyautogui
import tempfile

class AutoOpenService:

    def detect_monitors(self):
        """Detecta todos los monitores conectados"""
        try:
            monitors = get_monitors()
            print(f"Monitores detectados: {len(monitors)}")
            for i, monitor in enumerate(monitors, 1):
                print(f"  Monitor {i}: {monitor.width}x{monitor.height} en ({monitor.x}, {monitor.y})")
            return monitors
        except Exception as e:
            print(f"Error detectando monitores: {e}")
            return []



    def read_config(self):
        """Lee el archivo de configuración JSON"""
        config_file = "config_open.json"
        
        if not os.path.exists(config_file):
            print(f"Creando archivo de configuración: {config_file}")
            default_config = {
                                "exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                                "wait_time": 2,
                                "numlock" : 1,
                                "monitors": {
                                        "1": {
                                            "url": "http://localhost:8080/",
                                            "zoom": -5,
                                            "move": 0
                                        },
                                        "2": {
                                            "url": "http://localhost:8080/",
                                            "zoom": 2,
                                            "move": 1
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









    def iniciar_chrome_pantalla_completa(self,chrome_exe, monitor, monitor_num, url,wait_time, zoom_time, move_to, numlock):    
        
        # Crear una carpeta temporal para el perfil
        profile_dir = tempfile.mkdtemp(prefix=f'chrome_profile_{monitor_num}_')

        cmd = [
            chrome_exe,
            "--new-window",
            url,
            f"--app={url}",
            # f"--window-position={monitor.x},{monitor.y}",
            # f"--window-size={monitor.width},{monitor.height}",
            # "--start-maximized",
            # "--kiosk",
            "--no-first-run",
            # "--incognito",
            f"--user-data-dir={profile_dir}"
        ]
        
        print(f"Iniciando Chrome en monitor {monitor_num}...")
        process = subprocess.Popen(cmd)
        
        time.sleep(wait_time)
        

        pyautogui.press('f11')
        time.sleep(0.1)

        pyautogui.click(20,20)
        time.sleep(0.1)
        
        #si es > 0 movera hacia la derecha
        while move_to > 0:
            move_to -= 1
            print('moviendo derecha')
            time.sleep(0.1)
            pyautogui.press('numlock')  
            pyautogui.hotkey('win','shiftleft','shiftright','shift','right')
            if numlock == 1:
                pyautogui.press('numlock')  
                pyautogui.hotkey('win','shiftleft','shiftright','shift','right')

        #si es > 0 movera hacia la derecha
        while move_to < 0:
            move_to += 1
            print('moviendo izquierda')
            pyautogui.hotkey('win','shiftleft','shiftright','shift','left')
            time.sleep(0.1)


        # Resetear a 100% primero (Ctrl+0)
        pyautogui.hotkey('ctrl', '0')
        time.sleep(0.1)

        #si es > 0 hara zoom positivo
        while zoom_time > 0:
            zoom_time -= 1
            pyautogui.hotkey('ctrl', '+')
            time.sleep(0.1)
        
        #si es < 0 hara zoom negativo
        while zoom_time < 0:
            zoom_time += 1
            pyautogui.hotkey('ctrl', '-')
            time.sleep(0.1)




        return process

    def open_chrome_windows(self,monitors, config):
        """Abre ventanas de Chrome en los monitores configurados"""
        # chrome_exe = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        chrome_exe = config['exe']


        if not chrome_exe:
            print("ERROR: No se encontró Chrome instalado")
            return False
            
        processes = []
        opened_count = 0

        for monitor_num_str in config['monitors']:
            try:
                monitor_num = int(monitor_num_str)
                if monitor_num < 1 or monitor_num > len(monitors):
                    print(f"ERROR: Monitor {monitor_num} configurado pero no existe")
                    continue
                
                monitor = monitors[monitor_num - 1]
                print(f"Abriendo en Monitor {monitor_num}: {config['monitors'][monitor_num_str]['url']}")
                
                process = self.iniciar_chrome_pantalla_completa(chrome_exe,monitor,monitor_num,config['monitors'][monitor_num_str]['url'],config['wait_time'],
                                                        config['monitors'][monitor_num_str]['zoom'], config['monitors'][monitor_num_str]['move'],config['numlock'])
                processes.append(process)
                opened_count += 1
                
                time.sleep(0.1)
                
            except ValueError:
                print(f"ERROR: Número de monitor inválido: {monitor_num_str}")
            except Exception as e:
                print(f"ERROR abriendo monitor {monitor_num_str}: {e}")
        
        print(f"\nVentanas abiertas exitosamente: {opened_count}")
        return processes, opened_count

    def main(self):
        
        monitors = self.detect_monitors()
        if not monitors:
            print("No se detectaron monitores. Saliendo...")
            return
        
        print()
        
        config = self.read_config()
        if not config:
            return
        
        print()
        
        # Verificar que los monitores configurados existen
        for monitor_num_str in config['monitors'].keys():
            try:
                monitor_num = int(monitor_num_str)
                if monitor_num < 1 or monitor_num > len(monitors):
                    print(f"ERROR: Monitor {monitor_num} configurado pero no existe")
                    return
            except ValueError:
                print(f"ERROR: Número de monitor inválido: {monitor_num_str}")
                return
        
        print()
        
        # Abrir nuevas ventanas
        processes, opened_count = self.open_chrome_windows(monitors, config)

auto_open_service = AutoOpenService()