from aiohttp import web, WSMsgType

routes = web.RouteTableDef()
sockets = list()
cache = dict()

@routes.get('/')
async def index(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sockets.append(ws)

    for wsclient in sockets:
        await wsclient.ping()
        await wsclient.send_json(cache)
        await wsclient.send_json({'test': len(sockets)})

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                pass
        elif msg.type == WSMsgType.error:
            print(ws.exception())
            await ws.close()

    print('closed')
    sockets.remove(ws)
    return ws

@routes.get('/push')
async def push(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                key, value = msg.data.split(': ', 1)
                cache[key] = value
                for wsclient in sockets:
                    await wsclient.send_json(cache)
        elif msg.tp == WSMsgType.error:
            print(ws.exception())

    return ws


app = web.Application()
app.add_routes(routes)
web.run_app(app)
