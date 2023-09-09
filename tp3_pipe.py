from dataset import generate
from cluster import cluster_ip, agglomerative_cluster
from lxml import etree
import re
import codecs
import string
import operator
import functools
import glob
import os
import matplotlib.colors as mc
import nltk
import numpy as np
import textstat
import unicodedata
import pandas as pd
import math
import numpy as np
import fnmatch
#nltk.install("all")

from lexicalrichness import LexicalRichness
from collections import Counter

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag, map_tag
from nltk.tokenize import sent_tokenize

import nlp

from segmentador import Segmentador
from tp2_modulos import CleanText
from database_engineering import mongodb_esta_en_ejecucion, iniciar_mongodb, conectar_mongodb, insertar_datos
import perfmeasures
 # Feature Selection
from sklearn.feature_selection import VarianceThreshold




def crear_carpetas(version = ""):

    
    actual_directory = os.getcwd()

    ruta = os.path.join(actual_directory, "mini_corpus")
    ruta_del_directorio = str(ruta) + "\\*.txt"
    # Me produce una lista con los nombres de los archivos txt del corpus
    textos_originales = glob.glob(ruta_del_directorio)


    if not os.path.exists(str(actual_directory)+f"\\cleaned_corpus{version}"):
        os.mkdir(str(actual_directory)+f'\\cleaned_corpus{version}')
        
    cleaned_corpus = str(actual_directory)+f"\\cleaned_corpus{version}"

    # De esta manera le voy robo el nombre a los xml
    path_xml = str(actual_directory) + "\\mini_corpus" + "\\*.xml"
    xml_docs = glob.glob(path_xml)


    if not os.path.exists(str(actual_directory)+f"\\sospechoso{version}"):
        os.mkdir(str(actual_directory)+f'\\sospechoso{version}')
    else:
        print("Se elimino carpeta vieja de fragmentos sospechosos")
        patron_inicio = 'sosp*'
        patron_final = '*.txt'
        archivos = os.listdir(str(actual_directory)+f"\\sospechoso{version}")
        for archivo in archivos:
            if fnmatch.fnmatch(archivo, patron_inicio) and fnmatch.fnmatch(archivo, patron_final):
                ruta_completa = os.path.join(str(actual_directory)+f"\\sospechoso{version}", archivo)
                os.remove(ruta_completa)
                print(f"Eliminado: {ruta_completa}")

        
    if not os.path.exists(str(actual_directory) + f"\\xml\\output_xml{version}"):
        os.mkdir(str(actual_directory) + f"\\xml\\output_xml{version}")
    else:
        print("Se elimino carpeta vieja de fragmentos sospechosos en formato xml")
        patron_final = '*.xml'
        archivos = os.listdir(str(actual_directory) + f"\\xml\\output_xml{version}")
        for archivo in archivos:
            if fnmatch.fnmatch(archivo, patron_final):
                ruta_completa = os.path.join(str(actual_directory) + f"\\xml\\output_xml{version}", archivo)
                os.remove(ruta_completa)
                print(f"Eliminado: {ruta_completa}")


    sospechosos_path = str(actual_directory) + f"\\sospechoso{version}\\"
    output_xml = str(actual_directory) + f"\\xml\\output_xml{version}\\"

    return(textos_originales, sospechosos_path, output_xml, xml_docs)


def busqueda_plagio(textos_originales, sospechosos_path, output_xml, xml_docs, segment = "parraf", clustering = "dbscan"):
    


    # Comienzo a leer el conjunto de textos
    for i, archive in enumerate(textos_originales):
        
        print("File: " + str(i+1))
        
        f = open(archive, encoding="utf-8-sig")
        # Leo contenido del archivo
        text = f.read()

        # Cierro el txt
        f.close()           
        
        # Nombre de Archivo
        filename = os.path.basename(archive)
        # Separo nombre de archivo y extension
        filename2, extension = os.path.splitext(filename)
        
        Seg = Segmentador(text)
        # La variable data_text posee el texto completo, separado en párrafos

        if segment == "content":
            data_text = Seg.content_segmentation()
        
        else:
            data_text = Seg.para_segmentation()
        


        data_list = []

        lista_to_df = []
        
        for j, segmento in enumerate(data_text):

            segmento_limpio = CleanText(str(segmento)).lemmatizeText()

            data_list.append([j, re.sub("\n", " ", segmento_limpio), len(re.sub("\n", " ", segmento_limpio))])

            lista_to_df.append(
                [j, filename, nlp.getnumOfPunctN(segmento_limpio), nlp.gettypeToken(segmento_limpio)]
            )                        
        
        df = pd.DataFrame(lista_to_df, columns=["index", "filename", "getnumOfPunctN", "gettypeToken"])
        
        
        #df["getfleshReadingEase"] = df["getfleshReadingEase"] / df["getfleshReadingEase"].max()
        
        # Seleccionar los valores numéricos del df
        # Este paso se realiza para ir viendo que genera cada párrafo del txt y como fue convertido a un vector
        dataframe = df.iloc[:,[2,3]]
        
        # Aprendizaje No Supervisado
        if clustering == "dbscan":
            cluster = cluster_ip(dataframe, 4, "cosine")
        elif clustering == "aglomerative":
            cluster = agglomerative_cluster(dataframe, 4)
        labels = cluster.labels_    
        df["labels"] = labels
        
        realClusterNum=len(set(labels)) - (1 if -1 in labels else 0)
        clusterNum=len(set(labels))
        n_noise = list(labels).count(-1) 
        
        print("Estimated number of clusters: %d" % realClusterNum)
        print("Estimated number of noise points: %d" % n_noise)
        counts = df["labels"].value_counts().to_dict()
        print(counts)
        
        # Me sirve para guardar los casos de plagio y compararlos
        xml_name = os.path.basename(xml_docs[i])
        xml_name2, extension = os.path.splitext(xml_name)
        
        # Se crea el archivo txt donde se guardaran los fragmentos sospechosos
        sherlock = codecs.open(sospechosos_path + "sosp" + filename,"w","utf-8")
        
        # Los fragmentos que fueron clasificados como plagio
        # Se guardan en el archivo .txt
        # Tener en cuenta que el dataframe y la lista data_list, manejan los mismos índices
        # Por eso, si en el dataframe se encuentra un "-1" es porque este es un outlier
        for x in range(len(df["labels"])):
            l = df["labels"][x]
            if l == -1:
                print(data_list[x][1])
                print(x)
                sherlock.write(data_list[x][1]+os.linesep)       
                
        sherlock.close()    
        
        document_el = etree.Element("document", reference = xml_name2 + ".txt")

        offset = []

        init = 0

        sum_length = []

        last = -1

        for y in range(len(df["labels"])):       

            l = df["labels"][y]

            if l == -1:

                print(y)

                if y == 0:

                    sum_length.append([init, data_list[y][2]])

                    print(f"Case 0, y = 0")

                elif y != 0 and (y == (last + 1) or len(sum_length) == 0):

                    sum_length.append([init, data_list[y][2]])

                    print(f"Case 1, y == (last + 1)")

                elif y != 0 and y != (last + 1):

                    this_length = sum([l[1] for l in sum_length])

                    feature_el = etree.SubElement(document_el, "feature", name="detected-plagiarism", this_offset=str(sum_length[0][0]), this_length=str(this_length))

                    sum_length.clear()

                    print(sum_length)

                    sum_length.append([init, data_list[y][2]])

                    print(f"Case 2, y != (last + 1)")   

                last = y

            if y == (len(df["labels"]) - 1) and len(sum_length) > 0:

                print("Entro2")

                this_length = sum([l[1] for l in sum_length])

                feature_el = etree.SubElement(document_el, "feature", name="detected-plagiarism", this_offset=str(sum_length[0][0]), this_length=str(this_length))


            init += data_list[y][2] + 1





        et = etree.ElementTree(document_el)
        with open(output_xml+xml_name, "wb") as fe:
            et.write(fe, encoding="utf-8", xml_declaration=None, pretty_print=True)

def ejecutando_perfmeasures(xml_outputs):
    perfmeasures.ejecutable(xml_outputs)

def main():

    # Primer prueba con segmentación por párrafos y dbscan
    textos_originales1, sospechosos_path1, output_xml1, xml_docs1 = crear_carpetas(version="seg_parr_dbscan")
    busqueda_plagio(textos_originales1, sospechosos_path1, output_xml1, xml_docs1, segment = "parraf", clustering="dbscan")

    resultados1 = ejecutando_perfmeasures(output_xml1)


    # Segunda prueba con segmentación por contenido y agglomerative
    textos_originales2, sospechosos_path2, output_xml2, xml_docs2 = crear_carpetas(version="seg_content_agglo")
    busqueda_plagio(textos_originales2, sospechosos_path2, output_xml2, xml_docs2, segment = "content", clustering="aglomerative")

    resultados2 = ejecutando_perfmeasures(output_xml2)


    return resultados1, resultados2




if __name__ == '__main__':   
    resultado1, resultado2 = main()


    
    database_name = "deteccion_plagio"
    collection_name = "resultados"
    
    if mongodb_esta_en_ejecucion():
        print("MongoDB está en ejecución.")

        conectar_mongodb(database_name, collection_name)
    
    
        # Llamar a la función insertar_datos para insertar los datos en la colección
        insertar_datos(database_name, collection_name, resultado1)
        insertar_datos(database_name, collection_name, resultado2)


    else:
        print("MongoDB no está en ejecución.")
        iniciar_mongodb()
        insertar_datos(database_name, collection_name, resultado1)
        insertar_datos(database_name, collection_name, resultado2)
         