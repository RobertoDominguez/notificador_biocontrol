from services.MarcacionService import MarcacionService
from services.TerminalService import TerminalService

marcacion_service = MarcacionService()
terminal_service = TerminalService()

terminales = terminal_service.getTerminales()
print(terminales)

marcacion = marcacion_service.verificarMarcacion(terminal='AYACUCHO')
print(marcacion.to_dict())


# from core.db_mysql import ConnMySQL
# from services.ConfigService import config_service


# conn_mysql = ConnMySQL(
#                 server=config_service.host2,
#                 port=config_service.port2,
#                 database=config_service.database2,
#                 username=config_service.user2,
#                 password=config_service.password2
# )
# res = conn_mysql.execute_query("SELECT Carnet,ClieNombre,Membresia,FechaIni,FechaFin,Paquete,SucNombre,Habilitado FROM acceso " , ( ) )
# print(res)