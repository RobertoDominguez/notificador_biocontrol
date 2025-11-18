from flask import jsonify, request,send_from_directory
from services.ConfigService import config_service
import os 

class ConfigController:
    def __init__(self):
        self.config_service = config_service
    
    def obtener_configuraciones(self):
        """Obtiene Configs"""
        try:
            return jsonify({
                    'success': True,
                    'data': config_service.to_dict(),
                    'total': 1
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def serve_image_full(self,full_file):
        """Sirve imágenes desde el directorio configurado"""
        try:
            directory, filename = os.path.split(full_file)
            return send_from_directory(directory, filename)
        except FileNotFoundError:
            return "Imagen no encontrada", 404

config_controller = ConfigController()