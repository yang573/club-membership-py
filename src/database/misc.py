import csv, re
from flask import Blueprint, request

from . import *
from .utility import *
from .db_func import *

bp = Blueprint('misc', __name__)

# TODO: Add Mailchimp stats
@bp.route('/newsletter', methods=["GET"])
def get_newsletter_info():
    cursor = conn.cursor()

    sql = count(members, count_arg=members[5], conditions=[(members[5], 1)])
    cursor.execute(sql)
    signed_up = cursor.fetchone()

    sql = count(members)
    cursor.execute(sql)
    total = cursor.fetchone()

    return {'signed-up': signed_up, 'total-members': total}, 200

