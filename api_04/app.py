from flask import Flask, request
import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.encoding import Encoding
import time, os


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

@zipkin_client_span(service_name='api_04', span_name='use_env_var_api_04')
def use_env_var():
    # This function tries to read env var
    app.logger.info("Read env Variable")
    app.logger.info(os.environ['NOTFOUND'])

@zipkin_client_span(service_name='api_04', span_name='test_env_var_api_04')
def test_env_var():
    app.logger.info("Test read env var")

@zipkin_client_span(service_name='api_04', span_name='call_api_05_from_api04')
def call_api_05():
    headers = create_http_headers()
    requests.get('http://api_05:5000/', headers=headers)
    return 'OK'

@app.route('/')
def index():
    with zipkin_span(
        service_name='api_04',
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers['X-B3-TraceID'],
            span_id=request.headers['X-B3-SpanID'],
            parent_span_id=request.headers['X-B3-ParentSpanID'],
            flags=request.headers['X-B3-Flags'],
            is_sampled=request.headers['X-B3-Sampled'],
        ),
        span_name='index_api_04',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        test_env_var()
        use_env_var()
        call_api_05()

    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
