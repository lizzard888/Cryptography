from flask import Flask, request, jsonify, Response
from werkzeug import serving
import ssl
import OpenSSL
from random import randint, seed

app = Flask(__name__)

NUMBER_OF_CLIENTS = 3

G_LENGTH = 30

signedClients = []

modulo = None
g = None

clientsThatAcceptedGroup = []
keys = []
secondKeys = []

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


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    global signedClients
    client_serial = get_client_serial_number(request.environ)
    print("Got sign in from: {}".format(client_serial))
    if client_serial not in signedClients:
        signedClients.append(client_serial)
    print("Signed clients: {}".format(signedClients))
    if len(signedClients) == NUMBER_OF_CLIENTS:
        generateG()
    return jsonify({"id": signedClients.index(client_serial), "no_of_clients": NUMBER_OF_CLIENTS})


@app.route("/get-group",  methods=["GET", "POST"])
def get_group():
    global g, modulo, signedClients
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    print("sending group")
    if g is None or modulo is None:
        return Response(status=503)
    return jsonify({"g": str(g), "modulo": str(modulo)})


@app.route("/accept-group",  methods=["GET", "POST"])
def accept_group():
    global signedClients, clientsThatAcceptedGroup
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    print("Group accepted by: {}".format(client_serial))
    if client_serial not in clientsThatAcceptedGroup:
        clientsThatAcceptedGroup.append(client_serial)
    print("Accepted clients: {}".format(clientsThatAcceptedGroup))
    return "Accepted"
#
#
# @app.route("/deny-group",  methods=["GET", "POST"])
# def deny_group():
#     print("Group denied!")
#     return "Denied"


@app.route("/send-key",  methods=["POST"])
def send_key():
    global signedClients, clientsThatAcceptedGroup, keys, modulo, g
    if not keys:
        keys = [None for _ in range(0, NUMBER_OF_CLIENTS)]
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    if len(clientsThatAcceptedGroup) < NUMBER_OF_CLIENTS:
        return Response(status=503)
    client_id = signedClients.index(client_serial)
    if keys[client_id] is None:
        json = request.get_json()
        l_trail = (int(json['gr']) * int(json['key'])) % modulo
        r_trail = pow(g, int(json['xr']), modulo)
        if l_trail == r_trail:
            keys[client_id] = int(json['key'])
        else:
            return Response(status=504)
    print("Got key: {} for: {}".format(keys[client_id], client_serial))
    return "Got key"


@app.route("/get-keys",  methods=["GET", "POST"])
def get_keys():
    global signedClients, clientsThatAcceptedGroup, keys
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    if len(keys) < NUMBER_OF_CLIENTS:
        return Response(status=503)
    for key in keys:
        if key is None:
            return Response(status=503)
    print("Sending all keys to: {}".format(client_serial))
    return jsonify({"keys": keys})


@app.route("/send-second-key",  methods=["POST"])
def send_second_key():
    global signedClients, clientsThatAcceptedGroup, keys, secondKeys
    if not secondKeys:
        secondKeys = [None for _ in range(0, NUMBER_OF_CLIENTS)]
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    if len(keys) < NUMBER_OF_CLIENTS:
        return Response(status=503)
    for key in keys:
        if key is None:
            return Response(status=503)

    client_id = signedClients.index(client_serial)
    if len(secondKeys) <= client_id or secondKeys[client_id] is None:
        json = request.get_json()
        l_trail = (int(json['gr']) * int(json['key'])) % modulo
        r_trail = int(g ** int(json['xr'])) % modulo
        if l_trail == r_trail:
            secondKeys[client_id] = int(json['second_key'])
        else:
            return Response(status=504)
    print("Got second key: {} for: {}".format(secondKeys[client_id], client_serial))
    return "Got key"


@app.route("/get-second-keys",  methods=["GET", "POST"])
def get_second_keys():
    global signedClients, clientsThatAcceptedGroup, secondKeys
    client_serial = get_client_serial_number(request.environ)
    if client_serial not in signedClients:
        return Response(status=403)
    if len(secondKeys) < NUMBER_OF_CLIENTS:
        return Response(status=503)
    for key in secondKeys:
        if key is None:
            return Response(status=503)
    print("Sending all second keys to: {}".format(client_serial))
    return jsonify({"second_keys": secondKeys})


@app.route("/clear")
def clear():
    global signedClients, clientsThatAcceptedGroup, secondKeys, keys, g, modulo
    signedClients = []
    clientsThatAcceptedGroup = []
    keys = []
    secondKeys = []
    g = None
    modulo = None
    return "Cleared"


if __name__ == "__main__":
    seed()
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("certs/ca/rootCA.crt")
    context.load_cert_chain("certs/server.crt", "certs/server.key")
    serving.run_simple("steelforge.pl", 443, app, ssl_context=context, request_handler=PeerCertWSGIRequestHandler)
    # serving.run_simple("127.0.0.1", 8000, app, ssl_context=context, request_handler=PeerCertWSGIRequestHandler)
