from flask import jsonify, request, send_from_directory
from services.MarcacionService import marcacion_service

class MarcacionController:
    def __init__(self):
        self.marcacion_service = marcacion_service

    def obtener_marcacion(self,terminal):
        """Obtiene la marcacion"""
        try:
            marcacion = self.marcacion_service.verificarMarcacion(terminal)

            if marcacion == None:
                return jsonify({
                    'success': True,
                    'data': {},
                    'total': 0
                })
            else:
                return jsonify({
                    'success': True,
                    'data': marcacion.to_dict(),
                    'total': 1
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
    def serve_image(self,filename):
        """Sirve imágenes desde el directorio configurado"""
        try:
            return send_from_directory(self.marcacion_service.config.path_images,filename)
        except FileNotFoundError:
            return "Imagen no encontrada", 404
        

marcacion_controller = MarcacionController()