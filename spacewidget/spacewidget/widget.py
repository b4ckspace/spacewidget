from pathlib import Path
import os

from aiohttp import web, WSMsgType
from aiohttp import web_exceptions as aio_exc


WS_TOKEN = os.environ.get("WS_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC9")
METRICS_TOKEN = os.environ.get("METRICS_TOKEN", "8FTrU92m9HE47lmkBGt3I0CJGtGDE")
MEMBER_TOPIC = os.environ.get("MEMBER_TOPIC", "members")
LISTEN = os.environ.get("LISTEN", "localhost:8080")
with open(str(Path(Path(__file__).parent, "index.html"))) as f:
    INDEX = f.read()


routes = web.RouteTableDef()
sockets = list()
cache = dict()


@routes.get("/")
async def index(request):
    """Display the widget."""
    text = INDEX
    text = text.replace("{{ topic }}", MEMBER_TOPIC)
    text = text.replace("{{ host }}", request.headers.get("Host"))
    return web.Response(text=text, content_type="text/html")


@routes.get("/status")
async def status(request):
    """Websocket for the widget."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    sockets.append(ws)

    await ws.send_json(cache)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                pass
        elif msg.type == WSMsgType.error:
            await ws.close()

    sockets.remove(ws)
    return ws


@routes.get("/push")
async def push(request):
    """Websocket for pushing updates."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    auth_msg = await ws.receive()
    if not auth_msg.type == WSMsgType.TEXT:
        raise aio_exc.HTTPForbidden
    if not auth_msg.data == "Authorization: Token %s" % WS_TOKEN:
        raise aio_exc.HTTPForbidden

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == "close":
                await ws.close()
            else:
                key, value = msg.data.split(": ", 1)
                cache[key] = value
                for wsclient in sockets:
                    await wsclient.send_json(cache)
        elif msg.type == WSMsgType.error:
            print(ws.exception())

    return ws


@routes.get("/metrics")
async def metrics(request):
    """Provides prometheus metrics."""
    if not request.headers.get("Authorization", "") == "Token %s" % METRICS_TOKEN:
        raise aio_exc.HTTPForbidden
    _metrics = "spacewidget_conections: %s" % len(sockets)
    return web.Response(text=_metrics)


def init(argv):
    """Entrypoint."""
    app = web.Application()
    app.add_routes(routes)
    return app


def main():
    app = init([])
    args = {}
    if LISTEN.startswith("unix://"):
        args["path"] = LISTEN[7:]
        print(args)
    elif ":" in LISTEN:
        args["host"], args["port"] = LISTEN.split(":", 1)
    web.run_app(app, **args)


if __name__ == "__main__":
    main()
