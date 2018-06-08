import requests
import sys
import random
import time
import urllib3
import warnings
import gmpy

if __name__ == "__main__":
    random.seed()
    urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)
    warnings.simplefilter('ignore', urllib3.exceptions.SecurityWarning)
    if len(sys.argv) != 2:
        print("Invalid arguments!")
        sys.exit()
    cert_name = str(sys.argv[1])
    global r
    print("Establishing server connection...")
    while True:
        r = requests.post('https://steelforge.pl/sign-in', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Server connection established.")
    id = r.json()['id']
    clients = r.json()['no_of_clients']
    while True:
        r = requests.post('https://steelforge.pl/get-group', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Group data received.")
    g = int(r.json()['g'])
    p = int(r.json()['modulo'])
    while True:
        r = requests.post('https://steelforge.pl/accept-group', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Group acceptance sent.")
    x = random.randint(1, g-1)
    ran = random.randint(1, g-1)
    xr = (x+ran) % (p-1)
    print("Sending calculated keys.")
    while True:
        r = requests.post('https://steelforge.pl/send-key', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem', json = {'key': str(pow(g, x, p)), 'gr': str(pow(g, ran, p)), 'xr': str(xr)})
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        elif r.status_code == 504:
                print("Invalid key. Resending...")
                x = random.randint(1, g-1)
                ran = random.randint(1, g-1)
                xr = (x+ran) % (p-1)
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    while True:
        r = requests.post('https://steelforge.pl/get-keys', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Round 1 finished. Keys received")
    keys_num = [int(x) for x in r.json()['keys']]
    gi=1
    gj=1
    for v in range(0, id):
        gi *= keys_num[v] % p
    for v in range(id+1, clients):
        gj *= keys_num[v] % p
    gy = g1 * int(gmpy.invert(gj, p))
    decision = random.randint(1000)
    chance = int(1000/clients)
    c = 0
    if decision < chance:
        print("Sending veto!")
        c = x
    else:
        print("Not sending veto.")
        c = random.randint(1, g-1)
    ran = random.randint(1, g-1)
    print("Sending calculated keys.")
    while True:
        r = requests.post('https://steelforge.pl/send-second-key', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem', json = {'key': str(pow(gy, c, p)), 'gy': str(gy), 'gry': str(pow(gy, ran, p)), 'cr': str(c*ran)})
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        elif r.status_code == 504:
                print("Invalid key. Resending...")
                x = random.randint(1, g-1)
                ran = random.randint(1, g-1)
                xr = (x+ran) % (p-1)
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    while True:
        r = requests.post('https://steelforge.pl/get-second-keys', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Round 2 finished. Calculating result")
    result = 1
    for x in r.json()['keys']:
        result *= int(x)
    if result == 1:
        print("It was one of us.")
    else:
        print("It was NSA.")
