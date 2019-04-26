import os
import aiohttp
from aiohttp import web, MultipartWriter, WSMsgType
from time import time
from PIL import Image, ImageFilter
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

# Video streaming through websocket mpeg
@router.get("/ws/mpeg/{id}")
async def ws_connection(request):
    id = request.match_info['id']
    ws = web.WebSocketResponse(protocols=["null"])
    await ws.prepare(request)
    if id in sockets:
        sockets[id].output_sockets.append(ws)
    else:
        await ws.send_str("created")
        sockets[id] = Session(output_socket=ws)
    async for msg in ws:
        if msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
    sockets[id].output_sockets.remove(ws)
    return ws

# Video streaming through motion jpeg
# @router.get("/mjpeg/{id}")
# async def get_mjpeg(request):
#     id = request.match_info['id']
#     response = web.StreamResponse(
#         status=200,
#         reason='OK',
#         headers={
#             'Content-Type': 'multipart/x-mixed-replace;boundary=--bound'
#         }
#     )
#     await response.prepare(request)
#     files = gen_files("files")

#     #
#     model = load_model('model/digs.h5')
#     #
#     while True:
#         async with aiofiles.open(f"files/{next(files)}", "rb+") as f:
#             frame = await f.read()
#             nframe = Image.open(io.BytesIO(frame)).convert('LA')
#             nframe = nframe.resize((28,28))
#             nframe, dump = nframe.split()
#             nframe = np.array(nframe)
#             nframe = np.reshape(nframe,(1,784))
#             s = np.argmax(model.predict(nframe)) 
#             if id in sockets and sockets[id].output_sockets:
#                 for sock in sockets[id].output_sockets:
#                     await sock.send_str(str(s))
#         with MultipartWriter('image/jpeg', boundary='bound') as mpwriter:
#             mpwriter.append(frame, {
#                 'Content-Type': 'image/jpeg'
#             })
#             await mpwriter.write(response, close_boundary=False)
#         await response.drain()

@router.post("/image/{id}")
async def get_jpeg(request):
    id = request.match_info['id']
    post = await request.post()
    file_field = post['data']
    modelfin = load_model('model/zone.h5')
    modelrec = load_model('model/digs.h5')

    image_bytes = file_field.file.read()
    image_pil = Image.open(io.BytesIO(image_bytes)).convert('L')
    image = image_pil.filter(ImageFilter.FIND_EDGES)
    image.save("static/image2.png")
    inverted_image = PIL.ImageOps.invert(image)
    inverted_image.save("static/image1.png")
    images = inverted_image.resize((8, 8))
    images.save("static/image.png")

    
    images = np.array(images) 
    images = np.reshape(images,(1,64)) 
    image_pos = modelfin.predict(images)
    print(image_pos)
    
    width, height = inverted_image.size
    left, upper, right, lower = np.floor(image_pos[0]/8) * width, np.floor(image_pos[1]/8 + image_pos[3]/8)* height , np.floor(image_pos[0]/8 + image_pos[2]/8) * width, np.floor(image_pos[1]/8 )* height
    inverted_image = inverted_image.crop(left, upper, right, lower)
    inverted_image.save("static/find.png")
    
    s=5
    if id in sockets and sockets[id].output_sockets:
        for sock in sockets[id].output_sockets:
            await sock.send_str(f"new: {s}")
    async with aiofiles.open('static/filename.jpeg', 'wb+') as f:
        await f.write(image_bytes)
    return web.Response(text="OK")

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