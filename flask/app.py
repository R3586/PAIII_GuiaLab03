from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Cargar usuarios desde el archivo JSON
def cargar_usuarios():
    try:
        with open('users.json', 'r') as f:
            data = json.load(f)
            return data['users']
    except FileNotFoundError:
        return []

# Guardar usuarios en el archivo JSON
def guardar_usuarios(usuarios):
    with open('users.json', 'w') as f:
        json.dump({'users': usuarios}, f, indent=2)

# Ruta de autenticación
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({
                'error': 'Datos incompletos',
                'message': 'Se requieren usuario y contraseña'
            }), 400
        
        usuarios = cargar_usuarios()
        usuario = data['usuario'].strip()
        contraseña = data['contraseña']
        
        # Buscar usuario
        user_found = None
        for user in usuarios:
            if user['usuario'] == usuario and user['contraseña'] == contraseña:
                user_found = user.copy()
                # No devolver la contraseña por seguridad
                if 'contraseña' in user_found:
                    del user_found['contraseña']
                break
        
        if user_found:
            return jsonify([user_found]), 200
        else:
            return jsonify({
                'error': 'Credenciales inválidas',
                'message': 'Usuario o contraseña incorrectos'
            }), 401
            
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

# Ruta para obtener todos los usuarios (solo para testing)
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = cargar_usuarios()
    # No devolver contraseñas
    for user in usuarios:
        if 'contraseña' in user:
            del user['contraseña']
    return jsonify(usuarios)

# Ruta para registrar nuevo usuario
@app.route('/auth/registro', methods=['POST'])
def registro():
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data or 'email' not in data:
            return jsonify({
                'error': 'Datos incompletos',
                'message': 'Se requieren usuario, contraseña y email'
            }), 400
        
        usuarios = cargar_usuarios()
        usuario = data['usuario'].strip()
        email = data['email'].strip()
        
        # Verificar si el usuario ya existe
        for user in usuarios:
            if user['usuario'] == usuario:
                return jsonify({
                    'error': 'Usuario existente',
                    'message': 'El nombre de usuario ya está en uso'
                }), 409
            if user['email'] == email:
                return jsonify({
                    'error': 'Email existente',
                    'message': 'El email ya está registrado'
                }), 409
        
        # Crear nuevo usuario
        nuevo_usuario = {
            'id': len(usuarios) + 1,
            'usuario': usuario,
            'contraseña': data['contraseña'],
            'email': email,
            'nombre': data.get('nombre', usuario),
            'rol': data.get('rol', 'usuario'),
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d')
        }
        
        usuarios.append(nuevo_usuario)
        guardar_usuarios(usuarios)
        
        # No devolver la contraseña
        usuario_respuesta = nuevo_usuario.copy()
        if 'contraseña' in usuario_respuesta:
            del usuario_respuesta['contraseña']
            
        return jsonify(usuario_respuesta), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

# Ruta de verificación de salud del servidor
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando correctamente'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)