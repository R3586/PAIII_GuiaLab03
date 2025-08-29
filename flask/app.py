from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Cargar usuarios desde el archivo JSON
def cargar_usuarios():
    try:
        logger.info("Cargando usuarios desde users.json")
        with open('users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Se cargaron {len(data.get('users', []))} usuarios")
            return data.get('users', [])
    except FileNotFoundError:
        logger.error("Archivo users.json no encontrado")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado al cargar usuarios: {e}")
        return []

# Ruta de autenticación - Versión mejorada con debugging
@app.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    try:
        logger.info("Solicitud POST recibida en /auth/login")
        
        # Manejar preflight requests de CORS
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST')
            return response
        
        # Verificar si hay datos JSON en la solicitud
        if not request.is_json:
            logger.warning("Solicitud sin datos JSON")
            return jsonify({
                'error': 'Formato inválido',
                'message': 'Se esperaba application/json'
            }), 400
        
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")
        
        if not data:
            logger.warning("Datos JSON vacíos o inválidos")
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'El cuerpo de la solicitud está vacío o es inválido'
            }), 400
        
        if 'usuario' not in data or 'contraseña' not in data:
            logger.warning("Datos incompletos: falta usuario o contraseña")
            return jsonify({
                'error': 'Datos incompletos',
                'message': 'Se requieren usuario y contraseña'
            }), 400
        
        usuarios = cargar_usuarios()
        usuario = data['usuario'].strip().lower() if data['usuario'] else ''
        contraseña = data['contraseña']
        
        logger.debug(f"Buscando usuario: {usuario}")
        
        # Buscar usuario
        user_found = None
        for user in usuarios:
            if user.get('usuario', '').lower() == usuario and user.get('contraseña') == contraseña:
                user_found = user.copy()
                # No devolver la contraseña por seguridad
                user_found.pop('contraseña', None)
                logger.info(f"Usuario encontrado: {usuario}")
                break
        
        if user_found:
            response_data = [user_found]
            logger.debug(f"Respuesta exitosa: {response_data}")
            
            response = jsonify(response_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            logger.warning(f"Credenciales inválidas para usuario: {usuario}")
            return jsonify({
                'error': 'Credenciales inválidas',
                'message': 'Usuario o contraseña incorrectos'
            }), 401
            
    except Exception as e:
        logger.error(f"Error interno en login: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado'
        }), 500

# Ruta para verificar que el servidor está funcionando
@app.route('/')
def index():
    return jsonify({
        'message': 'API de Autenticación Flask',
        'status': 'active',
        'endpoints': {
            'login': '/auth/login (POST)',
            'health': '/health (GET)'
        }
    })

# Ruta de verificación de salud del servidor
@app.route('/health', methods=['GET'])
def health_check():
    try:
        usuarios = cargar_usuarios()
        return jsonify({
            'status': 'ok', 
            'message': 'Servidor funcionando correctamente',
            'usuarios_registrados': len(usuarios)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error en health check: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando servidor Flask en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
