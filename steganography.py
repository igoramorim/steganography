import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw


UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key2"

PATH_TO_UPLOAD = os.path.join(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image(image, msg):
    img = Image.open(image)
    encoded_img = img.copy()
    encoded_pixels = encoded_img.load()

    count = 0
    len_msg = len(msg)

    # TODO: usar pixels em posições não sequenciais
    # TODO: gerar uma key a partir dos pixels encodados
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = encoded_pixels[i, j][:-1]
            if count < len_msg:
                encoded_pixels[i, j] = (ord(msg[count]), g, b)
                count += 1
            else:
                encoded_pixels[i, j] = (r, g, b)

    filename = secure_filename(image.filename)
    encoded_img.save(PATH_TO_UPLOAD + '/encoded_' + filename)
    return filename


def decode_image(image, key):
    img = Image.open(image)
    pixels = img.load()

    msg = ''
    
    # TODO: fazer leitura da key para recuperar mensagem encodada
    for i in range(len('igor')):
        r = pixels[i, 0][0]
        msg += chr(r)

    return msg


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/encoded_<string:filename>')
def encoded_image(filename):
    path = PATH_TO_UPLOAD + '/encoded_' + filename
    # path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_puppy_text.png')
    return render_template('encoded.html', path=path, key="teste")
    # return send_file(PATH_TO_UPLOAD + '/encoded_' + filename, mimetype="image/gif")


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    message = request.form['message']
    
    # TODO: validacoes tamanho imagem, extensao, tamanho message etc
    # if file not in request.files:
    #     flash('No file part')
    #     return redirect(request.url)
    
    # if file.filename == '':
    #     flash('No selected file')
    #     return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = encode_image(file, message)
        
        # return send_file(PATH_TO_UPLOAD + '/encoded_' + filename, mimetype="image/gif")
        return redirect(url_for('encoded_image', filename=filename))
        
    # return render_template('index.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)