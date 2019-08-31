import os, re
from werkzeug import secure_filename
from flask import current_app as app

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def absolute_upload_path(file):
    name = secure_filename(file.filename)
    return os.path.join(app.config['UPLOAD_FOLDER'], name)

def save_file(file, path):
    return file.save(path)

def delete_file(path):
    os.remove(path)

def get_header_index(header, ordered_header):
    order = []
    for x in ordered_header:
        p = re.compile(x, re.IGNORECASE)
        index = [i for i, item in enumerate(header) if re.search(p, item)]
        if len(index) is 1:
            order.append(index[0])
        elif index:
            print('More than one result found found for "{}"'.format(x))
            order.append(index[0])
        else:
            print('"{}" not found.'.format(x))
            order.append(-1)

    print(order)
    return order

