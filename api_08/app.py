from flask import Flask, request
import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.encoding import Encoding
import sys, os


app = Flask(__name__)


def default_handler(encoded_span):
    body = encoded_span

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

@zipkin_client_span(service_name='api_08', span_name='just_message_api08')
def just_message_08():
    app.logger.info("Just message from API 08")
    return 'OK'

@zipkin_client_span(service_name='api_08', span_name='call_api_09_from_08')
def call_api_09():
    headers = create_http_headers()
    requests.get('http://api_09:5000/', headers=headers)
    return 'OK'

@app.route('/')
def index():
    with zipkin_span(
        service_name='api_08',
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers['X-B3-TraceID'],
            span_id=request.headers['X-B3-SpanID'],
            parent_span_id=request.headers['X-B3-ParentSpanID'],
            flags=request.headers['X-B3-Flags'],
            is_sampled=request.headers['X-B3-Sampled'],
        ),
        span_name='index_api_08',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        just_message_08()
        call_api_09()

    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
