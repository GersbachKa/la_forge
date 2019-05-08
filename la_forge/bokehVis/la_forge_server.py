#imports
import numpy as np

#bokeh imports
from bokeh.io import curdoc
from bokeh.layouts import column, row, widgetbox, layout, Spacer, gridplot
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
    menuDropdown = widgets.Select(title='What to view:',value='All chains',
                                  options=['All chains','All posteriors',
                                           'Single parameter','Single pulsar',
                                           'Select parameters'])

    parameterSelector = widgets.Select(title='Which Parameter:',
                                       value=allParams[0],options=allParams)

    pulsarSelector = widgets.Select(title='Which Pulsar:',value=psr_names[0],
                                    options=psr_names.tolist())

    plotsPerLine = widgets.Slider(title='Plots per line',start=1,end=8,value=5)

    goButton = widgets.Button(label='Go!',button_type='success')

    parameterMultiSelect = widgets.CheckboxGroup(name="Parameters:",
                                                 labels=allParams)

    layoutList = [[menuDropdown,plotsPerLine,goButton],
                  [Spacer()]]

    l = layout(layoutList,sizing_mode='scale_width')
    #Update functions-----------------------------------------------------------
    def update_menu(attr, old, new):
        toChange = l.children[1]
        if new == 'All chains' or new == 'All posteriors':
            if type(toChange.children[0])!=type(Spacer(height=50)):
                l.children[1] = row(Spacer(height=50),sizing_mode='scale_width')
        elif new == 'Single parameter':
            if toChange.children[0] != parameterSelector:
                l.children[1] = row(parameterSelector,sizing_mode='scale_width')
        elif new == 'Single pulsar':
            if toChange.children[0] != pulsarSelector:
                l.children[1] = row(pulsarSelector,sizing_mode='scale_width')
        elif new == 'Select parameters':
            if toChange.children[0] != parameterMultiSelect:
                l.children[1] = row(parameterMultiSelect,sizing_mode='scale_width')

        else:
            return
    menuDropdown.on_change('value',update_menu)

    def goClicked():
        if menuDropdown.value == 'All chains':
            showAllLinePlots()
        elif menuDropdown.value == 'All posteriors':
            showAllHistPlots()
        elif menuDropdown.value == 'Single parameter':
            showSingleParam()
        elif menuDropdown.value == 'Single pulsar':
            showSinglePulsar()
        elif menuDropdown.value == 'Select parameters':
            showOnlyParameters()
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
        templist = [genLinePlot(param),genHistPlot(param)]
        if len(l.children) > 2:
            del l.children[2:]

        l.children.append(row(templist,sizing_mode='scale_width'))


    def showSinglePulsar():
        if len(l.children) > 2:
            del l.children[2:]
        pulsar = pulsarSelector.value

        hex = gen2dHist(pulsar+'_gamma',pulsar+'_log10_A')
        gammaLine = genLinePlot(pulsar+'_gamma')
        gammaHist = genHistPlot(pulsar+'_gamma',square=True)
        logALine = genLinePlot(pulsar+'_log10_A')
        logAHist = genHistPlot(pulsar+'_log10_A',square=True)

        l.children.append(row([gammaHist,column([gammaLine,logALine],sizing_mode='scale_width')],sizing_mode='scale_width'))
        l.children.append(row([hex,logAHist],sizing_mode='scale_width'))


    def showOnlyParameters():
        #Remove the list from view
        l.children[1] = row(Spacer(height=50),sizing_mode='scale_width')

        if len(l.children) > 2:
            del l.children[2:]

        paramIndex = parameterMultiSelect.active
        lineList = []
        histList = []
        for i in paramIndex:
            param = allParams[i]
            lineList.append(genLinePlot(param))
            histList.append(genHistPlot(param))

        ppl = plotsPerLine.value
        templist = []
        for plot in lineList:
            templist.append(plot)
            if len(templist)==ppl:
                l.children.append(row(templist,sizing_mode='scale_width'))
                templist = []
        if len(templist) != 0:
            l.children.append(row(templist,sizing_mode='scale_width'))
            templist = []

        for plot in histList:
            templist.append(plot)
            if len(templist)==ppl:
                l.children.append(row(templist,sizing_mode='scale_width'))
                templist = []
        if len(templist) != 0:
            l.children.append(row(templist,sizing_mode='scale_width'))








    #Collumns used available for updates----------------------------------------
    allColumns = {}
    #Generation functions-------------------------------------------------------
    def genLinePlot(parameter,showAll=False):
        chain_array = currentCore.get_param(parameter,to_burn=False)
        #If arrays are big, show every 10th
        line_src = None
        if len(chain_array) > 10000 or not showAll:
            xvals = np.linspace(0,chain_array.shape[0],int(chain_array.shape[0]/10))
            line_src = ColumnDataSource(data=dict(x=xvals,y=chain_array[::10]))
        #if arrays are small, show all
        else:
            xvals = np.linspace(0,chain_array.shape[0],chain_array.shape[0])
            line_src = ColumnDataSource(data=dict(x=xvals,y=chain_array))

        allColumns.update({parameter+'_line':line_src})

        linefig = figure(title=parameter+" chain",
                         x_axis_label = 'Iterations',
                         y_axis_label = 'Value',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        linefig.line(source = line_src, x='x', y='y')

        return linefig

    def genHistPlot(parameter,square=False):
        chain_array = currentCore.get_param(parameter,to_burn=True)
        hist = np.histogram(chain_array,histbins)
        hist_src = ColumnDataSource(data=dict(x=hist[1][:-1],y=hist[0]))

        allColumns.update({parameter+'_hist':hist_src})

        histfig = figure(title=parameter+" posterior",
                         x_axis_label = 'Value',
                         y_axis_label = 'Number of iterations',
                         plot_height = 300, plot_width = 900,
                         tools = "pan,reset,box_zoom")
        if square:
            histfig.plot_height=900

        histfig.line(source = hist_src, x='x', y='y')

        return histfig

    def gen2dHist(xparam,yparam):
        x1 = currentCore.get_param(xparam,to_burn=True)
        y1 = currentCore.get_param(yparam,to_burn=True)

        hexbin = figure(title=xparam+' V '+yparam+" 2d posterior",
                         x_axis_label = xparam,
                         y_axis_label = yparam,
                         match_aspect=True,
                         plot_height = 400, plot_width = 400,
                         tools="pan,reset,box_zoom")
        hexbin.background_fill_color = '#440154'
        hexbin.grid.visible = False
        hexbin.hexbin(x=x1,y=y1,size=.06)

        return hexbin




    doc.title = "La Forge Server"
    doc.add_root(l)
