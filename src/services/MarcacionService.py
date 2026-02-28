from core.db_api import ConnAPI
from services.ConfigService import config_service
from models.Marcacion import Marcacion
import json
from datetime import datetime, timedelta, date
import threading
import time

from collections import defaultdict

def to_date(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return None

class MarcacionService:
    def __init__(self):
        self.config = config_service
        self.conndbgym = None
        self.firstEntry = True
        self.connect()
   
    def connect(self):
        if self.config.driver2 == 'API':
            self.conndbgym = ConnAPI(
                # base_url=str(self.config.host2)+":"+str(self.config.port2),
                base_url="https://production-239806056137.us-central1.run.app",
                # token=self.config.password2
                token='da8a8326-d468-4a7a-9670-a2874d7521c1'
            )

    # para evitar delay en update le paso por parametro una funcion que se ejecuta justo antes del update (para abrir el relay por ejemplo)
    # cuando llega un codigo ejecuta
    def verificarMarcacion(self,hid_reader,relay=False, funcion=None):
        marcacion = None

        # if self.firstEntry:
        #     return marcacion

        if self.config.config == 0:
            return Exception('no configurado')
        
        codigo = hid_reader.read()
        try:

            isEntry = self.config.user2 == 'Entry'



            if codigo != None and codigo.startswith(('https')):
                print('lee codigo qr: '+str(codigo))
                if self.config.debug == 1:
                    print('Entrada: '+str(isEntry))
                res = self.conndbgym.post('/ControlDevices/ValidateUserQR',{ "qrRaw": codigo, "IsEntry": isEntry })

                if self.config.debug == 1:
                    print(res)

                if res != None and res['allowed'] == True :
                    marcacion = Marcacion(codigo,'','QR',1,'QR','ip','Cliente',1,0,'','','','',1,1)

            #realiza la accion
            if marcacion is not None and callable(funcion):
                funcion(marcacion)
        except Exception as e:
            print(f'error al consumir api {e}')


marcacion_service = MarcacionService()