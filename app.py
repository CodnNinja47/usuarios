from flask import Flask, request, jsonify
import tu_script

app = Flask(__name__)

@app.route('/')
def index():
    return "Buscador de Usuarios Activo"

@app.route('/buscar', methods=['POST'])
def buscar_usuario():
    data = request.get_json()
    usuario = data.get("usuario")
    resultado = tu_script.buscar(usuario)
    return jsonify(resultado)
