from flask import jsonify, request
from services.TerminalService import terminal_service

class TerminalController:
    def __init__(self):
        self.terminal_service = terminal_service
    
    def obtener_terminales(self):
        """Obtiene Terminales"""
        try:
            terminales = self.terminal_service.getTerminales()

            return jsonify({
                    'success': True,
                    'data': terminales,
                    'total': len(terminales)
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

terminal_controller = TerminalController()