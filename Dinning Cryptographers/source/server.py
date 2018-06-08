from flask import Flask
from werkzeug import serving
import ssl

app = Flask(__name__)


@app.route("/sign-in")
def sign_in():
    print("Got sign in from: ")
    return "Top-level content"


@app.route("/get-group")
def get_group():
    print("sending group")
    return "Group"


@app.route("/accept-group")
def accept_group():
    print("Group accepted by: ")
    return "Accepted"


@app.route("/deny-group")
def deny_group():
    print("Group denied!")
    return "Denied"


@app.route("/send-key")
def send_key():
    print("Got key for: ")
    return "Got key"


@app.route("/get-keys")
def get_keys():
    print("Sending all keys: ")
    return "Keys"


@app.route("/send-second-key")
def send_second_key():
    print("Got second key")
    return "Thank you"


@app.route("/get-second-keys")
def get_second_keys():
    print("Sending all second keys: ")
    return "Keys"


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("certs/ca/rootCA.crt")
    context.load_cert_chain("certs/server.crt", "certs/server.key")
    serving.run_simple("0.0.0.0", 8000, app, ssl_context=context)
