from flask import Flask, render_template, request, jsonify
import os
import sys
import threading
import webbrowser
from waitress import serve
import time

# Importar controllers
from controllers.MarcacionController import marcacion_controller
from controllers.TerminalController import terminal_controller
from controllers.ConfigController import config_controller

from services.ConfigService import config_service
from services.AutoOpenService import auto_open_service
from services.ReleService import rele_service

app = Flask(__name__)

# Configurar paths para cuando esté empaquetado
if getattr(sys, 'frozen', False):
    # Si está ejecutándose como .exe
    template_dir = os.path.join(sys._MEIPASS, 'templates')
    static_dir = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
else:
    # Desarrollo normal
    app = Flask(__name__)

# Rutas de la interfaz web
@app.route('/')
def index():
    return render_template('terminales.html')

@app.route('/marcaciones')
def marcaciones():
    return render_template('marcaciones.html')

@app.route('/marcacion')
def marcacion():
    return render_template('marcacion.html')

@app.route('/api/marcacion/<string:terminal>', methods=['GET'])
def obtener_marcacion(terminal):
    return marcacion_controller.obtener_marcacion(terminal)

@app.route('/api/config', methods=['GET'])
def obtener_config():
    return config_controller.obtener_configuraciones()

@app.route('/api/imagen/<string:file>', methods=['GET'])
def obtener_imagen(file):
    return marcacion_controller.serve_image(file)

@app.route('/api/logo', methods=['GET'])
def obtener_logo():
    return config_controller.serve_image_full(config_service.logo_path)

@app.route('/api/fondo', methods=['GET'])
def obtener_imagen_fondo():
    return config_controller.serve_image_full(config_service.fondo_path)

@app.route('/api/terminales', methods=['GET'])
def obtener_terminales():
    return terminal_controller.obtener_terminales()


def open_browser():
    """Abre el navegador automáticamente cuando la app esté lista"""
    webbrowser.open_new('http://localhost:8080')

def get_base_path():
    """Obtiene el path base según si es .exe o desarrollo"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

def abrirNavegadores():
    auto_open_service.main()

if __name__ == '__main__':
    # Solo abre el navegador cuando se ejecuta directamente (no en .exe)
    if not getattr(sys, 'frozen', False) and config_service.web_enabled == 1:
        threading.Timer(1.5, open_browser).start()
    
    if config_service.web_enabled == 1:
        print("🚀 Servidor iniciado en http://localhost:"+str(config_service.web_port))
        threading.Timer(3, abrirNavegadores).start()

    print("📁 Directorio base:", get_base_path())    
    print("Presiona Ctrl+C para detener el servidor")
    
        
    if config_service.rele_enabled == 1:
        rele_service.iniciarHilos()
    
    # Si no esta el servidor web igual sigue corriendo el programa
    if config_service.web_enabled == 1:
        # Usar Waitress como servidor de producción
        serve(app, host='0.0.0.0', port=config_service.web_port)
    else:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Deteniendo la aplicación...")
            # Aquí podrías agregar código para limpiar si es necesario