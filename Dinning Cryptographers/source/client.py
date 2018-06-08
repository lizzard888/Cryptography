import requests
import sys
import random
import time
import urllib3
import warnings

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
    g = r.json()['g']
    p = r.json()['modulo']
    while True:
        r = requests.post('https://steelforge.pl/accept-group', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem')
        if r.status_code == 200:
            break
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
    print("Group acceptance sent.")
    x = random.randint(1, g-1)
    r = random.randint(1, g-1)
    xr = (x+r) % (p-1)
    print("Sending calculated keys.")
    while True:
        r = requests.post('https://steelforge.pl/send-key', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem', json = {'key': str(pow(g, x, p)), 'gr': str(pow(g, r, p)), 'xr': str(xr)})
        if r.status_code == 200:
            break
        elif r.status_code == 503:
            print("Waiting for other parties...")
        elif r.status_code == 504:
                print("Invalid key. Resending...")
                x = random.randint(1, g-1)
                r = random.randint(1, g-1)
                xr = (x+r) % (p-1)
        else:
            print("Internal server error. Connection reattempt...")
        time.sleep(1)
while True:
    r = requests.post('https://steelforge.pl/get-keys', cert=('certs/' + cert_name + '.crt', 'certs/' + cert_name + '.key'), verify='certs/ca/rootCA.pem', json = {'key': str(pow(g, x, p)), 'gr': str(pow(g, r, p)), 'xr': str(xr)})
    if r.status_code == 200:
        break
    elif r.status_code == 503:
        print("Waiting for other parties...")
    else:
        print("Internal server error. Connection reattempt...")
    time.sleep(1)
#TODO Obliczenia na otrzymanych kluczach
