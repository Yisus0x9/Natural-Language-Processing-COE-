from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import pickle
import os


def extraer_datos(archivo_csv, columna):
    df = pd.read_csv(archivo_csv, delimiter='\t')
    df = df[columna].fillna('')

    return df


class VectorRepresentation:
    def __init__(self, tipo_representacion, tipo_ngrama):
        self.vectorizer = None
        self.tipo_representacion = tipo_representacion
        self.tipo_ngrama = tipo_ngrama

    def entrenar(self, dataframe):
        if self.tipo_representacion == 'frequency':
            self.vectorizer = CountVectorizer(ngram_range=self.tipo_ngrama)
        elif self.tipo_representacion == 'binarized':
            self.vectorizer = CountVectorizer(ngram_range=self.tipo_ngrama, binary=True)
        elif self.tipo_representacion == 'tfidf':
            self.vectorizer = TfidfVectorizer(ngram_range=self.tipo_ngrama)
        else:
            raise ValueError(f"Tipo de representación no válido: {self.tipo_representacion}")

        self.vectorizer.fit(dataframe)
        return self

    def transformar(self, fit_dataframe):
        if self.vectorizer is None:
            raise RuntimeError('Vectorizer no se ha entrenado, utiliza fit() primero.')

        return self.vectorizer.transform(fit_dataframe)

    def crear_pickle(self, carpeta, tipo_grama, matriz, nomb_corpus, columna):
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = f'{nomb_corpus}_{self.tipo_representacion}_{columna}_{tipo_grama}'
        ruta_archivo_pkl = os.path.join(carpeta, f'{nombre_archivo}.pkl')

        with open(ruta_archivo_pkl, 'wb') as f:
            pickle.dump(matriz, f)

        print(f"Archivo {nombre_archivo}.pkl creado correctamente.")

def main():
    archivos = ["arxiv_normalized_corpus.csv", "pubmed_normalized_corpus.csv"]
    columnas = ['Title', 'Abstract']
    tipo_representacion = ['frequency', 'binarized', 'tfidf']
    tipo_ngrama = [(1, 1), (2, 2)] # (1, 1) -> unigrama, (2, 2) -> bigrama
    carpeta = 'vectorization'

    print("Iniciando vectorización...")

    for archivo in archivos:
        tipo_corpus = archivo.split('_')[0]

        for columna in columnas:
            dataframe = extraer_datos(archivo, columna)

            for tipo_rep in tipo_representacion:
                for ngrama in tipo_ngrama:
                    nomb_ngrama = 'unigrama' if ngrama == (1, 1) else 'bigrama'

                    print(f"Procesando: Corpus={tipo_corpus}, Columna={columna}, Rep={tipo_rep}, N-grama={nomb_ngrama}")

                    vectorizer = VectorRepresentation(
                        tipo_representacion=tipo_rep,
                        tipo_ngrama=ngrama
                    )

                    vectorizer.entrenar(dataframe)
                    matriz = vectorizer.transformar(dataframe)

                    vectorizer.crear_pickle(carpeta, nomb_ngrama, matriz, tipo_corpus, columna)

    print("Proceso completado.")

if __name__ == "__main__":
    main()




#csv_arxiv = pd.read_csv("arxiv_normalized_corpus.csv", delimiter="\t")
#csv_pubmed = pd.read_csv("pubmed_normalized_corpus.csv", delimiter="\t")

#title_arxiv = csv_arxiv["Title"].fillna('')
#title_pubmed = csv_pubmed["Title"].fillna('')

#abstract_arxiv = csv_arxiv["Abstract"].fillna('')
#abstract_pubmed = csv_pubmed["Abstract"].fillna('')