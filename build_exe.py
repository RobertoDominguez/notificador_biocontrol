import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def clean_directory(dir_path,rm):
    """Limpia un directorio si no existe"""
    if os.path.exists(dir_path) and rm:
        print(f"🧹 Limpiando directorio: {dir_path}")
        shutil.rmtree(dir_path)
    if not os.path.exists(dir_path):
        print(f"📁 Creando el directorio: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)

def build_exe(version):
    # Configurar paths
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    releases_dir = project_root / "releases"
    
    # Crear directorios necesarios
    clean_directory(build_dir,True)
    clean_directory(dist_dir,True)
    clean_directory(releases_dir,False)
    
    # Verificar que existe el código fuente
    if not src_dir.exists():
        print("❌ Error: No se encuentra la carpeta 'src' con el código fuente")
        return False
    
    # Instalar PyInstaller si no está instalado
    try:
        import PyInstaller
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Crear el comando de PyInstaller
    cmd = [
        'pyinstaller',
        '--name=NotificadorBiocontrol',
        '--onefile',
        '--add-data', f'{src_dir / "templates"};templates',
        '--add-data', f'{src_dir / "static"};static',

        '--add-data', f'{src_dir / "controllers"};controllers',
        '--add-data', f'{src_dir / "models"};models',
        '--add-data', f'{src_dir / "services"};services',
        '--add-data', f'{src_dir / "core"};core',
        
        '--hidden-import=waitress',
        '--hidden-import=flask',
        '--hidden-import=flask.json',
        '--hidden-import=webbrowser',
        '--hidden-import=pyodbc',
        '--hidden-import=mysql-connector-python',
        '--hidden-import=pymssql',
        '--hidden-import=pymysql',
        '--hidden-import=pyautogui',
        '--hidden-import=requests',
        '--hidden-import=pyinput',
        '--hidden-import=hidapi',


        '--hidden-import=core.db_mysql',
        '--hidden-import=core.db_sqlsrv',
        '--hidden-import=core.db_api',
        '--hidden-import=core.hid_reader',

        '--hidden-import=models.Marcacion',
        '--hidden-import=models.Terminal',
        '--hidden-import=controllers.MarcacionController',
        '--hidden-import=controllers.TerminalController',
        '--hidden-import=controllers.ConfigController',
        '--hidden-import=services.MarcacionService',
        '--hidden-import=services.TerminalService',
        '--hidden-import=services.ConfigService',
        '--hidden-import=services.AutoOpenService',
        '--hidden-import=services.ReleService',


        '--distpath', str(dist_dir),
        '--workpath', str(build_dir),
        '--specpath', str(build_dir),
        '--clean',
        # '--noconsole',
        str(src_dir / "app.py")
    ]
    
    print("🔨 Construyendo el ejecutable...")
    print(f"📁 Source: {src_dir}")
    print(f"📁 Build: {build_dir}")
    print(f"📁 Dist: {dist_dir}")
    
    try:
        subprocess.check_call(cmd)
        
        # Verificar si el ejecutable fue creado
        exe_path = dist_dir / "NotificadorBiocontrol.exe"
        if exe_path.exists():
            # Copiar a releases con timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            release_exe = releases_dir / f"NotificadorBiocontrol_{version}.exe"
            shutil.copy2(exe_path, release_exe)
            
            # También copiar una versión sin timestamp
            # latest_exe = releases_dir / "NotificadorBiocontrol.exe"
            # shutil.copy2(exe_path, latest_exe)
            
            print("✅ Ejecutable creado exitosamente!")
            # print(f"📄 Ejecutable principal: {exe_path}")
            print(f"📄 Release con timestamp: {release_exe}")
            # print(f"📄 Última versión: {latest_exe}")
            print(f"📏 Tamaño del archivo: {os.path.getsize(release_exe) / (1024*1024):.2f} MB")
            
            return True
        else:
            print("❌ Error: No se pudo crear el ejecutable")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la compilación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando proceso de construcción...")
    success = build_exe('qr_v1.0.8')
    
    if success:
        print("\n🎉 ¡Compilación completada exitosamente!")
        print("📋 Los archivos están en la carpeta 'releases/'")
    else:
        print("\n💥 ¡Compilación fallida!")
        sys.exit(1)