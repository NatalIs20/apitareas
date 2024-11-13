from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS  # Para habilitar CORS si es necesario

app = Flask(__name__)

# Configuración de la conexión con MongoDB
app.config["MONGO_URI"] = "mongodb+srv://Natali:NCA8711N.@natali.1sjupkd.mongodb.net/tareas_db"  # Cambia esto si tienes otra URI
mongo = PyMongo(app)
CORS(app)  # Habilitar CORS para permitir peticiones desde diferentes orígenes

tareas_collection = mongo.db.tareas  # Colección para almacenar las tareas

# Función de utilidad para manejar respuestas de error
def crear_respuesta_error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo

# Crear una tarea
@app.route('/tareas', methods=['POST'])
def crear_tarea():
    data = request.get_json()
    titulo = data.get('titulo')
    descripcion = data.get('descripcion', '')
    completada = data.get('completada', False)

    # Validación de título y descripción
    if not titulo or not isinstance(titulo, str) or len(titulo) > 100:
        return crear_respuesta_error("El título es requerido y debe ser un texto con máximo 100 caracteres.", 400)
    if descripcion and (not isinstance(descripcion, str) or len(descripcion) > 300):
        return crear_respuesta_error("La descripción debe ser un texto con máximo 300 caracteres.", 400)

    nueva_tarea = {"titulo": titulo, "descripcion": descripcion, "completada": completada}
    tarea_id = tareas_collection.insert_one(nueva_tarea).inserted_id

    return jsonify({
        "id": str(tarea_id),
        "titulo": titulo,
        "descripcion": descripcion,
        "completada": completada
    }), 201

# Leer todas las tareas
@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    tareas = []
    for tarea in tareas_collection.find():
        tareas.append({
            "id": str(tarea["_id"]),
            "titulo": tarea["titulo"],
            "descripcion": tarea.get("descripcion", ""),
            "completada": tarea["completada"]
        })
    return jsonify(tareas), 200

# Leer una tarea específica por ID
@app.route('/tareas/<string:id>', methods=['GET'])
def obtener_tarea(id):
    try:
        tarea = tareas_collection.find_one({"_id": ObjectId(id)})
    except:
        return crear_respuesta_error("ID de tarea inválido.", 400)

    if not tarea:
        return crear_respuesta_error("Tarea no encontrada.", 404)

    return jsonify({
        "id": str(tarea["_id"]),
        "titulo": tarea["titulo"],
        "descripcion": tarea.get("descripcion", ""),
        "completada": tarea["completada"]
    }), 200

# Actualizar una tarea por ID
@app.route('/tareas/<string:id>', methods=['PUT'])
def actualizar_tarea(id):
    data = request.get_json()

    try:
        tarea = tareas_collection.find_one({"_id": ObjectId(id)})
    except:
        return crear_respuesta_error("ID de tarea inválido.", 400)

    if not tarea:
        return crear_respuesta_error("Tarea no encontrada.", 404)

    titulo = data.get('titulo', tarea['titulo'])
    descripcion = data.get('descripcion', tarea.get('descripcion', ''))
    completada = data.get('completada', tarea['completada'])

    # Validación de título y descripción al actualizar
    if titulo and (not isinstance(titulo, str) or len(titulo) > 100):
        return crear_respuesta_error("El título debe ser un texto con máximo 100 caracteres.", 400)
    if descripcion and (not isinstance(descripcion, str) or len(descripcion) > 300):
        return crear_respuesta_error("La descripción debe ser un texto con máximo 300 caracteres.", 400)

    tareas_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"titulo": titulo, "descripcion": descripcion, "completada": completada}}
    )

    return jsonify({
        "id": id,
        "titulo": titulo,
        "descripcion": descripcion,
        "completada": completada
    }), 200

# Eliminar una tarea por ID
@app.route('/tareas/<string:id>', methods=['DELETE'])
def eliminar_tarea(id):
    try:
        tarea = tareas_collection.find_one({"_id": ObjectId(id)})
    except:
        return crear_respuesta_error("ID de tarea inválido.", 400)

    if not tarea:
        return crear_respuesta_error("Tarea no encontrada.", 404)

    tareas_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"mensaje": "Tarea eliminada"}), 200

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
