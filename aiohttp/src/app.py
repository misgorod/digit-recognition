import os
import aiohttp
from aiohttp import web, MultipartWriter, WSMsgType
from time import time
import datetime
from PIL import Image, ImageFilter, ImageEnhance
import PIL.ImageOps    
import io
import numpy as np
import subprocess
import keras
from keras.models import load_model                                                                                                                                                                         

import aiofiles

router = web.RouteTableDef()
modelrec = load_model('model/dig.h5')

@router.post("/api/image/{id}")
async def get_jpeg(request):
    time = datetime.datetime.now()
    print("Start get_jpeg")
    id = request.match_info['id']
    post = await request.post()
    file_field = post['data']
    print("Before file read: {}".format(datetime.datetime.now() - time))
    image_bytes = file_field.file.read()
    print("Before image open: {}".format(datetime.datetime.now() - time))
    image_pil = Image.open(io.BytesIO(image_bytes)).convert('L')
    print("Before image resuze: {}".format(datetime.datetime.now() - time))
    images = image_pil.resize((28, 28), Image.ANTIALIAS)
    images = preproc(images)
    images.save('files/{}'.format(datetime.datetime.now()), 'JPEG')
    images = np.array(images)
    images = images / 255
    print("Before array reshape: {}".format(datetime.datetime.now() - time))
    images = np.reshape(images,(1, 28, 28, 1))
    print("Before prediciton: {}".format(datetime.datetime.now() - time))
    image_pos = modelrec.predict(images)
    s = np.argmax(image_pos)

    return web.Response(text=str(s))

def preproc(image):
    
    
    

    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(2)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(12)
    
    
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