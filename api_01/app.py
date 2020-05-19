from flask import Flask, request
import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.encoding import Encoding
import sys, os

app = Flask(__name__)


def default_handler(encoded_span):
    body = encoded_span

    # decoded = _V1ThriftDecoder.decode_spans(encoded_span)
    app.logger.debug("body %s", body)

    # return requests.post(
    #     "http://zipkin:9411/api/v1/spans",
    #     data=body,
    #     headers={'Content-Type': 'application/x-thrift'},
    # )

    return requests.post(
        "http://zipkin:9411/api/v2/spans",
        data=body,
        headers={'Content-Type': 'application/json'},
    )


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


@zipkin_client_span(service_name='api_01', span_name='call_api_02')
def call_api_02():
    headers = create_http_headers()
    requests.get('http://api_02:5000/', headers=headers)
    return 'OK'


@zipkin_client_span(service_name='api_01', span_name='call_api_03_FROM_01')
def call_api_03():
    headers = create_http_headers()
    requests.get('http://api_03:5000/', headers=headers)
    return 'OK'


@zipkin_client_span(service_name='api_01', span_name='write_to_file_api1')
def write_to_file():
    # This function writes to file
    f = open("Justfile.txt", "a")
    for x in range(0, 100):
        f.write("Now the file has more content!")
    f.close()
    return 'OK'

@zipkin_client_span(service_name='api_01', span_name='read_from_file_api1')
def read_from_file():
    # This file reads from file
    f = open("Justfile.txt", "r")
    app.logger.info(f.read())
    os.remove("Justfile.txt")
    return 'OK'

@zipkin_client_span(service_name='api_01', span_name='call_api_05')
def call_api_05():
    headers = create_http_headers()
    requests.get('http://api_05:5000/', headers=headers)
    return 'OK'

@zipkin_client_span(service_name='api_01', span_name='call_api_07')
def call_api_07():
    headers = create_http_headers()
    requests.get('http://api_07:5000/', headers=headers)
    return 'OK'

@zipkin_client_span(service_name='api_01', span_name='call_api_10')
def call_api_10():
    headers = create_http_headers()
    requests.get('http://api_10:5000/', headers=headers)
    return 'OK'


@app.route('/')
def index():
    with zipkin_span(
        service_name='api_01',
        span_name='index_api_01',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        write_to_file()
        read_from_file()
        call_api_03()
        call_api_02()
        call_api_05()
        call_api_07()
        call_api_10()
    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
