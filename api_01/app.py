from flask import Flask, request
import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs


app = Flask(__name__)


def default_handler(encoded_span):
    body = encoded_span

    return requests.post(
        "http://zipkin:9411/api/v1/spans",
        data=body,
        headers={'Content-Type': 'application/x-thrift'},
    )


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())


@zipkin_span(service_name='api_01', span_name='call_api_02')
def call_api_02():
    headers = create_http_headers_for_new_span()
    requests.get('http://api_02:5000/', headers=headers)
    return 'OK'


@app.route('/')
def index():
    with zipkin_span(
        service_name='api_01',
        span_name='index_api_01',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
    ):
        call_api_02()
    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)



