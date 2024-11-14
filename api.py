import os
import imp
import io
import subprocess
import time

from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api

import json

CHARSET  = "utf8mb4"
COLLATION = "utf8mb4_unicode_520_ci"

app = Flask(__name__)
api = Api(app)

#isascii = lambda s: len(s) == len(s.encode())

#Configurar Filebeat
DIR_BASE = os.getenv('DIR_BASE')
TESTING_LABEL = os.getenv('TESTING_LABEL')
LOG_FILE = os.getenv('LOGFILE')
HELPER_JSON_LOGGER = os.getenv('HELPER')
log = imp.load_source('log', HELPER_JSON_LOGGER)
logger = log.init_logger(LOG_FILE)
resutl = None
success = True
command = 'service filebeat start'
timeout_secs = 10

try:
    result = subprocess.call(command, shell=True)
    print(result)
except Exception as e:
    result = str(e)
    success = False

if not success:
    logger.error('Filebeat start failed: {}'.format(
        result))  # We do not stop the whole system, as individual results have also being stored as backup
else:
    logger.debug('Filebeat agent started successfully')


class App(Resource):
    def get(self, doc_id, version_code):
        if os.path.exists(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.apk'):
            with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.apk', 'rb') as apk:
                return send_file(io.BytesIO(apk.read()), attachment_filename=(doc_id + '.apk'),
                                 mimetype='application/octet-stream')
        else:
            return

    def post(self, doc_id, version_code):
        data_dir = os.path.join(DIR_BASE, doc_id, version_code)
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
            os.chmod(data_dir, 0o777)
        with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.apk', 'wb') as apk_file:
            try:
                apk_file.write(request.get_data())
                logger.info('The App has been storaged successfully', extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'testing_label': TESTING_LABEL})
                msg = "APK SAVED"
                return msg
            except:
                logger.error("The App couldn't have been storaged", extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'testing_label': TESTING_LABEL})
                msg = "APK NOTSAVED"
                return msg

class Bundle(Resource):
    
    def get(self, doc_id, version_code, bundle, split_name):
        if bundle == 'search':
            if os.path.exists(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.apk'):
                print('Path exists')
                list_apk_names = subprocess.check_output("ls {}/{}/{} ".format(DIR_BASE, doc_id, version_code), shell=True).decode('utf-8').split()
                list_not_apk = [] # Added David
                for i in range(len(list_apk_names)):
                    if not '.apk' in list_apk_names[i]:
                        list_not_apk.append(list_apk_names[i])
                        #list_apk_names.pop(i) Added David
                
                #Added David
                for not_apk in list_not_apk:
                    list_apk_names.remove(not_apk)

                if len(list_apk_names)>0:
                    js = {}
                    js['splits'] = []
                    for i in list_apk_names:
                        js['splits'].append(i)
                    return Response(json.dumps(js),  mimetype='application/json')
                     
                else:
                    return
            else:
                msg = "No hay ningun APK en la carpeta"
                return msg
        elif bundle == 'download':
            if os.path.exists(DIR_BASE + doc_id + '/' + version_code + '/' + split_name):
                with open(DIR_BASE + doc_id + '/' + version_code + '/' + split_name, 'rb') as apk:
                    return send_file(io.BytesIO(apk.read()), attachment_filename=(split_name + '.apk'),
                                     mimetype='application/octet-stream')
            else:
                return 
        else:
            return           

    def post(self, doc_id, version_code, bundle, split_name):
        data_dir = os.path.join(DIR_BASE, doc_id, version_code)
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
            os.chmod(data_dir, 0o777)
        
        with open(DIR_BASE + doc_id + '/' + version_code + '/' + split_name + '.apk', 'wb') as apk_file:  
            try:
                apk_file.write(request.get_data())
                logger.info('The App has been storaged successfully', extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'testing_label': TESTING_LABEL})
                msg = "APK SAVED"
                return msg
            except:
                logger.error("The App couldn't have been storaged", extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'testing_label': TESTING_LABEL})
                msg = "APK NOTSAVED"
                return msg


class PrivacyPolicy(Resource):
    def get(self, doc_id, version_code, typ):
        if typ == 'txt':
            pp = ''
            data = {}
            if os.path.exists(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.txt'):
                with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.txt', 'rb') as texto:
                    return send_file(io.BytesIO(texto.read()), attachment_filename=(doc_id + '.txt'), mimetype='text/plain')
            else:
                return
        if typ == 'html':
            if os.path.exists(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.html'):
                with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.html', 'rb') as text:
                    return send_file(io.BytesIO(text.read()), attachment_filename=(doc_id + '.html'), mimetype='text/html')
            else:
                return
        else:
            return

    def post(self, doc_id, version_code, typ):
        data = request.get_data()
        data_dir = os.path.join(DIR_BASE, doc_id, version_code)
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
            os.chmod(data_dir, 0o777)
        if typ == 'txt':
            try:
                with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.txt', 'wb') as txt_file:
                    txt_file.write(data)
                txt_file.close()
                logger.info('The Privacy Policy has been storaged successfully', extra={'apk': doc_id,
                        'version': version_code, 'container':'storage', 'type': typ, 'testing_label': TESTING_LABEL})
                msg = 'PP.txt SAVED'
                return msg
            except:
                logger.error("The Privacy Policy couldn't have been storaged", extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'type': typ, 'testing_label': TESTING_LABEL})
                msg = 'PP.txt  NOT SAVED'
                return msg
        if typ == 'html':
            try:
                with open(DIR_BASE + doc_id + '/' + version_code + '/' + doc_id + '.html', 'wb') as html_file:
                    html_file.write(data)
                html_file.close()
                logger.info('The Privacy Policy has been storaged successfully', extra={'apk': doc_id,
                        'version': version_code, 'container':'storage', 'type': typ, 'testing_label': TESTING_LABEL})
                msg = 'PP.html SAVED'
                return msg
            except:
                logger.error("The Privacy Policy couldn't have been storaged", extra={'apk': doc_id,
                    'version': version_code, 'container':'storage', 'type': typ, 'testing_label': TESTING_LABEL})
                msg = 'PP.html  NOT SAVED'
                return msg
        else:
            return



api.add_resource(App, '/app/apk/<doc_id>/<version_code>')
#api.add_resource(VersionCode, '/app/versioncode/<doc_id>')
api.add_resource(Bundle, '/app/bundle/<doc_id>/<version_code>/<bundle>/<split_name>')
api.add_resource(PrivacyPolicy, '/app/privacypolicy/<doc_id>/<version_code>/<typ>')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
