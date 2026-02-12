from core.db_sqlsrv import ConnSQLSRV
from core.db_mysql import ConnMySQL
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
        self.conndbbioapp = None
        self.conndbgym = None
        self.cachegym = defaultdict(list)
        self.firstEntry = True
        self.connect()
        
        # Iniciar el hilo de actualización
        hilo_cache = threading.Thread(target=self.worker)
        hilo_cache.daemon = True  # Para que el hilo se cierre cuando el programa principal cierre
        hilo_cache.start()

        # Iniciar el hilo de actualizacion de los rele (Hacer en otro archivo py)

    def connect(self):
        if self.config.driver == 'SQLSRV':
            self.conndbbioapp = ConnSQLSRV(
                server=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.user,
                password=self.config.password
            )

        if self.config.driver == 'MYSQL':
            self.conndbbioapp = ConnMySQL(
                server=self.config.host,
                port=self.config.port,
                database=self.config.database,
                username=self.config.user,
                password=self.config.password
            )

        if self.config.driver2 == 'SQLSRV':
            self.conndbgym = ConnSQLSRV(
                server=self.config.host2,
                port=self.config.port2,
                database=self.config.database2,
                username=self.config.user2,
                password=self.config.password2
            )

        if self.config.driver2 == 'MYSQL':
            self.conndbgym = ConnMySQL(
                server=self.config.host2,
                port=self.config.port2,
                database=self.config.database2,
                username=self.config.user2,
                password=self.config.password2
            )

        if self.config.driver2 == 'API':
            self.conndbgym = ConnAPI(
                base_url=self.config.host2+":"+self.config.port2,
                token=self.config.password2
            )

    def cachearGymDB(self):
        if (self.config.driver2 == 'MYSQL' or self.config.driver2 == 'SQLSRV') and self.config.sistema == 1 :
            resultGym = self.conndbgym.execute_query("SELECT Carnet,ClieNombre,Membresia,FechaIni,FechaFin,Paquete,SucNombre,Habilitado FROM acceso ", ( ))
            if resultGym != None and len(resultGym) > 0:
                self.cachegym = defaultdict(list)
            else:
                print('Error en cache: 0 Tuplas recibidas')

            for gym in resultGym:
                row = {
                    'Carnet' : gym[0],
                    'ClieNombre' : gym[1],
                    'Membresia' : gym[2],
                    'FechaIni' : gym[3],
                    'FechaFin' : gym[4],
                    'Paquete' : gym[5],
                    'SucNombre' : gym[6],
                    'Habilitado' : gym[7],
                }
                self.cachegym[gym[0]].append(row)

        if self.config.driver2 == 'SQLSRV' and (self.config.sistema == 2 or self.config.sistema == 3):
            resultGym = self.conndbgym.execute_query("SELECT c.codigo, CONCAT(c.nombres, ' ', c.apellidos) as nombre_completo , p.nombre as membresia," \
            "v.fecha_desde, v.fecha_hasta, p.nombre as nombre_paquete,'' as suc_nombre, " \
            "CASE WHEN  fecha_desde <= CAST(GETDATE() AS DATE) AND fecha_hasta >= CAST(GETDATE() AS DATE) THEN 1 else 0 END as habilitado "\
            "FROM Venta as v JOIN Paquete as p ON v.id_paquete = p.id JOIN Cliente as c ON c.id = v.id_cliente " \
            "WHERE v.cancelado = 1 AND v.anulado = 0 ", ( ))

            if resultGym != None and len(resultGym) > 0:
                self.cachegym = defaultdict(list)
            else:
                print('Error en cache: 0 Tuplas recibidas')

            for gym in resultGym:
                row = {
                    'Carnet' : gym[0],
                    'ClieNombre' : gym[1],
                    'Membresia' : gym[2],
                    'FechaIni' : gym[3],
                    'FechaFin' : gym[4],
                    'Paquete' : gym[5],
                    'SucNombre' : gym[6],
                    'Habilitado' : gym[7],
                }
                self.cachegym[gym[0]].append(row)
        
        if self.config.driver == 'SQLSRV' and self.firstEntry:
            self.firstEntry = False
            self.vaciarColaDeEspera()
        
        # Cache para API
        if self.config.driver == 'SQLSRV' and self.config.driver2 == 'API' and self.config.sistema == 5:
            try:
                response = self.conndbgym.get(
                    self.config.database2,
                    {
                        "id_py": self.config.user2,
                        "id_membresia": 0,
                        "id_cliente": 0,
                        "nombre": "test"
                    }
                )

                detalle = response.get("detalleRespuesta", [])
                self.cachegym = defaultdict(list)

                hoy = date.today()

                for item in detalle:
                    carnet = str(item.get("Codigo_C_B"))

                    fecha_ini_raw = item.get("")
                    fecha_ini = to_date(fecha_ini_raw)
                    fecha_fin = hoy

                    habilitado = item.get("Estado_B") in (1, "1", True)

                    row = {
                        'Carnet': carnet,
                        'ClieNombre': '',      # no aplica
                        'Membresia': '',       # no aplica
                        'FechaIni': fecha_ini,
                        'FechaFin': fecha_fin,
                        'Paquete': '',         # no aplica
                        'SucNombre': '',       # no aplica
                        'Habilitado': habilitado,
                    }

                    self.cachegym[carnet].append(row)

                if self.config.debug == 1:
                    print(f'Cache API: {len(self.cachegym)}')

            except Exception as e:
                print(f'Error cache API: {e}')

        if self.config.debug == 1:
            print('Cache DB2: '+str(len(self.cachegym)))
    
    def worker(self):
        while True:
            self.cachearGymDB()
            time.sleep(self.config.cache_time)  # Esperar x segundos


    def queryACache(self,carnet):
        return self.cachegym.get(str(carnet), [])

    def vaciarColaDeEspera(self):
        if self.config.driver == 'SQLSRV' and (self.config.sistema == 1 or self.config.sistema == 2 or self.config.sistema == 5):
            print('Vaciando cola de espera...')
            resultBioApp = self.conndbbioapp.execute_query("UPDATE acc.AccessLog set mostrado = 1 where mostrado = 0",())
            resultBioApp = self.conndbbioapp.execute_query("UPDATE acc.AccessLog set abierto = 1 where abierto = 0",())

        if self.config.driver == 'SQLSRV' and self.config.sistema == 3:
            print('Vaciando cola de espera...')
            resultBioApp = self.conndbbioapp.execute_query("UPDATE acc_monitor_log set mostrado = 1 where mostrado = 0",())
            resultBioApp = self.conndbbioapp.execute_query("UPDATE acc_monitor_log set abierto = 1 where abierto = 0",())

        if self.config.driver == 'SQLSRV' and self.config.sistema == 4:
            print('Vaciando cola de espera...')
            resultBioApp = self.conndbbioapp.execute_query("UPDATE TEvent set mostrado = 1 where mostrado = 0",())
            resultBioApp = self.conndbbioapp.execute_query("UPDATE TEvent set abierto = 1 where abierto = 0",())

    #para evitar delay en update le paso por parametro una funcion que se ejecuta justo antes del update (para abrir el relay por ejemplo)
    def verificarMarcacion(self,terminal,relay=False, funcion=None):
        marcacion = None

        if self.firstEntry:
            return marcacion

        if self.config.config == 0:
            return Exception('no configurado')
        

        # BioApp
        if self.config.driver == 'SQLSRV' and (self.config.sistema == 1 or self.config.sistema == 2):
            if not relay:
                resultBioApp = self.conndbbioapp.execute_query("SELECT top 1 a.Id,a.UserCode,a.DateTime,a.TerminalCode,a.Allowed,a.TerminalName,a.TerminalIP,u.Meta FROM acc.AccessLog as a" \
                ' JOIN acc."User" as u ON a.UserCode=u.Code' \
                " WHERE a.mostrado = 0 AND a.TerminalName = %s",(terminal,))
            if relay:
                resultBioApp = self.conndbbioapp.execute_query("SELECT top 1 a.Id,a.UserCode,a.DateTime,a.TerminalCode,a.Allowed,a.TerminalName,a.TerminalIP,u.Meta FROM acc.AccessLog as a" \
                ' JOIN acc."User" as u ON a.UserCode=u.Code' \
                " WHERE a.abierto = 0 AND a.TerminalName = %s",(terminal,))
            

            r = None
            if resultBioApp != None and len(resultBioApp) > 0:
                r = resultBioApp[0]
                print("Nueva Marcacion: "+str(r[1]))
            
            g = None
            habilitado = 0
            if r != None:
                resultGym = self.queryACache(r[1])

                if len(resultGym) > 0:
                    g = resultGym[0]
                    for gym in resultGym:
                        if gym['Habilitado'] == 1 or gym['Habilitado'] == '1' or gym['Habilitado'] == True:
                            g = gym
                            habilitado = 1

                    

            if r != None and g != None:
                foto = 'Sin Foto'
                jsonMetaImage = json.loads(r[7]).get("photoFileName")
                if jsonMetaImage is not None:
                    foto = str(jsonMetaImage) + '.' + self.config.extension_images

                if self.config.debug == 1:
                    print(g['FechaFin'])

                fecha_fin = to_date( g['FechaFin'] )
                fecha_actual = date.today()

                diferencia = fecha_fin - fecha_actual
                dias_diferencia = diferencia.days
                if (dias_diferencia < 0):
                    dias_diferencia = 0
                cercaDeVencer = dias_diferencia <= self.config.dias_alerta

                marcacion = Marcacion(r[1],r[2],r[3],r[4],r[5],r[6],g['ClieNombre'],habilitado,cercaDeVencer,foto,g['Paquete'],g['FechaIni'],
                                      g['FechaFin'],self.config.seconds_notification,dias_diferencia)
                

                #realiza la accion
                if marcacion is not None and callable(funcion):
                    funcion(marcacion)

                #pone en mostrada la marcacion
                if not relay:
                    self.conndbbioapp.execute_query("UPDATE acc.AccessLog Set mostrado = 1 WHERE Id = %s",(r[0],))
                if relay:
                    self.conndbbioapp.execute_query("UPDATE acc.AccessLog Set abierto = 1 WHERE Id = %s",(r[0],))   

            #Intenta 3 veces antes de poner en mostrada la marcacion (en caso de algun error que no se trabe)
            if r != None and g == None:
                print('Error: Persona No encontrada en la DB2')
                #pone en mostrada la marcacion
                if not relay:
                    self.conndbbioapp.execute_query("UPDATE acc.AccessLog Set mostrado = 1 WHERE Id = %s",(r[0],))
                if relay:
                    self.conndbbioapp.execute_query("UPDATE acc.AccessLog Set abierto = 1 WHERE Id = %s",(r[0],))   




        # Access
        if self.config.driver == 'SQLSRV' and self.config.driver2 == 'SQLSRV' and self.config.sistema == 3:
            if not relay:
                resultBioApp = self.conndbbioapp.execute_query("SELECT TOP 1 a.id,a.pin,a.time,m.sn,1 as Allowed,a.device_name,m.ip,'' as meta"\
                ' FROM acc_monitor_log as a JOIN Machines as m ON a.device_id = m.id'\
                " WHERE a.mostrado = 0 AND a.device_name = %s",(terminal,))
            if relay:
                resultBioApp = self.conndbbioapp.execute_query("SELECT TOP 1 a.id,a.pin,a.time,m.sn,1 as Allowed,a.device_name,m.ip,'' as meta"\
                ' FROM acc_monitor_log as a JOIN Machines as m ON a.device_id = m.id'\
                " WHERE a.abierto = 0 AND a.device_name = %s",(terminal,))

            r = None
            if resultBioApp != None and len(resultBioApp) > 0:
                r = resultBioApp[0]
                print("Nueva Marcacion: "+r[1])
            
            g = None
            habilitado = 0
            if r != None:
                resultGym = self.queryACache(r[1])
                if len(resultGym) > 0:
                    g = resultGym[0]
                    print(g)
                    for gym in resultGym:
                        if gym['Habilitado'] == 1 or gym['Habilitado'] == '1' or gym['Habilitado'] == True:
                            g = gym
                            habilitado = 1

                    

            if r != None and g != None:
                foto = 'Sin Foto'
                jsonMetaImage = None #json.loads(r[7]).get("photoFileName")
                if jsonMetaImage is not None:
                    foto = str(jsonMetaImage) + '.' + self.config.extension_images

                fecha_fin = g['FechaFin']
                fecha_actual = datetime.today()

                diferencia = fecha_fin - fecha_actual
                dias_diferencia = diferencia.days
                if (dias_diferencia < 0):
                    dias_diferencia = 0
                cercaDeVencer = dias_diferencia <= self.config.dias_alerta

                marcacion = Marcacion(r[1],r[2],r[3],r[4],r[5],r[6],g['ClieNombre'],habilitado,cercaDeVencer,foto,g['Paquete'],g['FechaIni'],
                                      g['FechaFin'],self.config.seconds_notification,dias_diferencia)
                
                #realiza la accion
                if marcacion is not None and callable(funcion):
                    funcion(marcacion)

                #pone en mostrada la marcacion
                if not relay:
                    self.conndbbioapp.execute_query("UPDATE acc_monitor_log Set mostrado = 1 WHERE Id = %s",(r[0],))
                if relay:
                    self.conndbbioapp.execute_query("UPDATE acc_monitor_log Set abierto = 1 WHERE Id = %s",(r[0],))   


            if r != None and g == None:
                print('Error: Persona No encontrada en la DB2')
                #pone en mostrada la marcacion
                if not relay:
                    self.conndbbioapp.execute_query("UPDATE acc_monitor_log Set mostrado = 1 WHERE Id = %s",(r[0],))
                if relay:
                    self.conndbbioapp.execute_query("UPDATE acc_monitor_log Set abierto = 1 WHERE Id = %s",(r[0],))   
        

        # MINI SQL
        if self.config.driver == 'SQLSRV' and self.config.sistema == 4:
            if not relay:
                resultBioApp = self.conndbbioapp.execute_query(" SELECT TOP 1 e.EventID, p.EmployeeCode, e.EventTime, c.Serial, 1 as allowed, c.Name, c.IP,'' as meta, "\
                                                                " p.CardNo,ISNULL(p.EmployeeName, '') + ' ' + ISNULL(p.EnglishName, '') AS NombreCompleto, "\
                                                                " 'membresia' as membresia, p.RegDate, p.EndDate, 'Acceso' as nombre_paquete, '' as suc_nombre, "\
                                                                " CASE "\
                                                                "        WHEN DATEADD(day, DATEDIFF(day, 0, p.RegDate), 0) <= DATEADD(day, DATEDIFF(day, 0, GETDATE()), 0) "\
                                                                "        AND DATEADD(day, DATEDIFF(day, 0, p.EndDate), 0) >= DATEADD(day, DATEDIFF(day, 0, GETDATE()), 0) "\
                                                                "        THEN 1 "\
                                                                "        ELSE 0 "\
                                                                "    END as habilitado, e.EventType "\
                                                                " FROM TEvent as e "\
                                                                " JOIN TControl as c ON e.ControlID = c.ControlID "\
                                                                " JOIN TEmployee as p ON e.EmployeeID = p.EmployeeID "\
                                                                " WHERE p.deleted = 0  "\
                                                                " AND e.mostrado = 0 AND c.Name = %s",(terminal,))

            if relay:
                resultBioApp = self.conndbbioapp.execute_query(" SELECT TOP 1 e.EventID, p.EmployeeCode, e.EventTime, c.Serial, 1 as allowed, c.Name, c.IP,'' as meta, "\
                                                                " p.CardNo,ISNULL(p.EmployeeName, '') + ' ' + ISNULL(p.EnglishName, '') AS NombreCompleto, "\
                                                                " 'membresia' as membresia, p.RegDate, p.EndDate, 'Acceso' as nombre_paquete, '' as suc_nombre, "\
                                                                " CASE "\
                                                                "        WHEN DATEADD(day, DATEDIFF(day, 0, p.RegDate), 0) <= DATEADD(day, DATEDIFF(day, 0, GETDATE()), 0) "\
                                                                "        AND DATEADD(day, DATEDIFF(day, 0, p.EndDate), 0) >= DATEADD(day, DATEDIFF(day, 0, GETDATE()), 0) "\
                                                                "        THEN 1 "\
                                                                "        ELSE 0 "\
                                                                "    END as habilitado, e.EventType "\
                                                                " FROM TEvent as e "\
                                                                " JOIN TControl as c ON e.ControlID = c.ControlID "\
                                                                " JOIN TEmployee as p ON e.EmployeeID = p.EmployeeID "\
                                                                " WHERE p.deleted = 0  "\
                                                                " AND e.abierto = 0 AND c.Name = %s",(terminal,))
                
            r = None
            habilitado = 0
            if resultBioApp != None and len(resultBioApp) > 0:
                r = resultBioApp[0]
                print("Nueva Marcacion: "+r[1])
            
                allowed = r[4]
                if r[16] == 6 or r[16] == '6':
                    allowed = 0

                if r[15] == 1 or r[15] == '1' or r[15] == True:
                    habilitado = 1
                        

            if r != None:
                foto = 'Sin Foto'
                jsonMetaImage = r[1] #json.loads(r[7]).get("photoFileName")
                if jsonMetaImage is not None:
                    foto = str(jsonMetaImage) + '.' + self.config.extension_images

                fecha_fin = r[12]
                fecha_actual = datetime.today()

                diferencia = fecha_fin - fecha_actual
                dias_diferencia = diferencia.days
                if (dias_diferencia < 0):
                    dias_diferencia = 0
                cercaDeVencer = dias_diferencia <= self.config.dias_alerta

                marcacion = Marcacion(r[1],r[2],r[3],allowed,r[5],r[6],r[9],habilitado,cercaDeVencer,foto,r[13],r[11],
                                      r[12],self.config.seconds_notification,dias_diferencia)
                
                #realiza la accion
                if marcacion is not None and callable(funcion):
                    funcion(marcacion)

                #pone en mostrada la marcacion
                if not relay:
                    self.conndbbioapp.execute_query("UPDATE TEvent Set mostrado = 1 WHERE EventId = %s",(r[0],))
                if relay:
                    self.conndbbioapp.execute_query("UPDATE TEvent Set abierto = 1 WHERE EventId = %s",(r[0],))   



        # Access con API
        if self.config.driver == 'SQLSRV' and self.config.driver2 == 'API' and self.config.sistema == 5:
            if not relay:
                resultBioApp = self.conndbbioapp.execute_query(
                    "SELECT TOP 1 a.id,a.pin,a.time,m.sn,1 as Allowed,a.device_name,m.ip,'' as meta "
                    "FROM acc_monitor_log as a "
                    "JOIN Machines as m ON a.device_id = m.id "
                    "WHERE a.mostrado = 0 AND a.device_name = %s",
                    (terminal,)
                )

            if relay:
                resultBioApp = self.conndbbioapp.execute_query(
                    "SELECT TOP 1 a.id,a.pin,a.time,m.sn,1 as Allowed,a.device_name,m.ip,'' as meta "
                    "FROM acc_monitor_log as a "
                    "JOIN Machines as m ON a.device_id = m.id "
                    "WHERE a.abierto = 0 AND a.device_name = %s",
                    (terminal,)
                )

            r = None
            if resultBioApp and len(resultBioApp) > 0:
                r = resultBioApp[0]
                print("Nueva Marcacion:", r[1])

            g = None
            habilitado = 0

            if r is not None:
                resultGym = self.queryACache(r[1])

                if len(resultGym) > 0:
                    g = resultGym[0]
                    for gym in resultGym:
                        if gym['Habilitado'] in (1, '1', True):
                            g = gym
                            habilitado = 1

            if r is not None and g is not None:
                fecha_actual = datetime.today()
                fecha_fin = g['FechaFin']

                diferencia = fecha_fin - fecha_actual.date()
                dias_diferencia = diferencia.days
                if dias_diferencia < 0:
                    dias_diferencia = 0

                cercaDeVencer = dias_diferencia <= self.config.dias_alerta

                marcacion = Marcacion(
                    r[1],               # carnet
                    r[2],               # time
                    r[3],               # sn
                    r[4],               # allowed
                    r[5],               # device_name
                    r[6],               # ip
                    '',                 # ClieNombre (no aplica)
                    habilitado,
                    cercaDeVencer,
                    'Sin Foto',
                    '',                 # Paquete
                    g['FechaIni'],
                    g['FechaFin'],
                    self.config.seconds_notification,
                    dias_diferencia
                )

                if callable(funcion):
                    funcion(marcacion)

                if not relay:
                    self.conndbbioapp.execute_query(
                        "UPDATE acc_monitor_log SET mostrado = 1 WHERE Id = %s",
                        (r[0],)
                    )
                else:
                    self.conndbbioapp.execute_query(
                        "UPDATE acc_monitor_log SET abierto = 1 WHERE Id = %s",
                        (r[0],)
                    )

            if r is not None and g is None:
                print('Error: Persona No encontrada en API')

                if not relay:
                    self.conndbbioapp.execute_query(
                        "UPDATE acc_monitor_log SET mostrado = 1 WHERE Id = %s",
                        (r[0],)
                    )
                else:
                    self.conndbbioapp.execute_query(
                        "UPDATE acc_monitor_log SET abierto = 1 WHERE Id = %s",
                        (r[0],)
                    )


        return marcacion
    
marcacion_service = MarcacionService()