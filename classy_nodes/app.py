from PySide.QtGui import QWidget
from PySide.QtGui import QVBoxLayout

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
        self.scene.add_node('node1')
        self.scene.add_node('node2')
        self.scene.add_node('node3')
        self.scene.add_node('node4')
        self.scene.add_node('node5')
        self.scene.add_node('node6')
        self.scene.add_node('node7')

        self.scene.add_edge('node1', 'node3', conditional_to=True)

        self.scene.add_edge('node1', 'node2')

        self.scene.add_edge('node1', 'node5')

        self.scene.add_edge('node4', 'node6', two_way=True, conditional_to=True, conditional_from=False)
