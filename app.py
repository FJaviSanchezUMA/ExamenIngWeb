from flask import Flask, request, jsonify, Response, send_from_directory, send_file
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from google.oauth2 import id_token
from google.auth.transport import requests
import pymongo, os
from flask_cors import CORS

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER']  = UPLOAD_FOLDER
CORS(app)


url_mongo_atlas = "mongodb+srv://admin:123asd@examen.ro6k8.mongodb.net/examen?retryWrites=true&w=majority"
client = pymongo.MongoClient(url_mongo_atlas)
mongo = client.get_database('examen')

########################  Usuario  ########################

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = mongo.db.usuarios.find()
    response = json_util.dumps(usuarios)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/<id>', methods=['GET'])
def get_usuario(id):
    usuario = mongo.db.usuarios.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/<id>', methods=['DELETE'])
def delete_usuario(id):
    mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'Usuario eliminado correctamente'}
    return response

@app.route('/usuarios/<id>', methods=['PUT'])
def update_usuario(id):
    nombre = request.json['nombre']
    direccion = request.json['direccion']
    password = request.json['password']
    email = request.json['email']

    if nombre and direccion and password and email:
        mongo.db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': {
            'nombre': nombre, 
            'email': email, 
            'password': password,
            'direccion': direccion
        }})
        response = jsonify({'mensaje': 'Usuario actualizado correctamente'})
        return response
    else: 
        return not_found()

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    nombre = request.json['nombre']
    password = request.json['password']
    email = request.json['email']
    direccion = request.json['direccion']

    if nombre and password and email and direccion:
        id = mongo.db.usuarios.insert(
            {'nombre': nombre, 'email': email, "password": password, 'direccion': direccion}
        )
        response = {
            'id': str(id),
            'nombre': nombre,
            'email': email,
            'password': password,
            'direccion': direccion
        }
        return response
    else: 
        return not_found()

@app.route('/usuarios/findByNombre/<nombre>', methods=['GET'])
def get_usuario_byNombre(nombre):
    myquery = { "nombre": { '$regex': ".*" + nombre + ".*" } }
    usuario = mongo.db.usuarios.find(myquery)
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/findByEmail/<email>', methods=['GET'])
def get_usuario_byEmail(email):
    myquery = { "email": email }
    usuario = mongo.db.usuarios.find(myquery)
    response = json_util.dumps(usuario)
    return Response(response, mimetype='application/json')

@app.route('/usuarios/login/<email>/<nombre>/<token>', methods=['GET'])
def login(email, nombre, token):
    try:
        CLIENT_ID = '475793231677-ki9jf2e8gb75ecr15gttcekmteqfp30k.apps.googleusercontent.com'
        id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

    except ValueError:
        error_response = jsonify({'Error': 'Error con el token'})
        return error_response

    myquery = { "email": email }
    usuario = mongo.db.usuarios.find_one(myquery)
    if not usuario:
        mongo.db.usuarios.insert(
            {'nombre': nombre, 'email': email, 'password': 'Desconocida', 'direccion': 'Desconocida'}
        )
    else:
        response = json_util.dumps(usuario)
        return Response(response, mimetype='application/json')

    responsee = jsonify({'mensaje': 'Usuario nuevo añadido correctamente'})
    return responsee




########################  Foto  ########################

@app.route('/fotos', methods=['GET'])
def get_fotos():
    fotos = mongo.db.fotos.find()
    response = json_util.dumps(fotos)
    return Response(response, mimetype='application/json')

@app.route('/fotos/<id>', methods=['GET'])
def get_foto(id):
    foto = mongo.db.fotos.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(foto)
    return Response(response, mimetype='application/json')

@app.route('/fotos/<id>', methods=['DELETE'])
def delete_foto(id):
    mongo.db.fotos.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'Foto eliminada correctamente'}
    return response

@app.route('/fotos/<id>', methods=['PUT'])
def update_foto(id):
    nombre = request.json['nombre']
    url = request.json['url']
    descripcion = request.json['descripcion']
    likes = request.json['likes']
    usuario_email = request.json['usuario_email']

    if nombre and url and descripcion and usuario_email:
        mongo.db.fotos.update_one({'_id': ObjectId(id)}, {'$set': {
            'nombre': nombre,
            'url': url,
            'descripcion': descripcion,
            'likes': likes,
            'usuario_email': usuario_email
        }})
        response = jsonify({'mensaje': 'Foto actualizada correctamente'})
        return response
    else: 
        return not_found()

@app.route('/fotos', methods=['POST'])
def create_foto():
    nombre = request.json['nombre']
    url = request.json['url']
    descripcion = request.json['descripcion']
    likes = request.json['likes']
    usuario_email = request.json['usuario_email']

    if nombre and url and descripcion and usuario_email:
        id = mongo.db.fotos.insert({
                'nombre': nombre,
                'url': url,
                'descripcion': descripcion,
                'likes': likes,
                'usuario_email': usuario_email
            }
        )
        response = {
            'id': str(id),
            'nombre': nombre,
            'url': url,
            'descripcion': descripcion,
            'likes': likes,
            'usuario_email': usuario_email
        }
        return response
    else: 
        return not_found()

@app.route('/fotos/findByNombre/<nombre>', methods=['GET'])
def get_foto_byNombre(nombre):
    myquery = { "nombre": { '$regex': ".*" + nombre + ".*" } }
    foto = mongo.db.fotos.find(myquery)
    response = json_util.dumps(foto)
    return Response(response, mimetype='application/json')

@app.route('/fotos/findByUsuario/<email>', methods=['GET'])
def get_foto_byUsuario(email):
    myquery = { "usuario_email": email }
    foto = mongo.db.fotos.find(myquery)
    response = json_util.dumps(foto)
    return Response(response, mimetype='application/json')

@app.route('/fotos/findByDescripcion/<descripcion>', methods=['GET'])
def get_foto_byDescripcion(descripcion):
    myquery = { "descripcion": { '$regex': ".*" + descripcion + ".*" } }
    foto = mongo.db.fotos.find(myquery)
    response = json_util.dumps(foto)
    return Response(response, mimetype='application/json')



########################  Comentario  ########################

@app.route('/comentarios', methods=['GET'])
def get_comentarios():
    comentarios = mongo.db.comentarios.find()
    response = json_util.dumps(comentarios)
    return Response(response, mimetype='application/json')

@app.route('/comentarios/<id>', methods=['GET'])
def get_comentario(id):
    comentario = mongo.db.comentarios.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(comentario)
    return Response(response, mimetype='application/json')

@app.route('/comentarios/<id>', methods=['DELETE'])
def delete_comentario(id):
    mongo.db.comentarios.delete_one({'_id': ObjectId(id)})
    response = {'mensaje': 'Comentario eliminado correctamente'}
    return response

@app.route('/comentarios/<id>', methods=['PUT'])
def update_comentario(id):
    contenido = request.json['contenido']
    usuario_nombre = request.json['usuario_nombre']
    grafiti_id = request.json['grafiti_id']

    if contenido and usuario_nombre and grafiti_id:
        mongo.db.comentarios.update_one({'_id': ObjectId(id)}, {'$set': {
            'contenido': contenido, 
            'usuario_nombre': usuario_nombre,
            'grafiti_id': grafiti_id
        }})
        response = jsonify({'mensaje': 'comentario actualizado correctamente'})
        return response
    else: 
        return not_found()

@app.route('/comentarios', methods=['POST'])
def create_comentario():
    contenido = request.json['contenido']
    usuario_nombre = request.json['usuario_nombre']
    grafiti_id = request.json['grafiti_id']

    if contenido and usuario_nombre and grafiti_id:
        id = mongo.db.comentarios.insert(
            {'contenido': contenido, 'usuario_nombre': usuario_nombre, "grafiti_id": grafiti_id}
        )
        response = {
            'id': str(id),
            'contenido': contenido,
            'usuario_nombre': usuario_nombre,
            'grafiti_id': grafiti_id
        }
        return response
    else: 
        return not_found()

@app.route('/comentarios/findByGrafiti/<id>', methods=['GET'])
def get_comentario_byGrafiti(id):
    myquery = { "grafiti_id": id }
    comentario = mongo.db.comentarios.find(myquery)
    response = json_util.dumps(comentario)
    return Response(response, mimetype='application/json')



########################  Media  ########################

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/media', methods=['POST'])
def guardar_imagen():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        response = jsonify({'foto': filename})
        return response
    return not_found()

@app.route('/media/<filename>', methods=['GET'])
def devolver_imagen(filename):
    return send_file(filename, as_attachment=True)



@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'mensaje': 'Recurso no encontrado',
        'estado': 404
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)
