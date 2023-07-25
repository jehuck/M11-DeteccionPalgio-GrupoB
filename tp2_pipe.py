import os
import glob
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from nltk.tokenize import sent_tokenize

from tp2_modulos import CleanText


#creo el entorno
engine = create_engine('sqlite:///deteccion_plagio_tp2.sqlite3', echo=True)

#creo la base
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

#Defino las tablas

class Documentos(Base):
    __tablename__ = 'documentos'
    id = Column(Integer, primary_key=True)
    nombre_archivo = Column(String)
    texto = Column(String)
    
class Segmentos(Base):
    __tablename__ = 'segmentos'
    id_segmento = Column(Integer, primary_key=True)
    id_documento = Column(Integer, ForeignKey('documentos.id'))
    segmento_texto = Column(String)
    segmento_limpio = Column(String)
    init_s = Column(String)
    length_s = Column(Integer)
    
    documento = relationship("Documentos", backref="segmentos")

# Actualiza las tablas en la base de datos
Base.metadata.create_all(engine)


class Segmentation:
    
    def __init__(self, text):
        
        self.text = text
        #self.nombre = nombre
        
    def sentSegmentation(self):
        
        return sent_tokenize(self.text)
    
    def paraSegmentation(self):
        
        texto = self.text.split("\n\n")
        
        return list(filter(bool, texto))


# Función para guardar el contenido de un archivo en la base de datos
def guardar_documento(ruta_archivo=os.path.join(os.getcwd(), "plagiarism", "example", "corpus")):
    nombre_archivo = os.path.basename(ruta_archivo)
    with open(ruta_archivo, 'r', encoding= "utf-8-sig") as archivo:
        contenido = archivo.read()

    nuevo_documento = Documentos(nombre_archivo=nombre_archivo, texto=contenido)
    session.add(nuevo_documento)

    try:
        session.commit()
        print(f"Documento '{nombre_archivo}' guardado correctamente.")
    except IntegrityError:
        session.rollback()
        print(f"Error al guardar el documento '{nombre_archivo}'.")


def guardar_segmento(ruta_archivo, id_documento):
    
    #nombre_archivo = os.path.basename(ruta_archivo)
    with open(ruta_archivo, 'r', encoding= "utf-8-sig") as archivo:
        text = archivo.read()
        
        Seg = Segmentation(text)

        sentSeg = Seg.sentSegmentation()

        paraSeg = Seg.paraSegmentation()
        
    for i, value in enumerate (sentSeg):
        
        segmento_limpio = CleanText(str(value)).lemmatizeText()

        nuevo_segmento = Segmentos(id_documento=id_documento, segmento_texto=segmento_limpio, init_s=i, length_s=int(len(value.strip())))
        session.add(nuevo_segmento)

    try:
        session.commit()
        print(f"Segmentos del archivo '{ruta_archivo}' guardados correctamente.")
    except IntegrityError:
        session.rollback()
        print(f"Error al guardar los segmentos del archivo '{ruta_archivo}'.")  

def load_corpus_documents(carpeta):

    # Recorre los archivos de la carpeta
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta_archivo) and archivo.endswith('.txt'):
            guardar_documento(ruta_archivo)


def read_load_corpus_segments(carpeta):
    
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta_archivo) and archivo.endswith('.txt'):
            file = open(ruta_archivo, encoding= "utf-8-sig")
            
            print(archivo)

            documento = session.query(Documentos).filter_by(nombre_archivo=archivo).first()
            if documento:
                print(archivo, documento.id)
                guardar_segmento(ruta_archivo, documento.id)


def main():

    
    #Defino la carpeta donde esta el corpus y guardo los archivos en la base
    path = os.path.join(os.path.join(os.getcwd(), "plagiarism", "example", "corpus"))
    load_corpus_documents(path)
    read_load_corpus_segments(path)


if __name__ == '__main__' :
    main()
