import pymysql

class ConnMySQL:
    def __init__(self, server, port, database, username, password):
        self.server = server
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self._connect()

    def _connect(self):
        """Establece conexión persistente"""
        try:
            self.connection = pymysql.connect(
                host=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                charset='utf8mb4',
                autocommit=True
            )
            print("✅ Conexión MySQL establecida con pymysql")
        except pymysql.Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            self.connection = None

    def _check_connection(self):
        """Verifica si la conexión sigue activa"""
        if self.connection is None:
            self._connect()
            return False
        
        try:
            # En pymysql, podemos usar ping() para verificar la conexión
            self.connection.ping(reconnect=True)
            return True
        except pymysql.Error:
            print("🔌 Conexión MySQL perdida, reconectando...")
            self._connect()
            return False
        
    def _close_connection(self):
        """Cerrar conexión"""
        if self.connection:
            self.connection.close()
            print("🔒 Conexión MySQL cerrada")

    def execute_query(self, query, params=None):
        """Ejecuta consulta con manejo de reconexión"""
        if not self._check_connection():
            return None
        
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    resultados = cursor.fetchall()

                    # if resultados and isinstance(resultados[0], dict):
                    #     print(f"📊 Columnas: {list(resultados[0].keys())}")
                    return resultados
                else:
                    self.connection.commit()
                    affected_rows = cursor.rowcount
                    return affected_rows
                
        except pymysql.Error as e:
            print(f"❌ Error en consulta MySQL: {e}")
            # Hacer rollback en caso de error
            try:
                self.connection.rollback()
            except:
                pass
            return None