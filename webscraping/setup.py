
import subprocess
import sys
import os

def install_requirements():
    """Instala las dependencias desde requirements.txt"""
    try:
        print("Instalando dependencias...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def create_directories():
    """Crea directorios necesarios"""
    dirs = ['data', 'logs', 'html_cache']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Directorio creado: {dir_name}")

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

if __name__ == "__main__":
    print("🔧 Configurando entorno para scrapers ArXiv y PubMed...")
    check_python_version()
    create_directories()
    install_requirements()
    print("✅ Setup completado. Puedes ejecutar el scraper con: python scraper.py")