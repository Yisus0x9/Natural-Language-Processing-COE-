import pickle
import pandas as pd

# --- CONFIGURACIÓN ---
# 1. Escribe aquí el nombre del archivo .pkl que quieres inspeccionar
nombre_del_archivo = 'arxiv_frequency_Title_unigrama.pkl'

# 2. (Opcional) Si quieres ver el contenido completo, pon esto en True.
#    ¡CUIDADO! Si la matriz es muy grande, esto puede consumir mucha memoria.
ver_contenido_completo = True

# --- CÓDIGO PARA CARGAR Y VER EL ARCHIVO ---
try:
    with open(nombre_del_archivo, 'rb') as f:
        # Cargar el objeto desde el archivo
        objeto_cargado = pickle.load(f)

    print(f"✅ ¡Archivo '{nombre_del_archivo}' cargado con éxito!")
    print("-" * 50)

    # Imprimir información básica
    print(f"Tipo de objeto: {type(objeto_cargado)}")
    print(f"Dimensiones (forma): {objeto_cargado.shape}")
    print(f" (Documentos: {objeto_cargado.shape[0]}, Características/Palabras: {objeto_cargado.shape[1]})")

    # Si se eligió ver el contenido completo
    if ver_contenido_completo:
        print("\n--- Contenido de la Matriz (primeras 5 filas y 10 columnas) ---")
        # Convertimos la matriz dispersa a un DataFrame de pandas para verla fácilmente
        df = pd.DataFrame(objeto_cargado.toarray())
        print(df.iloc[:5, :10])  # Muestra una pequeña porción

except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo '{nombre_del_archivo}'.")
except Exception as e:
    print(f"Ocurrió un error: {e}")