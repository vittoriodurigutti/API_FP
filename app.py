from flask import Flask, request, jsonify, render_template
from db import ejecutar_consulta, insertar_datos
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/api', methods=['POST'])
def recibir_datos():
    try:
        # Campos requeridos según el envío del ESP32
        required_fields = [
            'id', 'temp', 'hum', 'luz', 'hum_cap', 'hum_res', 'nivel_agua',
            'distancia', 'iluminacion', 'bomba'
        ]

        # Validar que todos los campos requeridos estén presentes en el POST
        missing_fields = [field for field in required_fields if field not in request.form]
        if missing_fields:
            return jsonify({
                'status': 'Error al guardar los datos',
                'error': f'Faltan los campos: {", ".join(missing_fields)}'
            }), 400

        # Extraer y convertir los datos enviados por el ESP32
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

        # Log de datos recibidos
        print(f"Datos recibidos: {request.form}")

        # Insertar datos del sensor en la tabla sensor_datos
        sql_sensor_datos = """
            INSERT INTO sensor_datos (nodo_id, temperatura, humedad, luz_ambiente,
                                      humedad_suelo_cap, humedad_suelo_res, nivel_agua,
                                      distancia, iluminacion, bomba)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_sensor = (
            nodo_id, temperatura, humedad, luz_ambiente,
            humedad_suelo_cap, humedad_suelo_res, nivel_agua,
            distancia, iluminacion, bomba
        )
        insertar_datos(sql_sensor_datos, datos_sensor)

        # Insertar datos de actuadores si es necesario
        if iluminacion or bomba:
            sql_actuador_datos = """
                INSERT INTO actuador_datos (nodo_id, tipo_actuador, estado_actuador)
                VALUES (%s, %s, %s)
            """
            if iluminacion:
                datos_actuador_iluminacion = (nodo_id, 'Iluminación', 'Encendido')
                insertar_datos(sql_actuador_datos, datos_actuador_iluminacion)

            if bomba:
                datos_actuador_bomba = (nodo_id, 'Bomba', 'Encendido')
                insertar_datos(sql_actuador_datos, datos_actuador_bomba)

        return jsonify({'status': 'Datos guardados correctamente'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'Error al guardar los datos', 'error': str(e)}), 500

if __name__ == '__main__':
    # Leer el puerto asignado de la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    # Ejecutar la API de Flask
    app.run(host='0.0.0.0', port=port, debug=True)
