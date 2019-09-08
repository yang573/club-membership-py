import csv, re
from flask import Blueprint, request

from . import *
from .utility import *
from .db_func import *

bp = Blueprint('member', __name__)

EMAIL_REGEX = re.compile(r"([A-Z0-9_.+-]+@[A-Z0-9-]+\.[A-Z0-9-.]+)", re.IGNORECASE)

@bp.route('/', methods=["POST"])
def insert_new_member():
    sql = None
    cursor = conn.cursor()

    if EMAIL_REGEX.match(request.form['email']):
        sql = select(members, conditions=[(members[4], request.form['email'])])
    else:
        return {'message': "Invalid email"}, 400

    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        return {'message': "A member already exists with email {}"
                    .format(request.form['email'])}, 400

    values_list = [request.form['firstName'],
                    request.form['lastName'],
                    request.form['yearID'],
                    request.form['email'],
                    request.form['newsletter']
                    ]
    sql = insert(members, values_list, members[1:])
    cursor.execute(sql)

    memberID = cursor.lastrowid
    cursor.close()
    conn.commit()
    return {'memberID': memberID}, 201

