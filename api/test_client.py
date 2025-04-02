import requests
from PIL import Image
from io import BytesIO
import hashlib

def calculate_hash(ip: str, private_key:str) -> str:
    print(ip)
    return hashlib.sha256((ip+private_key).encode()).hexdigest()

# Hardkodirana IP adresa za testiranje (ili koristi stvarnu ako znaš svoju lokalnu IP)
client_ip = "127.0.0.1"  # ili zamijeni sa stvarnom IP adresom ako testiraš s drugog uređaja
private_key = "1234"
hashed = calculate_hash(client_ip, private_key)

url = "http://127.0.0.1:8069"
payload = {
    "auth": hashed
}

def real_image_test(image_name):
    request_url = url+"/get-real-image"
    payload["file"] = image_name

    response = requests.post(request_url, json=payload)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.show()
    else:
        print("Greška:", response.json())

def pattern_image_test(image_name):
    request_url = url+"/get-pattern-image"
    payload["file"] = image_name

    response = requests.post(request_url, json=payload)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.show()
    else:
        print("Greška:", response.json())

def random_image_name():
    request_url = url + "/get-random-image-name"

    response = requests.post(request_url, json=payload)

    if response.status_code == 200:
        print(response.json().get("data"))
    else:
        print("Greška:", response.json())

def all_image_names():
    request_url = url + "/get-all-image-names"

    response = requests.post(request_url, json=payload)

    if response.status_code == 200:
        print(response.json().get("data"))
    else:
        print("Greška:", response.json())

#real_image_test("smjesko2")
#pattern_image_test("smjesko2")
#random_image_name()
all_image_names()