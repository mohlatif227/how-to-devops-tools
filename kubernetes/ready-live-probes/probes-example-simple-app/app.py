import os
import logging
import time
import signal
from distutils.util import strtobool
from flask import Flask
from flask import make_response

# Initializations
app = Flask("integration-application")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

liveness_env_should_fail = "FAIL_LIVE"
readiness_env_should_fail = "FAIL_READY"


@app.route('/live')
def live_check():
    should_fail_live = strtobool(os.environ.get(liveness_env_should_fail, False))
    logging.info(f'should fail in live probe: {should_fail_live}')
    if should_fail_live:
        return make_response("Internal Server Error", 500)
    return make_response("OK", 200)

@app.route('/fail_live')
def fail_live():
    os.environ[liveness_env_should_fail] = "True"
    return make_response("OK", 200)


@app.route('/start_live')
def start_live():
    os.environ[liveness_env_should_fail] = "False"
    return make_response("OK", 200)


@app.route('/ready')
def ready_check():
    should_fail_ready = strtobool(os.environ.get(readiness_env_should_fail, False))
    logging.info(f'should fail in ready probe: {should_fail_ready}')
    if should_fail_ready:
        return make_response("Internal Server Error", 500)
    return make_response("OK", 200)


@app.route('/fail_ready')
def fail_ready():
    os.environ[readiness_env_should_fail] = "True"
    return make_response("OK", 200)


@app.route('/start_ready')
def start_ready():
    os.environ[readiness_env_should_fail] = "False"
    return make_response("OK", 200)

@app.route('/exit/<exit_code>')
def exit_using_code(exit_code):
    exit(exit_code)

def exit_gracefully(signalNumber, frame):
    logging.critical('Received: %s' % signalNumber)
    exit(1)


signal.signal(signal.SIGTERM, exit_gracefully)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
