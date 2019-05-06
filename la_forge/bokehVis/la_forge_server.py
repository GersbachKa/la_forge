#imports
import numpy as np

#bokeh imports
from bokeh.io import curdoc
from bokeh.layouts import column, row, widgetbox, layout, Spacer
from bokeh.models import ColumnDataSource, LinearColorMapper
import bokeh.models.widgets as widgets
from bokeh.plotting import figure

currentCore = None
histbins = 50

def setCore(coreIn):
    global currentCore
    currentCore = coreIn

def set_hist_bins(inp):
    global histbins
    histbins = inp

def make_server(doc):
    #Getting prarmeters and pulsars for dropdowns-------------------------------
    allParams = currentCore.params
    psr_names = [p.split('_')[0] for p in allParams if p[5] in ['+','-']]
    psr_names = np.unique(psr_names)
    psr_names.sort()
    #bokeh widgets--------------------------------------------------------------
    menuDropdown = widgets.Select(title='What to view:',value='All line plots',
                                  options=['All line plots','All histograms',
                                           'Single parameter','Single Pulsar'])

    parameterSelector = widgets.Select(title='Which Parameter:',
                                       value=allParams[0],options=allParams)

    pulsarSelector = widgets.Select(title='Which Pulsar:',value=psr_names[0],
                                    options=psr_names.tolist())

    plotsPerLine = widgets.Slider(title='Plots per line',start=1,end=8,value=5)

    goButton = widgets.Button(label='Go!',button_type='success')

    layoutList = [[menuDropdown,plotsPerLine],
                  [Spacer(),goButton]]

    l = layout(layoutList,sizing_mode='scale_width')
    #Update functions-----------------------------------------------------------
    def update_menu(attr, old, new):
        toChange = l.children[1]
        if new == 'All line plots' or new == 'All histograms':
            if type(toChange.children[0])!=type(Spacer()):
                toChange.children[0] = Spacer()
        elif new == 'Single parameter':
            if toChange.children[0] != parameterSelector:
                toChange.children[0] = parameterSelector
        elif new == 'Single Pulsar':
            if toChange.children[0] != pulsarSelector:
                toChange.children[0] = pulsarSelector
        else:
            return
    menuDropdown.on_change('value',update_menu)

    def goClicked():
        if menuDropdown.value == 'All line plots':
            showAllLinePlots()
        elif menuDropdown.value == 'All histograms':
            showAllHistPlots()
        elif menuDropdown.value == 'Single parameter':
            showSingleParam()
        elif menuDropdown.value == 'Single Pulsar':
            showSinglePulsar()
        else:
            return
    goButton.on_click(goClicked)

    #Show Functions-------------------------------------------------------------
    def showAllLinePlots():
        #If showing something else, remove them
        if len(l.children) > 2:
            del l.children[2:]

        ppl = plotsPerLine.value
        templist = []
        for param in currentCore.params:
            templist.append(genLinePlot(param,showAll=False))
            if len(templist)==ppl:
                l.children.append(row(templist,sizing_mode='scale_width'))
                templist = []
        if len(templist) != 0:
            l.children.append(row(templist,sizing_mode='scale_width'))


    def showAllHistPlots():
        #If showing something else, remove them
        if len(l.children) > 2:
            del l.children[2:]

        ppl = plotsPerLine.value
        templist = []
        for param in currentCore.params:
            templist.append(genHistPlot(param))
            if len(templist)==ppl:
                l.children.append(row(templist,sizing_mode='scale_width'))
                templist = []
        if len(templist) != 0:
            l.children.append(row(templist,sizing_mode='scale_width'))

    def showSingleParam():
        param = parameterSelector.value
        templist = [genLinePlot(param,showAll=True),genHistPlot(param)]
        if len(l.children) > 2:
            del l.children[2:]

        l.children.append(row(templist,sizing_mode='scale_width'))


    def showSinglePulsar():
        pass

    #Collumns used available for updates----------------------------------------
    allColumns = {}
    #Generation functions-------------------------------------------------------
    def genLinePlot(parameter,showAll=False):
        chain_array = currentCore.get_param(parameter,to_burn=True)
        #If arrays are big, show every 10th
        line_src = None
        if len(chain_array) > 10000 or not showAll:
            xvals = np.linspace(0,chain_array.shape[0],int(chain_array.shape[0]/50)+1)
            line_src = ColumnDataSource(data=dict(x=xvals,y=chain_array[::50]))
        #if arrays are small, show all
        else:
            xvals = np.linspace(0,chain_array.shape[0],chain_array.shape[0])
            line_src = ColumnDataSource(data=dict(x=xvals,y=chain_array))

        allColumns.update({parameter+'_line':line_src})

        linefig = figure(title=parameter+" line plot",
                         x_axis_label = 'Iterations',
                         y_axis_label = 'Value',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        linefig.line(source = line_src, x='x', y='y')

        return linefig

    def genHistPlot(parameter):
        chain_array = currentCore.get_param(parameter,to_burn=True)
        hist = np.histogram(chain_array,histbins)
        hist_src = ColumnDataSource(data=dict(x=hist[1][:-1],y=hist[0]))

        allColumns.update({parameter+'_hist':hist_src})

        histfig = figure(title=parameter+" histogram",
                         x_axis_label = 'Value',
                         y_axis_label = 'Number of iterations',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        histfig.line(source = hist_src, x='x', y='y')

        return histfig

    def gen2dHist(pulsar):
        pass




    doc.title = "La Forge Server"
    doc.add_root(l)
