import os
import aiohttp
from aiohttp import web, MultipartWriter, WSMsgType
from time import time
from PIL import Image, ImageFilter, ImageEnhance
import PIL.ImageOps    
import io
import numpy as np
import subprocess
import keras
from keras.models import load_model                                                                                                                                                                         

import aiofiles

router = web.RouteTableDef()
sockets = dict()

class Session:
    def __init__(self, input_socket=None, output_socket=None):
        self.output_sockets = list()
        self.input_socket = input_socket
        if output_socket != None:
            self.output_sockets.append(output_socket)

@router.get("/")
async def hello(request):
    return web.Response(text="hello")

@router.post("/image/{id}")
async def get_jpeg(request):
    print("Start get_jpeg")
    id = request.match_info['id']
    post = await request.post()
    file_field = post['data']
   
    modelrec = load_model('model/digs.1.h5')

    image_bytes = file_field.file.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert('L')
    images = image_pil.resize((28, 28), Image.ANTIALIAS)
    images = np.array(images) 
    images = np.reshape(images,(28, 28, 1))

    image_pos = modelrec.predict(images)
    s = np.argmax(image_pos)

    # async with aiofiles.open('static/filename.jpeg', 'wb+') as f:
    #     await f.write(image_bytes)
    return web.Response(text=str(s))

def preproc(image):
    
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(0)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(0.5)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(5)
    
    

    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(2)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(22)
    
    image = image.filter(ImageFilter.CONTOUR)
    return image

def gen_files(directory):
    while True:
        for fl in os.listdir(directory):
            yield fl

ALLOWED_HEADERS = ','.join((
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-requested-with',
    'x-csrftoken',
    ))

def set_cors_headers (request, response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = request.method
    response.headers['Access-Control-Allow-Headers'] = ALLOWED_HEADERS
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

async def cors_factory (app, handler):
    async def cors_handler (request):
        if request.method == 'OPTIONS':
            return set_cors_headers(request, web.Response())
        else:
            response = await handler(request)
            return set_cors_headers(request, response)
    return cors_handler

def create_app():
    app = web.Application(middlewares=[cors_factory])
    app.add_routes(router)
    return app

if __name__ == "main":
    app = create_app()
    web.run_app(app)