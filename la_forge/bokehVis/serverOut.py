#Find out how to redirect new connections into old document


#imports
import numpy as np

#bokeh imports
from bokeh.io import curdoc
from bokeh.layouts import column, row, widgetbox, layout, Spacer
from bokeh.models import ColumnDataSource, LinearColorMapper
import bokeh.models.widgets as widgets
from bokeh.plotting import figure

#Used for calling server from notebook
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler



#For retrieving the core values
currentCore = None
histogram_bins = 50

#The array
#dataArrays = {}
columnDict = {}
plotDict = {}

l = layout([],sizing_mode='scale_width')

#Bokeh Widgets------------------------------------------------------------------
menuDropdown = None
parameterSelector = None
pulsarSelector = None
plotsPerLine = None
goButton = None



#TODO: Add ability to remove burned values
def _create_columns():
    global columnDict

    print("Creating visualization with {} parameters..".format(len(currentCore.params)))

    for param in currentCore.params:
        chain_array = currentCore.get_param(param,to_burn=False)

        line_src = ColumnDataSource(data=dict(x=np.linspace(0,chain_array.shape[0],chain_array.shape[0]),
                                              y=chain_array))

        hist = np.histogram(chain_array,histogram_bins)
        hist_src = ColumnDataSource(data=dict(x=hist[1][:-1],y=hist[0]))

        columnDict.update({param:[line_src,hist_src]})

    print("Retrieved Data.")


def _create_plots():
    if currentCore is None:
        print("Server has not been set up")
        return

    global plotDict
    print('Creating interactive plots...')
    for param in currentCore.params:

        linefig = figure(title=param+" line plot",
                         x_axis_label = 'Iterations',
                         y_axis_label = 'Value',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        linefig.line(source = columnDict.get(param)[0], x='x', y='y')

        histfig = figure(title=param+" Histogram",
                         x_axis_label = 'Iterations',
                         y_axis_label = 'Number of iterations',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        histfig.line(source = columnDict.get(param)[1], x='x', y='y')

        plotDict.update({param:[linefig,histfig]})
    print('Plots Generated.')


def _setup_server(core):
    global currentCore
    currentCore = core
    _create_columns()
    _create_plots()


#Stuff to start server from python
def _make_document(doc):
    global menuDropdown
    global menuDropdown
    global parameterSelector
    global pulsarSelector
    global plotsPerLine
    global goButton

    global l

    menuDropdown = widgets.Select(title='What to view:',value='All line plots',
                                  options=['All line plots','All histograms',
                                           'Single parameter','Single Pulsar'])

    menuDropdown.on_change('value', selectMode)

    allParams = currentCore.params
    psr_names = [p.split('_')[0] for p in allParams if p[5] in ['+','-']]
    psr_names = np.unique(psr_names)
    psr_names.sort()

    parameterSelector = widgets.Select(title='Which Parameter:',
                                       value=allParams[0],options=allParams)

    pulsarSelector = widgets.Select(title='Which Pulsar:',value=psr_names[0],
                                    options=psr_names.tolist())

    plotsPerLine = widgets.Slider(title='Plots per line',start=1,end=8,value=5)

    goButton = widgets.Button(label='Go!',button_type='success')

    layoutList = [[menuDropdown,Spacer(),plotsPerLine,goButton],
                  [Spacer()]]

    l = layout(layoutList,sizing_mode='scale_width')
    doc.title = 'La Forge Core Output'
    doc.add_root(l)


def selectMode(attrname, old, new):
    global l
    toChange = l.children[0].children[2]
    if menuDropdown.value == 'All line plots':
        if type(toChange) != type(Spacer()):
            toChange = Spacer()
    elif menuDropdown.value == 'All histograms':
        if type(toChange) != type(Spacer()):
            toChange = Spacer()
    elif menuDropdown.value == 'Single parameter':
        if toChange != parameterSelector:
            toChange = parameterSelector
    elif menuDropdown.value == 'Single Pulsar':
        if toChange != pulsarSelector:
            toChange = pulsarSelector

def _launch():
    print('Launching server. Go to \"local host:5000\" to see visualization')
    apps = {'/': Application(FunctionHandler(_make_document))}
    server = Server(apps, port=5000)
    server.start()


def EZ_Start(core):
    _setup_server(core)
    _launch()
