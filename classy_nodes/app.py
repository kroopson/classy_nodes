from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout

from view import ClassyNode
from view import ClassyView
from view import ClassyScene
from view import ClassyEdge


class ClassyWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QVBoxLayout(self)
        self.view = ClassyView(self)
        layout.addWidget(self.view)
        self.scene = ClassyScene(self)
        self.view.setScene(self.scene)
        self.node = ClassyNode()
        self.node2 = ClassyNode()
        self.scene.addItem(self.node)
        self.scene.addItem(self.node2)
        self.node.setZValue(10.0)
        self.node2.setZValue(10.1)

        self.edge = ClassyEdge()
        self.scene.addItem(self.edge)

        self.edge.set_node_from(self.node)
        self.edge.set_node_to(self.node2)
