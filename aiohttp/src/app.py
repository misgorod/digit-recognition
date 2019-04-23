import os
from aiohttp import web, MultipartWriter, WSMsgType
from time import time
import subprocess

import aiofiles

router = web.RouteTableDef()
sockets = dict()

class Session:
    def __init__(self, input_socket=None, output_socket=None):
        self.__output_sockets = list()
        self.input_socket = input_socket
        if output_socket:
            self.output_sockets.append(output_socket)

    @property
    def input_socket(self):
        return self.__input_socket

    @input_socket.setter
    def input_socket(self, value):
        self.__input_socket = value

    @property
    def output_sockets(self):
        return self.__output_sockets

@router.get("/")
async def hello(request):
    return web.Response(text="hello")

# Saves image
# @router.post("/save/{id}")
# async def send(request):
#     reader = await request.multipart()
#     image = await reader.next()
#     filename = create_name()
#     async with open(os.path.join('static/files', filename), 'wb+') as f:
#         while True:
#             chunk = await image.read_chunk()
#             if not chunk:
#                 break
#             await f.write(chunk)
#     return web.Response(text="OK")

# def create_name():
#     return str(round(time() * 1000))

# Video streaming through websocket mpeg
@router.get("/ws/mpeg/{id}")
async def ws_connection(request):
    id = request.match_info['id']
    ws = web.WebSocketResponse(protocols=["null"])
    await ws.prepare(request)
    if id in sockets:
        sockets[id].output_socket = ws
    else:
        sockets[id] = Session(output_socket=ws)
    async for msg in ws:
        if msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
    sockets[id].output_socket = None
    return ws

@router.post("/mpeg/{id}")
async def send_mpeg(request):
    id = request.match_info['id']
    if id not in sockets or not sockets[id].output_sockets:
        return web.Response(status=409, text="Client not connected")
    while True:
        cmd = ['ffmpeg', '-i', '/app/src/files/IMG_%d.jpg', f'/app/src/files/{id}_output.ts']
        code = subprocess.call(cmd)
        if not code == 0:
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd)))  
        for sock in sockets[id].output_sockets:
            sock.send_bytes()

# Video streaming through motion jpeg
@router.get("/mjpeg/{id}")
async def get_mjpeg(request):
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'multipart/x-mixed-replace;boundary=--bound'
        }
    )
    await response.prepare(request)
    files = gen_files("files")
    while True:
        async with aiofiles.open(f"files/{next(files)}", "rb+") as f:
            frame = await f.read()
        with MultipartWriter('image/jpeg', boundary='bound') as mpwriter:
            mpwriter.append(frame, {
                'Content-Type': 'image/jpeg'
            })
            await mpwriter.write(response, close_boundary=False)
        await response.drain()


def gen_files(directory):
    while True:
        for fl in os.listdir(directory):
            yield fl

def create_app():
    app = web.Application()
    app.add_routes(router)
    return app

if __name__ == "main":
    app = create_app()
    web.run_app(app)