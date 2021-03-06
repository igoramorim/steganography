import os
import random
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw


UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = set(['png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key2"

PATH_TO_UPLOAD = os.path.join(app.config['UPLOAD_FOLDER'])
MAX_LEN_MESSAGE = 140


def encode_image(image, msg):
    img = Image.open(image)
    encoded_img = img.copy()
    encoded_pixels = encoded_img.load()

    key = ''
    positions = []

    for i in range(len(msg)):
        position = get_position(img.size[0], img.size[1], positions)
        x = position[0]
        y = position[1]

        r, g, b = encoded_pixels[x, y]
        pixel_old = encoded_pixels[x, y][0]
        encoded_pixels[x, y] = (ord(msg[i]), g, b)

        # print(encoded_pixels[x, y])
        positions.append(format_position_encode(position))
        print('x: {} \t\ty: {} \t\tletra: {} \tencoded: {} \tpixel_old: {}'.format(str(x), str(y), msg[i], ord(msg[i]), pixel_old))
        # print('')

    filename = secure_filename(image.filename)
    encoded_img.save(PATH_TO_UPLOAD + '/encoded_' + filename)
    key = generate_key(positions)
    return filename, key


def generate_key(positions):
    key = ''
    for pos in positions:
        for coord in pos:
            key += coord

    return key


def format_position_encode(position):
    new_position = []
    for coord in position:
        prefix = ''
        dif = 4 - len(str(coord))
        prefix = '0' * dif

        new_position.append(prefix + str(coord))

    # print('x: {} \ty: {}'.format(new_position[0], new_position[1]))
    return new_position


def get_position(x_len, y_len, positions):
    x = random.randrange(x_len)
    y = random.randrange(y_len)
    position = [x, y]
    if position in positions:
        # print('duplicada')
        # print(position)
        get_position(x_len, y_len, positions)
    else:
        return position


def decode_image(image, key):
    img = Image.open(image)
    pixels = img.load()

    msg = ''
    positions = []

    for i in range(0, len(key), 8):
        coord = key[i:i+8]
        x = coord[:4]
        y = coord[4:]
        positions.append([int(x), int(y)])
        # print('x: {} \ty: {}'.format(x, y))

    for pos in positions:
        x = pos[0]
        y = pos[1]
        pixel = pixels[x, y][0]
        print('x: {} \ty: {} \tpixel: {} \tmsg: {}'.format(x, y, pixel, chr(pixel)))
        msg += chr(pixel)

    return msg


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_upload_encode(file, message):
    if not file or file.filename == '' or not allowed_file(file.filename):
        flash('Please, upload a PNG image to encode.')
        return False

    if not message or len(message) <= 0:
        flash('Please, enter a message to encode!')
        return False

    if MAX_LEN_MESSAGE < len(message):
        flash('Message too large. Max length: 140 characters.')
        return False

    return True


def validate_upload_decode(file, message):
    if not file or file.filename == '' or not allowed_file(file.filename):
        flash('Please, upload a PNG image to decode.')
        return False

    if not message or len(message) <= 0:
        flash('Please, enter the key of the image to decode!')
        return False

    return True


#####################################################################################
#                               ENDPOINTS
#####################################################################################


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/encoded_<string:filename>key<string:key>')
def encoded_image(filename, key):
    path = PATH_TO_UPLOAD + '/encoded_' + filename
    # path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_puppy_text.png')
    return render_template('encoded.html', path=path, key=key)
    # return send_file(PATH_TO_UPLOAD + '/encoded_' + filename, mimetype="image/gif")


@app.route('/upload', methods=['POST'])
def upload_file():
    if validate_upload_encode(request.files['image'], request.form['message']):
        file = request.files['image']
        message = request.form['message']
        encoded_image = encode_image(file, message)
        return redirect(url_for('encoded_image', filename=encoded_image[0], key=encoded_image[1]))
    else:
        return redirect(url_for('index'))


@app.route('/decode', methods=['POST'])
def decoded_file():
    if validate_upload_decode(request.files['imageEncoded'], request.form['key']):
        file = request.files['imageEncoded']
        key = request.form['key']
        decoded_message = decode_image(file, key)
        return render_template('decoded.html', decoded_message=decoded_message)
    else:
        return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)