from core.db_sqlsrv import ConnSQLSRV
from core.db_mysql import ConnMySQL
from services.ConfigService import config_service
from models.Terminal import Terminal

class TerminalService:
    def __init__(self):
        self.config = config_service
        self.conndbbioapp = None
        self.connect()

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


    def getTerminales(self):
        terminales = []

        if self.config.config == 0:
            return Exception('no configurado')
        
        # ACCESS
        if self.config.driver == 'SQLSRV' and self.config.sistema == 1 :
            resultBioApp = self.conndbbioapp.execute_query('SELECT m.id, m.sn, m.MachineAlias, 1 as group_id FROM Machines as m',())

            for r in resultBioApp:
                terminal = Terminal(r[0],r[1],r[2],r[3])
                print(terminal.to_dict())
                terminales.append(terminal.to_dict())

        return terminales
    
terminal_service = TerminalService()