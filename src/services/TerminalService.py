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
        
        if self.config.driver == 'SQLSRV' and (self.config.sistema == 1 or self.config.sistema == 2 or self.config.sistema == 5) :
            resultBioApp = self.conndbbioapp.execute_query('SELECT t.Guid, t.Code, t.Name, t.GroupId FROM bio.Terminal as t,acc."Group" as g where t.GroupId=g.Id AND g.Name=%s',(self.config.grupo,))

            for r in resultBioApp:
                terminal = Terminal(r[0],r[1],r[2],r[3])
                print(terminal.to_dict())
                terminales.append(terminal.to_dict())

        if self.config.driver == 'SQLSRV' and self.config.sistema == 3 :
            resultBioApp = self.conndbbioapp.execute_query('SELECT m.id, m.sn, m.MachineAlias, 1 as group_id FROM Machines as m',())

            for r in resultBioApp:
                terminal = Terminal(r[0],r[1],r[2],r[3])
                print(terminal.to_dict())
                terminales.append(terminal.to_dict())

        if self.config.driver == 'SQLSRV' and self.config.sistema == 4 :
            resultBioApp = self.conndbbioapp.execute_query('SELECT m.ControlID, m.Serial, m.Name, 1 as group_id FROM TControl as m order by orden asc',())

            for r in resultBioApp:
                terminal = Terminal(r[0],r[1],r[2],r[3])
                print(terminal.to_dict())
                terminales.append(terminal.to_dict())

        return terminales
    
terminal_service = TerminalService()