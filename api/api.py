from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import hashlib
import uvicorn
import re
import os
from random import randint

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_valid_files()
    print("Api started")
    print(VALID_FILES)
    yield

app = FastAPI(lifespan=lifespan)

PRIVATE_KEY = "1234"
VALID_FILES = {}
ALLOWED_FILENAME_REGEX = re.compile(r'^[a-zA-Z0-9]+$')
PATTERN_IMAGES_FOLDER = "files/pattern_images"
REAL_IMAGES_FOLDER = "files/real_images"

def calculate_hash(ip: str, private_key:str) -> str:
    print(ip)
    return hashlib.sha256((ip+private_key).encode()).hexdigest()

def initialize_valid_files():
    folder = REAL_IMAGES_FOLDER
    for filename in os.listdir(REAL_IMAGES_FOLDER):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            key = os.path.splitext(filename)[0]
            VALID_FILES[key] = filename

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get-real-image")
async def get_real_image(request: Request):
    data = await request.json()
    client_ip = request.client.host
    received_hash = data.get("auth")
    file_key = data.get("file")

    # Validacija file imena
    if not file_key or not ALLOWED_FILENAME_REGEX.match(file_key):
        return JSONResponse(content={"error": "Invalid file name. Only letters and numbers allowed."}, status_code=400)

    # Provjera hasha
    expected_hash = calculate_hash(client_ip, PRIVATE_KEY)
    if received_hash != expected_hash:
        return JSONResponse(content={"error": "Auth incorrect"}, status_code=401)

    # Provjera postojanja fajla
    if file_key not in VALID_FILES:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    filename = os.path.join(REAL_IMAGES_FOLDER, VALID_FILES[file_key])
    return FileResponse(filename, media_type="image/jpeg")

@app.post("/get-pattern-image")
async def get_pattern_image(request: Request):
    data = await request.json()
    client_ip = request.client.host
    received_hash = data.get("auth")
    file_key = data.get("file")

    # Validacija file imena
    if not file_key or not ALLOWED_FILENAME_REGEX.match(file_key):
        return JSONResponse(content={"error": "Invalid file name. Only letters and numbers allowed."}, status_code=400)

    # Provjera hasha
    expected_hash = calculate_hash(client_ip, PRIVATE_KEY)
    if received_hash != expected_hash:
        return JSONResponse(content={"error": "Auth incorrect"}, status_code=401)

    # Provjera postojanja fajla
    if file_key not in VALID_FILES:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    filename = os.path.join(PATTERN_IMAGES_FOLDER, VALID_FILES[file_key])
    return FileResponse(filename, media_type="image/jpeg")

@app.post("/get-random-image-name")
async def get_random_image_name(request: Request):
    data = await request.json()
    client_ip = request.client.host
    received_hash = data.get("auth")

    # Provjera hasha
    expected_hash = calculate_hash(client_ip, PRIVATE_KEY)
    if received_hash != expected_hash:
        return JSONResponse(content={"error": "Auth incorrect"}, status_code=401)

    return {"data": list(VALID_FILES.keys())[randint(0,len(VALID_FILES)-1)]}

@app.post("/get-all-image-names")
async def get_all_image_names(request: Request):
    data = await request.json()
    client_ip = request.client.host
    received_hash = data.get("auth")

    # Provjera hasha
    expected_hash = calculate_hash(client_ip, PRIVATE_KEY)
    if received_hash != expected_hash:
        return JSONResponse(content={"error": "Auth incorrect"}, status_code=401)

    return {"data": list(VALID_FILES.keys())}

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8069, reload=True)