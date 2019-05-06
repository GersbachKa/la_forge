#Used for calling server from notebook
from bokeh.server.server import Server

from . import la_forge_server as lfs

def start_server(core,port):
    lfs.setCore(core)
    server = Server({'/': lfs.make_server},port=port)
    server.start()
