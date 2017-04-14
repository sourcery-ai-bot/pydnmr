"""
The main GUI application to be run from the command line.
"""

import sys
from collections import namedtuple

from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QDoubleSpinBox,
                             QToolBar, QRadioButton, QVBoxLayout, QButtonGroup,
                             QStackedWidget, QApplication, QMainWindow)
from PyQt5.QtCore import Qt
from pyqtgraph import PlotWidget, setConfigOption

from pydnmr.dnmrplot import dnmrplot_2spin, dnmrplot_AB


# Each type of calculation will have its own ordering of input widgets.
# Models that correspond to an equivalent in Reich's WINDNMR program use
# the same preset values as WINDNMR.

# Define the different types of input widgets that may be required.
# Currently all inputs are QDoubleSpinBox.
# Keys are for use with a dict that is sent to model as **kwargs.
# Keys are also used to setObjectName for widgets.
# Strings are for labels.
# Value is for the inital QDoubleSpinBox default.
# Range is the range of values for the QDoubleSpinBox.
# RANGE MUST BE SET BEFORE VALUE

# Widgets needed for two uncoupled spins view:
var = namedtuple('var', ['key', 'string', 'value', 'range'])
va = var(key='va', string=str('ν')+'<sub>A</sub>', value=165.00,
         range=(0.00, 10000.00))
vb = var(key='vb', string=str('ν')+'<sub>B</sub>', value=135.00,
         range=(0.00, 10000.00))
k = var(key='k', string='k<sub>A</sub>', value=1.50,
        range=(0.01, 1000.00))
wa = var(key='wa', string='W<sub>A</sub>', value=0.50,
         range=(0.01, 100.00))
wb = var(key='wb', string='W<sub>B</sub>', value=0.50,
         range=(0.01, 100.00))
percent_a = var(key='percent_a', string='% A', value=50.00,
                range=(0.00, 100.00))


twosinglets_vars = (va, vb, k, wa, wb, percent_a)

# Widgets for the two coupled spins (AB system) view:
j_ab = var(key='j_ab', string='J<sub>AB</sub>', value=12.00,
           range=(0.00, 100.00))
k_ab = var(key='k_ab', string='k<sub>AB</sub>', value=12.00,
           range=(0.01, 1000.00))
ab_vars = (va, vb, j_ab, k_ab, wa)

mainviews = (('twosinglets', twosinglets_vars), ('ab', ab_vars))
plots = []


class DnmrGui(QMainWindow):
    """
    Create the GUI for the application.

    Currently the app features a single simulation model (two uncoupled
    spins), and so a single main window. TODO: as views are added, create a
    toggle between GUI windows tailored to each simulation (e.g. appropriate
    widgets for data entry)
    """

    def __init__(self, parent=None):

        print('ititializing gui class')

        super(DnmrGui, self).__init__(parent)

        #self.simulation_vars = {}  # stores kwargs that model is called with
        #self.plots = []
        print('creating views list')
        self.views = []
        self.models = [dnmrplot_2spin, dnmrplot_AB]
        self.setObjectName('toplevel')
        self.setupUi()

    class MainView(QWidget):
        """A QWidget that has the following properties:
        - A top row of labeled QDoubleSpinBox es for data entry
        - Beneath them, a pqtgraph PlotWidget for the simulated plot
        - the ability to detect changes to the data entries, store their 
        current values, call the appropriate model and pass the simulation 
        results to the pyqtgraph widget
        """
        def __init__(self, name, *args):
            super().__init__()
            self.setObjectName(name + 'widget')
            self.setAutoFillBackground(True)
            self.setStyleSheet("background-color: rgb(60, 63, 65);")

            self.simulation_vars = {}

            layout = QGridLayout()
            layout.setObjectName(name + 'layout')

            for i, widget in enumerate(args):
                # make a label for the widget
                wlabel = QLabel(widget.string)
                wlabel.setObjectName(widget.key + '_label')
                wlabel.setStyleSheet('color: white')
                wlabel.setAlignment(Qt.AlignCenter)

                # Make a QDoubleSpinBox widget
                wbox = QDoubleSpinBox()
                wbox.setObjectName(widget.key)
                wbox.setStyleSheet('color: white')
                wbox.setRange(*widget.range)  # SET RANGE BEFORE VALUE
                wbox.setValue(widget.value)
                wbox.setAlignment(Qt.AlignCenter)
                wbox.setAccelerated(True)

                # Add label (above) and spinbox (below) to layout
                layout.addWidget(wlabel, 0, i)
                layout.addWidget(wbox, 1, i)

                # Store the default simulation value
                self.simulation_vars[widget.key] = widget.value

                # update the view if this widget's value is changed
                wbox.valueChanged.connect(
                    lambda val, key=widget.key: self.parent().parent()
                        .updateView(key, val))

            # Add pyqtgraph widget
            setConfigOption('background', (43, 43, 43))
            setConfigOption('foreground', (187, 187, 187))
            graphicsView = PlotWidget()

            layout.addWidget(graphicsView, 2, 0, 1, len(twosinglets_vars))
            plots.append(graphicsView.plot())
            # lets the graph span the entire width of the window, no matter how
            # many input widgets appear above

            # TODO: This looks to be wrong! second line smells off
            self.setLayout(layout)
            #self.layout().setObjectName('twosingletlayout')
            #print('twosinglet layout name is:', twoSingletLayout.objectName())
            #print('about to return twosingletwidget; name is: ',
                  #twoSingletWidget.objectName())

    def setupUi(self):
        """
        Set up the GUI with the default moded, default variables,
        and simulated lineshape.
        """

        self.setupCentral()
        self.setupModelBar()
        self.initializeGui()

    def setupModelBar(self):
        """
        Add a tool bar to the GUI for selecting which model to display 
        """

        leftToolBar = QToolBar()
        leftToolBar.setStyleSheet("background-color: rgb(60, 63, 65);")
        leftToolBar.setObjectName('lefttoolbar')
        #leftToolBar.addWidget(QLabel('Models!'))
        leftToolBar.addWidget(self.modelButtonGroup())
        self.addToolBar(Qt.LeftToolBarArea, leftToolBar)

    def modelButtonGroup(self):
        """
        A widget of radio buttons that will determine which QStackedWidget is
        displayed.
        """

        # It seems that in order for the buttonClicked signal to work,
        # self.ButtonGroup and not ButtonGroup is necessary. Does not work
        # with out 'self.' prefix!!!

        modelsWidget = QWidget()
        modelsWidget.setObjectName('modelswidget')
        modelsLayout = QVBoxLayout()
        modelsLayout.setObjectName('modelslayout')
        self.ButtonGroup = QButtonGroup()

        selectModelLabel = QLabel('Select Model:')
        selectModelLabel.setAlignment(Qt.AlignCenter)
        selectModelLabel.setStyleSheet('color: white')

        twosingletbutton = QRadioButton('Two uncoupled spin-1/2 nuclei')
        twosingletbutton.setObjectName('twosingletbutton')
        twosingletbutton.setStyleSheet('color: white')
        twosingletbutton.setChecked(True)
        self.ButtonGroup.addButton(twosingletbutton, 0)

        abbutton = QRadioButton('Two coupled spin-1/2 nuclei\n ("AB quartet)')
        abbutton.setObjectName('abbutton')
        abbutton.setStyleSheet('color: white')
        self.ButtonGroup.addButton(abbutton, 1)

        self.ButtonGroup.buttonClicked[int].connect(self.switchView)

        modelsLayout.addStretch()
        modelsLayout.addWidget(selectModelLabel)
        modelsLayout.addWidget(twosingletbutton)
        modelsLayout.addWidget(abbutton)
        modelsLayout.addStretch()
        modelsWidget.setLayout(modelsLayout)
        modelsWidget.setStyleSheet("background-color: rgb(60, 63, 65);")

        return modelsWidget

    def switchView(self, id):
        print('button %d has been pressed' % id)
        self.stackedWidget.setCurrentIndex(id)
        self.call_model()

    def setupCentral(self):

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setObjectName('stackedwidget')
        # self.createViews()
        # for view in views:
        #     self.stackedWidget.addWidget(view)
        # self.setCentralWidget(self.stackedWidget)
        for view in mainviews:
            widget = self.MainView(view[0], *view[1])
            self.stackedWidget.addWidget(widget)
        self.setCentralWidget(self.stackedWidget)

    def createViews(self):
        self.views.append(self.twoSingletView())
        self.views.append(self.ABView())

    def twoSingletView(self):

        twoSingletWidget = QWidget()
        twoSingletWidget.setObjectName('twosingletwidget')
        twoSingletWidget.setAutoFillBackground(True)
        twoSingletWidget.setStyleSheet("background-color: rgb(60, 63, 65);")

        twoSingletWidget.simulation_vars = {}

        twoSingletLayout = QGridLayout()
        twoSingletLayout.setObjectName('twosingletlayout')
        # More complex layouts can be considered in future, e.g. a horizontal
        #  layout containing a serious of vertical layouts containing labels
        # and spinboxes.

        for i, widget in enumerate(twosinglets_vars):
            # The namedtuple construct facilitates widget generation:
            wlabel = QLabel(widget.string)
            wlabel.setObjectName(widget.key + '_label')
            wlabel.setStyleSheet('color: white')
            wlabel.setAlignment(Qt.AlignCenter)

            wbox = QDoubleSpinBox()
            wbox.setObjectName(widget.key)
            wbox.setStyleSheet('color: white')
            wbox.setRange(*widget.range)  # SET RANGE BEFORE VALUE
            wbox.setValue(widget.value)
            wbox.setAlignment(Qt.AlignCenter)
            wbox.setAccelerated(True)

            # populate the dictionary with initial simulation variables
            #self.simulation_vars[widget.key] = widget.value
            twoSingletWidget.simulation_vars[widget.key] = widget.value
            #print(widget.string, ' added to dict')

            twoSingletLayout.addWidget(wlabel, 0, i)
            twoSingletLayout.addWidget(wbox, 1, i)

            # Using the lambda expression below allows extra information to
            # be passed to the self.update slot, allowing the delegator to
            # see who sent the signal, update the dictionary of model inputs,
            # call the model for a simulation result, and plot it. See:
            # https://mfitzp.io/article/transmit-extra-data-with-signals-in-pyqt/

            # noinspection PyUnresolvedReferences
            wbox.valueChanged.connect(
                lambda val, key=widget.key: self.updateView(key, val))

        #print('dict is now:', twoSingletWidget.simulation_vars)

        setConfigOption('background', (43, 43, 43))
        setConfigOption('foreground', (187, 187, 187))
        graphicsView = PlotWidget()
        self.plots.append(graphicsView.plot())
        twoSingletLayout.addWidget(graphicsView, 2, 0, 1, len(twosinglets_vars))
        # lets the graph span the entire width of the window, no matter how
        # many input widgets appear above

        # TODO: This looks to be wrong! second line smells off
        twoSingletWidget.setLayout(twoSingletLayout)
        twoSingletWidget.layout().setObjectName('twosingletlayout')
        print('twosinglet layout name is:', twoSingletLayout.objectName())
        print('about to return twosingletwidget; name is: ',
              twoSingletWidget.objectName())
        return twoSingletWidget

    def ABView(self):

        AB_Widget = QWidget()
        AB_Widget.setAutoFillBackground(True)
        AB_Widget.setStyleSheet("background-color: rgb(60, 63, 65);")
        AB_Widget.setObjectName('ABwidget')

        AB_Widget.simulation_vars = {}

        AB_Layout = QGridLayout()
        AB_Layout.setObjectName('ABlayout')
        # More complex layouts can be considered in future, e.g. a horizontal
        #  layout containing a serious of vertical layouts containing labels
        # and spinboxes.

        for i, widget in enumerate(ab_vars):
            # The namedtuple construct facilitates widget generation:
            wlabel = QLabel(widget.string)
            wlabel.setObjectName(widget.key + '_label')
            wlabel.setStyleSheet('color: white')
            wlabel.setAlignment(Qt.AlignCenter)

            wbox = QDoubleSpinBox()
            wbox.setObjectName(widget.key)
            wbox.setStyleSheet('color: white')
            wbox.setRange(*widget.range)  # SET RANGE BEFORE VALUE
            wbox.setValue(widget.value)
            wbox.setAlignment(Qt.AlignCenter)
            wbox.setAccelerated(True)

            # populate the dictionary with initial simulation variables
            AB_Widget.simulation_vars[widget.key] = widget.value
            print(widget.string, ' added to dict')
            AB_Layout.addWidget(wlabel, 0, i)
            AB_Layout.addWidget(wbox, 1, i)

            # Using the lambda expression below allows extra information to
            # be passed to the self.update slot, allowing the delegator to
            # see who sent the signal, update the dictionary of model inputs,
            # call the model for a simulation result, and plot it. See:
            # https://mfitzp.io/article/transmit-extra-data-with-signals-in-pyqt/

            # noinspection PyUnresolvedReferences
            wbox.valueChanged.connect(
                lambda val, key=widget.key: self.updateView(key, val))

        print('dict is now:', AB_Widget.simulation_vars)

        setConfigOption('background', (43, 43, 43))
        setConfigOption('foreground', (187, 187, 187))
        graphicsView = PlotWidget()
        self.plots.append(graphicsView.plot())
        AB_Layout.addWidget(graphicsView, 2, 0, 1, len(twosinglets_vars))
        # lets the graph span the entire width of the window, no matter how
        # many input widgets appear above

        # TODO: as with twosinglet, check second line and how names are done
        AB_Widget.setLayout(AB_Layout)
        AB_Widget.layout().setObjectName('ABlayout')

        return AB_Widget

    def initializeGui(self):

        # Initial view and plot determined by index in next 2 lines
        for i in range(len(plots)):
            self.stackedWidget.setCurrentIndex(i)
            plot = plots[i]
            plot.getViewBox().invertX(True)  # Reverse x axis "NMR style"
            plot.setData(*self.call_model())

        self.stackedWidget.setCurrentIndex(0)
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle('pyDNMR')
        self.statusBar().showMessage('Ready')

    def call_model(self):
        """
        Send the dictionary as **kwargs to the model
        :return: a spectrum, consisting of a tuple of x and y coordinate arrays
        """
        #x, y = dnmrplot_2spin(**self.simulation_vars)
        # x, y = dnmrplot_2spin(
        #     **self.stackedWidget.currentWidget().simulation_vars)
        model = self.models[self.stackedWidget.currentIndex()]
        x, y = model(
            **self.stackedWidget.currentWidget().simulation_vars)
        return x, y

    # TODO: this would override the builtin class function 'update'!
    # You probably want to rename this!
    def updateView(self, key, val):
        """
        Detect a change in numerical input; record the change in
        the dictionary of widget values; call the model to get an updated
        spectrum; and plot the spectrum.
        :param key: the dictionary key for the variable associated with the
        signalling widget
        :param val: the current value of the signalling widget
        """
        #self.simulation_vars[key] = val
        self.stackedWidget.currentWidget().simulation_vars[key] = val
        self.plot_graph()

        # plot = self.plots[self.stackedWidget.currentIndex()]
        # plot.setData(*self.call_model())  # original routine

        # OR:

        # spectrum = TwoSinglets(**self.simulation_vars).spectrum()
        # self.plotdata.setData(*spectrum)  # using new TwoSinglets class

    def plot_graph(self):
        activePlot = plots[self.stackedWidget.currentIndex()]
        activePlot.setData(*self.call_model())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = DnmrGui()
    ui.show()
    sys.exit(app.exec_())
