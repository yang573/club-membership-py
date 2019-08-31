#!/usr/bin/python3

import os
from flask import Flask
from database import event
#from flask import request
#from flask import jsonify

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads/')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(event.bp, url_prefix='/database/event')
#app.register_blueprint(member.bp, url_prefix='/database/member')

print("App print")

@app.route('/')
def default():
    return 'oops'

#def GetEmissions(company):
#    try:
#        with connection.cursor() as cursor:
#            sql = "SELECT * FROM Company WHERE Name LIKE %s"
#            cursor.execute(sql, [company])
#            result = cursor.fetchone()
#            return result
#    except Exception as ex:
#        print("Error: {}".format(ex))
#        return ex
#    finally:
#        cursor.close()
#
#@app.route('/database')
#
#@app.route('/company', methods=['GET'])
#def GetProductInfo():
#    company = request.args.get('company')
#    print('Company: {}'.format(company)) #DEBUG
#    emissions = GetEmissions(company)
#    print('Emissions: {}'.format(emissions)) #DEBUG
#    if emissions is None:
#        error = {
#                'error': 404,
#                'message': 'Company not found'
#                }
#        return jsonify(error)
#    else:
#        return jsonify(emissions)
#
