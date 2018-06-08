from flask import Flask, request, jsonify, Response
from werkzeug import serving
import ssl
import OpenSSL
from random import randint

app = Flask(__name__)

NUMBER_OF_CLIENTS = 3

G_LENGTH = 30

signedClients = []

modulo = None
g = None

clientsThatAcceptedGroup = []


class PeerCertWSGIRequestHandler(serving.WSGIRequestHandler):

    def make_environ(self):
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, x509_binary)
        environ['peercert'] = x509
        return environ


def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True


def generate_big_prime(n):
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p


def is_germain_prime(a):
    return is_prime(int((a - 1) / 2), 1000)


def get_client_serial_number(environ):
    return environ["peercert"].get_serial_number()


def generateG():
    global modulo, g
    temp_modulo = generate_big_prime(G_LENGTH)
    while not is_germain_prime(temp_modulo):
        temp_modulo = generate_big_prime(G_LENGTH)
    modulo = temp_modulo
    g = randint(2, modulo - 1)
    print("Generated g: {}, modulus: {}".format(g, modulo))


@app.route("/sign-in")
def sign_in():
    global signedClients
    client_serial = get_client_serial_number(request.environ)
    print("Got sign in from: {}".format(client_serial))
    if client_serial not in signedClients:
        signedClients.append(client_serial)
    print("Signed clients: {}".format(signedClients))
    if len(signedClients) == NUMBER_OF_CLIENTS:
        generateG()
    return jsonify({"id": signedClients.index(client_serial)})


@app.route("/get-group")
def get_group():
    global g, modulo, signedClients
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    print("sending group")
    if g is None or modulo is None:
        return Response(status=503)
    return jsonify({"g": str(g), "modulo": str(modulo)})


@app.route("/accept-group")
def accept_group():
    global signedClients, clientsThatAcceptedGroup
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    print("Group accepted by: {}".format(client_serial))
    if client_serial not in clientsThatAcceptedGroup:
        clientsThatAcceptedGroup.push(client_serial)
    print("Accepted clients: {}".format(signedClients))
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
    serving.run_simple("steelforge.pl", 443, app, ssl_context=context, request_handler=PeerCertWSGIRequestHandler)
    # serving.run_simple("127.0.0.1", 8000, app, ssl_context=context, request_handler=PeerCertWSGIRequestHandler)
