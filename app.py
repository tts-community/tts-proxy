import base64
import logging
import os
import re
import requests
import sys

from flask import Flask, abort, jsonify, redirect, request

try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except:
    pass

URL_RE = re.compile(os.environ.get('URL_REGEX') or r".+")
MAX_TIMEOUT=float(os.environ.get('MAX_TIMEOUT')) if 'MAX_TIMEOUT' in os.environ else 60.0

app = Flask(__name__)

if 'DYNO' in os.environ:
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)


def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json', 'text/plain'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/plain']


@app.route('/')
def index():
    return redirect('https://github.com/Benjamin-Dobell/tts-proxy')

@app.route('/forward', methods=['PUT'])
def forward_request():
    params = request.get_json(force=True)

    url = params.get('url')
    method = params.get('method')

    if not url:
        return ('URL not specified', 422)

    if not method:
        return ('HTTP method not specified', 422)

    if not URL_RE.fullmatch(url):
        return ('Specified URL is not permitted', 403)

    headers = {
        **(params.get('headers') or {}),
    }
    headers['X-Forwarded-For'] = '%s, %s' % (headers['X-Forwarded-For'], request.remote_addr) if 'X-Forwarded-For' in headers else request.remote_addr

    timeout = min(MAX_TIMEOUT, float(params['timeout'])) if 'timeout' in params else MAX_TIMEOUT

    body = None

    if 'body' in params:
        body = base64.b64decode(params['body']) if params.get('base64') else params['body']

    if body:
        body = body.encode()

    response = requests.request(method, url, timeout=timeout, headers=headers, data=body)

    wrapped_response = {
        'status_code': response.status_code,
        'headers': dict(response.headers),
    }

    if response.content:
        if 'content-type' in response.headers and response.headers['content-type'].lower() == 'application/octet-stream':
            wrapped_response['body'] = base64.b64encode(response.content)
            wrapped_response['base64'] = True
        else:
            wrapped_response['body'] = response.text

    return jsonify(wrapped_response)
