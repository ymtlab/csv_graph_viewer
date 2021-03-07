# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
import pandas as pd
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from graph_widget import Ui_Form
from mainwindow import Ui_MainWindow
from model import Model, Delegate

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.folder = None
        self.graph_widgets = []
        self.model = Model(self)
        self.scrollAreaWidget = QtWidgets.QWidget(self.ui.scrollArea)
        self.graphs_leyout = QtWidgets.QVBoxLayout(self.scrollAreaWidget)

        self.ui.listView.setModel(self.model)
        self.ui.listView.setItemDelegate(Delegate())
        self.ui.scrollArea.setWidget(self.scrollAreaWidget)
        self.ui.actionOpen_folder.triggered.connect(self.open_folder)
        self.ui.listView.clicked.connect(self.listview_clicked)
        
        self.ui.plotWidget.setBackground("#FFFFFFFF")
        plotitem = self.ui.plotWidget.plotItem
        plotitem.setLabels(bottom='csv', left='max absolute force')
        plotitem.getAxis('bottom').setPen(pg.mkPen(color='#000000'))
        plotitem.getAxis('left').setPen(pg.mkPen(color='#000000'))

        for c, column in enumerate(['Name' , 'Path', 'DataFrame']):
            self.model.insertColumn(c)
            self.model.setHeaderData(c, QtCore.Qt.Horizontal, column)

    def add_graph_widget(self, title):
        graph_widget = GraphWidget(self, title)
        self.graph_widgets.append(graph_widget)
        self.graphs_leyout.addWidget(graph_widget)
        
        graph_widget.ui.plotWidget.setBackground("#FFFFFFFF")
        plotitem = graph_widget.ui.plotWidget.plotItem
        plotitem.setLabels(bottom='time', left='force')
        plotitem.getAxis('bottom').setPen(pg.mkPen(color='#000000'))
        plotitem.getAxis('left').setPen(pg.mkPen(color='#000000'))

        return graph_widget

    def open_folder(self, folder=None):
        if folder is False:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder', '/', QtWidgets.QFileDialog.ShowDirsOnly)
            if folder == '':
                return
        self.folder = folder
        maxes = []

        for path in list(Path(folder).glob('*.csv'))[::-1]:
            row = self.model.rowCount()
            self.model.insertRow(row)
            self.model.setData(self.model.index(row, 0), path.name)
            self.model.setData(self.model.index(row, 1), path)
            self.ui.listView.setCurrentIndex(self.model.index(row, 0))

            # laod csv
            df = pd.read_csv(path)
            self.model.setData(self.model.index(row, 2), df)

            # add graph
            graph_widget = self.add_graph_widget(path.name)
            plot_widget = graph_widget.ui.plotWidget
            plot_widget.addItem( pg.PlotDataItem(x=df['time'], y=df['force'], pen=pg.mkPen(color='#000000', width=1), antialias=True) )

            min_value = df['force'].min()
            max_value = df['force'].max()
            graph_widget.ui.lineEdit.setText( str(min_value) )
            graph_widget.ui.lineEdit_2.setText( str(max_value) )

            if abs(min_value) > max_value:
                maxes.append( abs(min_value) )
            else:
                maxes.append( abs(max_value) )

        bar_graph = pg.BarGraphItem(x=range(len(maxes)), height=maxes, width=0.6, brush='b')
        self.ui.plotWidget.addItem(bar_graph)

    def listview_clicked(self, index):
        selected_rows = [ index.row() for index in self.ui.listView.selectedIndexes() ]
        show_indexes = []
        for i in range(self.model.rowCount()):
            if i in selected_rows:
                self.graph_widgets[i].show()
                show_indexes.append(i)
            else:
                self.graph_widgets[i].hide()
        self.ui.plotWidget.clear()
        bar_graph = pg.BarGraphItem(x=show_indexes, height=[ self.model.data(self.model.index(i, 2))['force'].max() for i in show_indexes ], width=0.6, brush='r')
        self.ui.plotWidget.addItem(bar_graph)

class GraphWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, title=None):
        super(GraphWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.groupBox.setTitle(title)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
