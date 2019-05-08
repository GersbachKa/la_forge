#Used for calling server from notebook
from bokeh.server.server import Server

from . import la_forge_server as lfs

def start_server(core,port):
    lfs.setCore(core)
    server = Server({'/': lfs.make_server},port=port)
    server.start()
    print('Started server. Open a browser to http://localhost:{} to view.'.format(port))
    print('Posterior histogram bins are 50 by default, to change this, use .set_bokeh_histogram_bins()')

def set_histogram_bins(bins):
    lfs.set_hist_bins(bins)
