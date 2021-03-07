from PyQt5 import QtWidgets, QtCore

class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent):
        super(Model, self).__init__(parent)
        self.root = Item()
        self.columns = []

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        data = self.item(index).data( self.columns[index.column()] )
        if role == QtCore.Qt.EditRole:
            if data is None:
                return ''
            return data
        if role == QtCore.Qt.DisplayRole:
            if data is None:
                return 'None'
            return data
        return QtCore.QVariant()

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columns[section]
        
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return section + 1

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if parent == QtCore.QModelIndex():
            return self.createIndex( row, column, self.root.child(row) )

        if parent.isValid():
            return self.createIndex( row, column, self.item(parent).child(row) )

        return QtCore.QModelIndex()

    def insertColumn(self, column, parent=QtCore.QModelIndex()):
        self.insertColumns(column, 1, parent)

    def insertColumns(self, column, count, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, column, column + count - 1)
        self.columns[column:column] = [ '' for i in range(count) ]
        self.endInsertColumns()

    def insertRow(self, row, parent=QtCore.QModelIndex()):
        self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self.item(parent).insert(row, count)
        self.endInsertRows()

    def item(self, index):
        if index == QtCore.QModelIndex() or index is None:
            return self.root
        if index.isValid():
            return index.internalPointer()
        return QtCore.QModelIndex()
        
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        item = self.item(index)
        if item.parent() == self.root:
            return QtCore.QModelIndex()
        return self.createIndex(index.row(), 0, self.item(index).parent())

    def removeColumn(self, column, parent=QtCore.QModelIndex()):
        self.removeColumns(column, 1, parent)

    def removeColumns(self, column, count, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, column, column + count - 1)
        del self.columns[column:column+count]
        self.endRemoveColumns()

    def removeRow(self, row, parent=QtCore.QModelIndex()):
        self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self.item(parent).remove(row, count)
        self.endRemoveRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len( self.item(parent).children() )

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.item(index).data( self.columns[index.column()], value )
            return True
        return False

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole):
        if orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.EditRole:
            self.columns[section] = value
        return True

class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, setModelDataEvent=None):
        super(Delegate, self).__init__(parent)
        self.setModelDataEvent = setModelDataEvent
 
    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)
 
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(str(value))
 
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())
        if not self.setModelDataEvent is None:
            self.setModelDataEvent()

class Item(object):
    def __init__(self, parent=None):
        self._data = {}
        self._parent = parent
        self._children = []

    def append(self):
        self._children.append( Item(self) )

    def child(self, row):
        return self._children[row]

    def children(self):
        return self._children

    def data(self, key=None, value=None):
        if key is None:
            return self._data
        if type(key) is dict:
            self._data = key
            return
        if value is None:
            return self._data.get(key)
        self._data[key] = value

    def insert(self, row, count=1):
        self._children[row:row] = [ Item(self) for i in range(count) ]

    def parent(self, item=None):
        if item is None:
            return self._parent
        self._parent = item

    def pop(self, row, count=1):
        d = self._children[row:row+count]
        del self._children[row:row+count]
        return d

    def remove(self, row, count=1):
        del self._children[row:row+count]

    def row(self):
        if not self._parent is None:
            if self in self._parent._children:
                return self._parent._children.index(self)
        return -1
