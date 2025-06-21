from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 Importa CORS
import tu_script

app = Flask(__name__)
CORS(app)  

@app.route('/')
def index():
    return "Buscador de Usuarios Activo"

@app.route('/buscar', methods=['POST'])
def buscar_usuario():
    data = request.get_json()
    usuario = data.get("usuario")
    resultado = tu_script.buscar(usuario)
    return jsonify(resultado)
