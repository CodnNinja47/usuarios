from flask import Flask, request, jsonify
from flask_cors import CORS
import tu_script
import os

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
