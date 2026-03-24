from flask import jsonify, request, send_from_directory, Response
from services.MarcacionService import marcacion_service
import requests


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
        
    def serve_image(self, filename):
        """Sirve imágenes desde directorio local o URL remota"""
        try:
            base_path = self.marcacion_service.config.path_images

            # Si es URL
            if base_path.startswith('http'):
                url = f"{base_path.rstrip('/')}/{filename}"

                response = requests.get(url, stream=True)

                if response.status_code != 200:
                    return "Imagen no encontrada", 404

                return Response(
                    response.content,
                    content_type=response.headers.get('Content-Type', 'image/jpeg')
                )

            # Si es local
            return send_from_directory(base_path, filename)

        except Exception as e:
            return f"Error: {str(e)}", 500

marcacion_controller = MarcacionController()