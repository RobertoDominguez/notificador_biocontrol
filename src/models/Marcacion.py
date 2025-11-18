class Marcacion:
    def __init__(self,codigo,datetime,terminalCode,allowed,terminalName,terminalIP,nombre, habilitado, cercaDeVencer, foto,paquete,fecha_ini,fecha_fin,duracion_marcacion,saldo_dias):
        self.codigo = codigo
        self.datetime = datetime
        self.terminalCode = terminalCode
        self.allowed = allowed
        self.terminalName = terminalName
        self.terminalIP = terminalIP

        self.nombre = nombre
        self.habilitado = habilitado
        self.cercaDeVencer = cercaDeVencer
        self.foto = foto
        self.paquete = paquete
        self.fecha_ini = fecha_ini
        self.fecha_fin = fecha_fin
        self.duracion_marcacion = duracion_marcacion
        self.saldo_dias = saldo_dias

    def to_dict(self):
        return {
            'codigo': self.codigo,
            'datetime': self.datetime,
            'terminalCode': self.terminalCode,
            'allowed': self.allowed,
            'terminalName': self.terminalName,
            'terminalIP': self.terminalIP,
            'nombre' : self.nombre,
            'habilitado' : self.habilitado,
            'cercaDeVencer' : self.cercaDeVencer,
            'foto' : self.foto,
            'paquete' : self.paquete,
            'fecha_ini' : self.fecha_ini,
            'fecha_fin' : self.fecha_fin,
            'duracion_marcacion' : self.duracion_marcacion,
            'saldo_dias' : self.saldo_dias
        }