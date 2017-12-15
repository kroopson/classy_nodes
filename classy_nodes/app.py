from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout

from view import ClassyNode
from view import ClassyView
from view import ClassyScene


class ClassyWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QVBoxLayout(self)
        self.view = ClassyView(self)
        layout.addWidget(self.view)
        self.scene = ClassyScene(self)
        self.view.setScene(self.scene)
        self.node = ClassyNode()
        self.scene.addItem(self.node)
