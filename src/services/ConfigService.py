class ConfigService:
    def __init__(self, config_file='config'):
        self.config_file = config_file
        self.config = 0
        self.grupo = ''

        self.driver = ''
        self.host = ''
        self.port = 0
        self.database = ''
        self.user = ''
        self.password = ''

        self.driver2 = ''
        self.host2 = ''
        self.port2 = 0
        self.database2 = ''
        self.user2 = ''
        self.password2 = ''

        self.sistema = 0
        self.web_port = 0
        self.path_images = ''
        self.extension_images = ''
        self.seconds_notification = 0
        self.cache_time = 60
        self.dias_alerta = 3
        self.logo_path = ''
        self.nombre_gym = ''
        self.fondo_path = ''
        self.web_enabled = 0
        self.rele_enabled = 0

        self.getConfigs()

    def getConfigs(self):
        """Obtiene las configuraciones del archivo"""
        print('obteniendo configuraciones')
        try:
            with open(self.config_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'CONFIG':
                            self.config = int(value) if value.isdigit() else 0
                        elif key == 'GRUPO':
                            self.grupo = value

                        elif key == 'DRIVER':
                            self.driver = value
                        elif key == 'HOST':
                            self.host = value
                        elif key == 'DATABASE':
                            self.database = value
                        elif key == 'PORT':
                            self.port = int(value) if value.isdigit() else 1433
                        elif key == 'USER':
                            self.user = value
                        elif key == 'PASSWORD':
                            self.password = value

                        if key == 'CONFIG2':
                            self.config2 = int(value) if value.isdigit() else 0
                        elif key == 'DRIVER2':
                            self.driver2 = value
                        elif key == 'HOST2':
                            self.host2 = value
                        elif key == 'DATABASE2':
                            self.database2 = value
                        elif key == 'PORT2':
                            self.port2 = int(value) if value.isdigit() else 1433
                        elif key == 'USER2':
                            self.user2 = value
                        elif key == 'PASSWORD2':
                            self.password2 = value

                        elif key == 'SISTEMA':
                            self.sistema = int(value) if value.isdigit() else 1
                        elif key == 'WEB_PORT':
                            self.web_port = int(value) if value.isdigit() else 8080
                        elif key == 'PAHT_IMAGES':
                            self.path_images = value
                        elif key == 'EXTENSION_IMAGES':
                            self.extension_images = value
                        elif key == 'SECONDS_NOTIFICATION':
                            self.seconds_notification = int(value) if value.isdigit() else 10
                        elif key == 'CACHE_TIME':
                            self.cache_time = int(value) if value.isdigit() else 60
                        elif key == 'DIAS_ALERTA':
                            self.dias_alerta = int(value) if value.isdigit() else 3
                        elif key == 'LOGO_PATH':
                            self.logo_path = value
                        elif key == 'NOMBRE_GYM':
                            self.nombre_gym = value
                        elif key == 'FONDO_PATH':
                            self.fondo_path = value

                        elif key == 'WEB_ENABLED':
                            self.web_enabled = int(value) if value.isdigit() else 1
                        elif key == 'RELE_ENABLED':
                            self.rele_enabled = int(value) if value.isdigit() else 1

            return True
        except FileNotFoundError:
            print(f"Error: Archivo de configuración '{self.config_file}' no encontrado, creando archivo...")
            self.setConfigs(0,'','SQLSRV','localhost',1433,'database','root','','MYSQL','localhost',3306,'dbname','root','',1,8080,'c:/BioApp/images','jpg',3,60,3,'','','',1,1)
            return False
        except Exception as e:
            print(f"Error al leer el archivo de configuración: {e}")
            return False

    def setConfigs(self, config, grupo, driver, host, port, database, user, password, driver2, host2, port2, database2, user2,
                    password2, sistema, web_port, path_images, extension_images, seconds_notification,cache_time,dias_alerta,logo_path, nombre_gym, fondo_path,
                    web_enabled,rele_enabled):
        """Actualiza las configuraciones en memoria y las guarda en el archivo"""
        self.config = config
        self.grupo = grupo

        self.driver = driver
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        self.driver2 = driver2
        self.host2 = host2
        self.port2 = port2
        self.database2 = database2
        self.user2 = user2
        self.password2 = password2

        self.sistema = sistema
        self.web_port = web_port
        self.path_images = path_images
        self.extension_images = extension_images
        self.seconds_notification = seconds_notification
        self.cache_time = cache_time
        self.dias_alerta = dias_alerta
        self.logo_path = logo_path
        self.nombre_gym = nombre_gym
        self.fondo_path = fondo_path
        self.web_enabled = web_enabled
        self.rele_enabled = rele_enabled
        
        # Guardar en archivo
        try:
            with open(self.config_file, 'w') as file:
                file.write("#CONFIG 0: no configurado, 1: configurado\n")
                file.write(f"CONFIG={self.config}\n")
                file.write("#GRUPO: GRUPO DE TERMINALES EN LA DB (Asociadas a los molinetes)\n")
                file.write(f"GRUPO={self.grupo}\n")
                file.write("\n")

                file.write("#CONFIGURACIONES DE LA DB PRINCIPAL (SQL SERVER)\n")
                file.write(f"DRIVER={self.driver}\n")
                file.write(f"HOST={self.host}\n")
                file.write(f"PORT={self.port}\n")
                file.write(f"DATABASE={self.database}\n")
                file.write(f"USER={self.user}\n")
                file.write(f"PASSWORD={self.password}\n")
                file.write("\n")

                file.write("#CONFIGURACIONES DE LA DB SECUNDARIA (MYSQL) o (SQL SERVER)\n")
                file.write(f"DRIVER2={self.driver2}\n")
                file.write(f"HOST2={self.host2}\n")
                file.write(f"PORT2={self.port2}\n")
                file.write(f"DATABASE2={self.database2}\n")
                file.write(f"USER2={self.user2}\n")
                file.write(f"PASSWORD2={self.password2}\n")
                file.write("\n")

                file.write("#QUE SISTEMA UTILIZA PARA LA DB2\n")
                file.write("# 1: BioApp + FitGym\n")
                file.write("# 2: BioApp + GymControl \n")
                file.write("# 3: Access + GymControl\n")
                file.write(f"SISTEMA={self.sistema}\n")
                file.write("\n")

                file.write("#CONFIGURACIONES WEB\n")
                file.write(f"WEB_PORT={self.web_port}\n")
                file.write(f"PAHT_IMAGES={self.sistema}\n")
                file.write(f"EXTENSION_IMAGES={self.extension_images}\n")
                file.write(f"SECONDS_NOTIFICATION={self.sistema}\n")
                file.write(f"DIAS_ALERTA={self.dias_alerta}\n")
                file.write(f"LOGO_PATH={self.logo_path}\n")
                file.write(f"NOMBRE_GYM={self.nombre_gym}\n")
                file.write(f"FONDO_PATH={self.fondo_path}\n")
                file.write("\n")

                file.write("#TIEMPO DE CACHE DE LA DB SECUNDARIA\n")
                file.write(f"CACHE_TIME={self.cache_time}\n")
                file.write("\n")

                file.write("# CONFIGURACIONES DEL SISTEMA\n")
                file.write(f"WEB_ENABLED={self.web_enabled}\n")
                file.write(f"RELE_ENABLED={self.rele_enabled}\n")
 
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")
            return False
        
    def to_dict(self):
        return {

            'PAHT_IMAGES': self.path_images,
            'EXTENSION_IMAGES': self.extension_images,
            'SECONDS_NOTIFICATION': self.seconds_notification,
            'CACHE_TIME': self.cache_time,
            'DIAS_ALERTA': self.dias_alerta,
            'LOGO_PATH': self.logo_path,
            'NOMBRE_GYM': self.nombre_gym,
            'FONDO_PATH': self.fondo_path,

        }

config_service = ConfigService()