from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

class Layer(QtCore.QObject):
    def __init__(self, host, child, alignment = Qt.AlignLeft, setWidth = False, setHeight = False, parent = None):
        super().__init__(parent)
        self._host = host
        self._child = child
        self._alignment = alignment
        self._setWidth = setWidth
        self._setHeight = setHeight
        child.setParent(host)
        host.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched != self._host or event.type() != QtCore.QEvent.Resize:
            return False
        hostSize = event.size()
        childSize = self._child.sizeHint()
        alignment = self._alignment
        x = 0
        y = 0
        dWidth = max(0, hostSize.width() - childSize.width())
        dHeight = max(0, hostSize.height() - childSize.height())
        if alignment & Qt.AlignRight:
            x = dWidth
        elif alignment & Qt.AlignHCenter:
            x = dWidth / 2
        if alignment & Qt.AlignVCenter:
            y = dHeight / 2
        elif alignment & Qt.AlignBottom:
            y = dHeight
        width = hostSize.width() if self._setWidth else childSize.width()
        height = hostSize.height() if self._setHeight else childSize.height()
        self._child.setGeometry(x, y, width, height)
        return False

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    label1 = QtWidgets.QLabel("right label")
    label2 = QtWidgets.QLabel("bottom label")
    layer1 = Layer(widget, label1, Qt.AlignRight)
    layer2 = Layer(widget, label2, Qt.AlignBottom | Qt.AlignHCenter, True)
    widget.show()
    sys.exit(app.exec_())