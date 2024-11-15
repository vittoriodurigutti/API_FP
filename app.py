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

# Route to receive data from the ESP32
@app.route('/api', methods=['POST'])
def recibir_datos():
    try:
        # List of required fields based on the ESP32 data
        required_fields = [
            'id', 'temp', 'hum', 'luz', 'hum_cap', 'hum_res', 'nivel_agua',
            'distancia', 'iluminacion', 'bomba', 'nombre', 'apellido'
        ]

        # Check if all required fields are present in the request
        missing_fields = [field for field in required_fields if field not in request.form]
        if missing_fields:
            return jsonify({
                'status': 'Error al guardar los datos',
                'error': f'Faltan los campos: {", ".join(missing_fields)}'
            }), 400

        # Extract data sent by ESP32
        nodo_id = request.form['id']
        temperatura = float(request.form['temp'])
        humedad = float(request.form['hum'])
        luz_ambiente = float(request.form['luz'])
        humedad_suelo_cap = int(request.form['hum_cap'])
        humedad_suelo_res = int(request.form['hum_res'])
        nivel_agua = int(request.form['nivel_agua'])
        distancia = int(request.form['distancia'])
        iluminacion = bool(int(request.form['iluminacion']))
        bomba = bool(int(request.form['bomba']))
        nombre = request.form['nombre']
        apellido = request.form['apellido']

        # Log incoming data for debugging
        print(f"Received data: {request.form}")

        # Check if the device already exists in the dispositivo table
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
            dispositivo = ejecutar_consulta(sql_dispositivo, (nombre, apellido))
        
        # Ensure dispositivo is not None before accessing its ID
        if not dispositivo:
            return jsonify({
                'status': 'Error al guardar los datos',
                'error': 'Fallo al crear o recuperar el dispositivo en la base de datos'
            }), 500

        dispositivo_id = dispositivo[0][0]

        # Insert sensor data into the sensor_datos table
        sql_sensor_datos = """
            INSERT INTO sensor_datos (nodo_id, temperatura, humedad, luz_ambiente,
                                      humedad_suelo_cap, humedad_suelo_res, nivel_agua,
                                      distancia, iluminacion, bomba, dispositivo_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_sensor = (
            nodo_id, temperatura, humedad, luz_ambiente,
            humedad_suelo_cap, humedad_suelo_res, nivel_agua,
            distancia, iluminacion, bomba, dispositivo_id
        )

        # Try inserting sensor data and log success or failure
        if insertar_datos(sql_sensor_datos, datos_sensor):
            print("Datos del sensor insertados correctamente en sensor_datos.")
        else:
            print("Error al insertar datos del sensor en sensor_datos.")
            return jsonify({'status': 'Error al guardar los datos', 'error': 'Error al insertar en sensor_datos'}), 500

        # Insert into actuador_datos if the state of 'iluminacion' or 'bomba' changes
        if iluminacion or bomba:
            sql_actuador_datos = """
                INSERT INTO actuador_datos (nodo_id, tipo_actuador, estado_actuador, dispositivo_id)
                VALUES (%s, %s, %s, %s)
            """
            if iluminacion:
                datos_actuador_iluminacion = (nodo_id, 'Iluminación', 'Encendido', dispositivo_id)
                if insertar_datos(sql_actuador_datos, datos_actuador_iluminacion):
                    print("Datos de iluminación insertados correctamente en actuador_datos.")
                else:
                    print("Error al insertar datos de iluminación en actuador_datos.")

            if bomba:
                datos_actuador_bomba = (nodo_id, 'Bomba', 'Encendido', dispositivo_id)
                if insertar_datos(sql_actuador_datos, datos_actuador_bomba):
                    print("Datos de bomba insertados correctamente en actuador_datos.")
                else:
                    print("Error al insertar datos de bomba en actuador_datos.")

        return jsonify({'status': 'Datos guardados correctamente'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error al guardar los datos', 'error': str(e)}), 500

# Route to get the last 10 data entries
@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    try:
        # Consulta de los últimos 10 registros de sensor_datos
        sql_consulta_datos = """
            SELECT nodo_id, temperatura, humedad, luz_ambiente, humedad_suelo_cap, 
                   humedad_suelo_res, nivel_agua, distancia, iluminacion, bomba, dispositivo_id
            FROM sensor_datos
            ORDER BY id_sensor DESC
            LIMIT 10
        """

        # Ejecutar consulta y obtener datos
        datos = ejecutar_consulta(sql_consulta_datos)

        # Transformar resultados en un diccionario para garantizar formato JSON
        resultado = [
            {
                "nodo_id": d[0],
                "temperatura": d[1],
                "humedad": d[2],
                "luz_ambiente": d[3],
                "humedad_suelo_cap": d[4],
                "humedad_suelo_res": d[5],
                "nivel_agua": d[6],
                "distancia": d[7],
                "iluminacion": bool(d[8]),
                "bomba": bool(d[9]),
                "dispositivo_id": d[10],
            }
            for d in datos
        ]

        return jsonify(resultado), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error al obtener datos', 'error': str(e)}), 500

if __name__ == '__main__':
    # Read the assigned port from the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    # Run the Flask API
    app.run(host='0.0.0.0', port=port, debug=True)
