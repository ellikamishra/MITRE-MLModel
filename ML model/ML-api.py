from flask import Flask, request
from flask_cors import CORS, cross_origin
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
app = Flask(__name__)
CORS(app)


@app.route('/', methods = ['GET'])
def default():
    return "hi"

@app.route('/upload', methods = ['POST'])
def upload_file():
    file = request.files['file']
    print(file)
    print(type(file))
    file.save(secure_filename(file.filename))
    return "done"

# ef returnTech():
#     dict = predict(file)d

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=8089)
    app.run(debug = True)