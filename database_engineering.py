import pymongo
import psutil
import subprocess
import json

def mongodb_esta_en_ejecucion():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if 'mongod' in proc.info['name']:
            return True
    return False


def conectar_mongodb(database_name, collection_name):
    # Establecemos la conexión con MongoDB
    cliente = pymongo.MongoClient("mongodb://localhost:27017/")  
    db = cliente[database_name]

    # Comprobar si la base de datos existe
    if database_name not in cliente.list_database_names():
        # Si la base de datos no existe, créala aquí
        db = cliente[database_name]
        print(f"La base de datos '{database_name}' ha sido creada.")
    
    coleccion = db[collection_name]

    # Comprobar si la colección existe
    if collection_name not in db.list_collection_names():
        # Si la colección no existe, créala aquí
        db.create_collection(collection_name)
        print(f"La colección '{collection_name}' ha sido creada.")
    
    # Cerrar la conexión
    cliente.close()

def insertar_datos(database_name, collection_name, data):
    # Establecer la conexión con MongoDB
    cliente = pymongo.MongoClient("mongodb://localhost:27017/")  # Cambia la URL si es necesario
    db = cliente[database_name]
    coleccion = db[collection_name]

    # Convertir el diccionario en una cadena JSON
    result_json = json.dumps(data)
    
    # Insertar la cadena JSON como un documento en la colección
    coleccion.insert_one(json.loads(result_json))

    # Insertar datos en la colección
    #coleccion.insert_one(data)
    print("Datos insertados en la colección.")

    # Cerrar la conexión
    cliente.close()

def iniciar_mongodb():
    if not mongodb_esta_en_ejecucion():
        try:
            subprocess.Popen(["mongod"])
            print("MongoDB se ha iniciado correctamente.")
        except Exception as e:
            print(f"Error al iniciar MongoDB: {e}")
    else:
        print("MongoDB ya está en ejecución.")
        