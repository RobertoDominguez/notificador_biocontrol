import pymssql

class ConnSQLSRV:
    def __init__(self, server, port, database, username, password):
        self.server = server
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    # NUEVA VERSION ABRE UNA CONEXION POR CADA CONSULTA
    def execute_query(self, query, params=None):
        try:
            conn = pymssql.connect(
                server=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                data = cursor.fetchall()
                conn.close()
                return data
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                return affected

        except pymssql.Error as e:
            print(f"SQL ERROR: {e}")
            return None