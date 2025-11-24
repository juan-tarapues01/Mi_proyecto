from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
# Configuración de la aplicación
app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'Base_datos',
    'user': 'postgres',
    'password': '123456',
    'port': 5432
}


def conectar_bd(): # crea funcion para crear una conexion con la base de datos 
    try:       # Intenta crear una conexión con los datos de configuración
        conexion = psycopg2.connect(**DB_CONFIG)   # Importa la librería psycopg2 para conectarse a PostgreSQL
        return conexion  # Si todo sale bien, devuelve la conexión
    except psycopg2.Error as e:   # Si ocurre un error, lo muestra en consola
        print(f" Error al conectar a la base de datos: {e}")
        return None  # Retorna None si falla la conexión

# Crea la tabla 'contactos' si aún no existe
def crear_tabla():
    conexion = conectar_bd()  # Se conecta a la base de datos
    if conexion:
        cursor = conexion.cursor()  # Crea un cursor para ejecutar SQL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id SERIAL PRIMARY KEY,              
            nombre VARCHAR(100) NOT NULL,       
            correo VARCHAR(100) NOT NULL,       
            mensaje TEXT,                       
            creado TIMESTAMP DEFAULT NOW()     
        );
        """)
        conexion.commit()  # Guarda los cambios en la base de datos
        cursor.close()     # Cierra el cursor
        conexion.close()   # Cierra la conexión

# Ruta principal del sitio web
@app.route('/')
def inicio():
    # Renderiza la página principal 'index.html'
    return render_template('index.html')

# Ruta para guardar los datos de un contacto
@app.route('/contacto', methods=['POST'])
def guardar_contactos():
    try:
        conexion = conectar_bd()  # Conexión a la base de datos
        if conexion is None:
            # Si no se puede conectar, devuelve un error
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        # Obtiene los datos enviados en formato JSON
        datos = request.get_json()
        nombre = datos.get('nombre', '').strip()   # Obtiene el nombre sin espacios
        correo = datos.get('correo', '').strip()   # Obtiene el correo sin espacios
        mensaje = datos.get('mensaje', '').strip() # Obtiene el mensaje sin espacios

        # Valida que nombre y correo no estén vacíos
        if not nombre or not correo:
            return jsonify({'error': 'Nombre y correo son obligatorios'}), 400

        cursor = conexion.cursor()  # Crea el cursor para ejecutar SQL
        sql_insertar = """
        INSERT INTO contactos (nombre, correo, mensaje)
        VALUES (%s, %s, %s)
        RETURNING id;
        """  # Consulta SQL para insertar un nuevo contacto

        # Ejecuta la consulta con los valores recibidos
        cursor.execute(sql_insertar, (nombre, correo, mensaje))
        contacto_id = cursor.fetchone()[0]  # Obtiene el ID del nuevo registro

        conexion.commit()  # Guarda los cambios
        cursor.close()     # Cierra el cursor
        conexion.close()   # Cierra la conexión

        # Devuelve un mensaje de éxito con el ID generado
        return jsonify({
            'mensaje': 'Contacto guardado exitosamente',
            'id': contacto_id
        }), 201

    except Exception as e:
        # Si ocurre un error, lo muestra y devuelve un mensaje de error
        print(f" Error al guardar el contacto: {e}")
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

# Ruta para consultar todos los contactos guardados
@app.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        conexion = conectar_bd()  # Conexión a la base de datos
        if conexion is None:
            # Si no se puede conectar, devuelve error
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        # Crea un cursor que devuelve los resultados como diccionarios
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        # Consulta todos los contactos ordenados del más reciente al más antiguo
        cursor.execute("SELECT * FROM contactos ORDER BY creado DESC;")
        contactos = cursor.fetchall()  # Obtiene todos los registros
        cursor.close()  # Cierra el cursor
        conexion.close()  # Cierra la conexión

        # Formatea la fecha de creación para que sea legible
        for contacto in contactos:
            if contacto['creado']:
                contacto['creado'] = contacto['creado'].strftime('%Y-%m-%d %H:%M:%S')

        # Devuelve la lista de contactos en formato JSON
        return jsonify(contactos), 200

    except Exception as e:
        # Muestra el error si ocurre algún problema
        print(f" Error al obtener contactos: {e}")
        return jsonify({'error': 'Error al obtener contactos'}), 500

# Punto de inicio del servidor Flask
if __name__ == '__main__':
    print(" Iniciando servidor...")  # Mensaje en consola al iniciar
    crear_tabla()  # Crea la tabla si no existe
    # Inicia el servidor en modo debug, accesible desde cualquier IP
    app.run(debug=True, host='0.0.0.0', port=5000)
