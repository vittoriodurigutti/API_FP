# app.py
from flask import Flask, request, jsonify, render_template
from db import ejecutar_consulta, insertar_datos
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sobre-nosotros.html')
def sobre_nosotros():
    return render_template('sobre-nosotros.html')

@app.route('/proyecto.html')
def proyecto():
    return render_template('proyecto.html')

# Route to receive data from the ESP32
@app.route('/api', methods=['POST'])
def recibir_datos():
    try:
        # Extract data sent by ESP32
        nodo_id = request.form['id']
        temperatura = request.form['temp']
        humedad = request.form['hum']
        luz_ambiente = request.form['luz']
        humedad_suelo_cap = request.form['hum_cap']
        humedad_suelo_res = request.form['hum_res']
        nivel_agua = request.form['nivel_agua']
        nombre = request.form['nombre']
        apellido = request.form['apellido']

        # Check if the device already exists in the database
        sql_dispositivo = """
            SELECT id_dispositivo FROM dispositivo
            WHERE nombre = %s AND apellido = %s
        """
        dispositivo = ejecutar_consulta(sql_dispositivo, (nombre, apellido))

        if not dispositivo:
            # If the device does not exist, insert it
            sql_insert_dispositivo = """
                INSERT INTO dispositivo (nombre, apellido)
                VALUES (%s, %s)
            """
            insertar_datos(sql_insert_dispositivo, (nombre, apellido))
            # Get the ID of the new device
            dispositivo_id = ejecutar_consulta(sql_dispositivo, (nombre, apellido))[0]['id_dispositivo']
        else:
            dispositivo_id = dispositivo[0]['id_dispositivo']

        # Insert sensor data into the sensor_datos table
        sql_sensor_datos = """
            INSERT INTO sensor_datos (nodo_id, temperatura, humedad, luz_ambiente,
                                      humedad_suelo_cap, humedad_suelo_res, nivel_agua, dispositivo_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_sensor = (
            nodo_id, temperatura, humedad, luz_ambiente,
            humedad_suelo_cap, humedad_suelo_res, nivel_agua, dispositivo_id
        )
        insertar_datos(sql_sensor_datos, datos_sensor)

        return jsonify({'status': 'Datos guardados correctamente'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error al guardar los datos', 'error': str(e)}), 500

# Route to get the last 10 data entries
@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    try:
        # Query the last 10 records from the database
        sql_consulta_datos = """
            SELECT nodo_id, temperatura, humedad, luz_ambiente, humedad_suelo_cap, 
                   humedad_suelo_res, nivel_agua, dispositivo_id
            FROM sensor_datos
            ORDER BY id_sensor DESC
            LIMIT 10
        """

        datos = ejecutar_consulta(sql_consulta_datos)

        return jsonify(datos), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error al obtener datos', 'error': str(e)}), 500

if __name__ == '__main__':
    # Read the assigned port from the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    # Run the Flask API
    app.run(host='0.0.0.0', port=port, debug=True)
