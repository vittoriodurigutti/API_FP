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
    
@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    try:
        # Consulta para obtener los últimos 10 registros de la tabla sensor_datos
        sql_query = """
            SELECT nodo_id, temperatura, humedad, luz_ambiente, humedad_suelo_cap, 
                   humedad_suelo_res, nivel_agua, distancia, iluminacion, bomba
            FROM sensor_datos
            ORDER BY id_sensor DESC
            LIMIT 10
        """
        datos = ejecutar_consulta(sql_query)

        # Transformar resultados en un diccionario para enviar como JSON
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
                "bomba": bool(d[9])
            }
            for d in datos
        ]

        return jsonify(resultado), 200

    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({'status': 'Error al obtener datos', 'error': str(e)}), 500


if __name__ == '__main__':
    # Leer el puerto asignado de la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    # Ejecutar la API de Flask
    app.run(host='0.0.0.0', port=port, debug=True)
