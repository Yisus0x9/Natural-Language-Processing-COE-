
import subprocess
import sys
import os

def install_requirements():
    """Instala las dependencias desde requirements.txt y packages adicionales"""
    # Primero instalar desde requirements.txt si existe
    if os.path.exists('requirements.txt'):
        try:
            print("📦 Instalando dependencias desde requirements.txt...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--break-system-packages'])
            print("✅ Dependencias de requirements.txt instaladas")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning installing from requirements.txt: {e}")
    
    # Instalar packages esenciales para el proyecto
    essential_packages = [
        'requests',
        'beautifulsoup4', 
        'lxml',
        'feedparser',
        'pandas',
        'nltk',
        'numpy',
        'tqdm'
    ]
    
    for package in essential_packages:
        try:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--break-system-packages'])
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {package}: {e}")
            
    print("✅ Todas las dependencias instaladas correctamente")

def create_directories():
    """Crea directorios necesarios"""
    dirs = ['data', 'logs', 'html_cache']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Directorio creado: {dir_name}")

def download_nltk_resources():
    """Descarga los recursos necesarios de NLTK"""
    try:
        import nltk
        print("📚 Descargando recursos de NLTK...")
        
        resources = [
            'punkt',
            'punkt_tab', 
            'averaged_perceptron_tagger',
            'averaged_perceptron_tagger_eng',
            'wordnet',
            'omw-1.4'
        ]
        
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
                print(f"   ✅ {resource} descargado")
            except Exception as e:
                print(f"   ⚠️ Warning descargando {resource}: {e}")
                
        print("✅ Recursos de NLTK descargados")
        
    except ImportError:
        print("⚠️ NLTK no está instalado aún, se descargará después")

def run_complete_pipeline():
    """Ejecuta el pipeline completo: webscraping -> text_normalization"""
    print("\n🚀 Ejecutando pipeline completo del proyecto...")
    
    # Step 1: Webscraping
    print("\n📡 Paso 1: Ejecutando webscraping...")
    try:
        if os.path.exists('webscraping.py'):
            subprocess.check_call([sys.executable, 'webscraping.py'])
            print("✅ Webscraping completado")
        else:
            print("❌ No se encontró webscraping.py")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en webscraping: {e}")
        return False
    
    # Step 2: Text Normalization
    print("\n🔄 Paso 2: Ejecutando normalización de texto...")
    try:
        if os.path.exists('text_normalization.py'):
            subprocess.check_call([sys.executable, 'text_normalization.py'])
            print("✅ Normalización de texto completada")
        else:
            print("❌ No se encontró text_normalization.py")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en normalización: {e}")
        return False
    
    print("\n🎉 Pipeline completo ejecutado exitosamente!")
    print("📁 Archivos generados:")
    print("   - arxiv_raw_corpus.csv")
    print("   - pubmed_raw_corpus.csv") 
    print("   - arxiv_normalized_corpus.csv")
    print("   - pubmed_normalized_corpus.csv")
    return True

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

if __name__ == "__main__":
    print("🔧 Natural Language Processing - Document Similarity Setup")
    print("=" * 60)
    
    # Setup básico
    check_python_version()
    create_directories()
    install_requirements()
    download_nltk_resources()
    
    print("\n" + "=" * 60)
    print("✅ Setup completado exitosamente!")
    
    # Preguntar si quiere ejecutar el pipeline completo
    print("\n🤖 ¿Deseas ejecutar el pipeline completo ahora?")
    print("   Esto ejecutará:")
    print("   1. Webscraping (ArXiv + PubMed)")
    print("   2. Text Normalization") 
    
    response = input("\n¿Ejecutar pipeline? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', 'sí', 'si']:
        success = run_complete_pipeline()
        if success:
            print("\n🎊 ¡Proyecto completado exitosamente!")
        else:
            print("\n❌ Hubo errores en el pipeline")
    else:
        print("\n📝 Para ejecutar manualmente:")
        print("   1. python webscraping.py")
        print("   2. python text_normalization.py")
        print("   O ejecuta: python setup.py (y elige 'y' para el pipeline)")