from PySide.QtCore import QRect
from PySide.QtGui import QGraphicsItem, QPainter


from PySide.QtGui import QColor
from PySide.QtGui import QPen
from PySide.QtGui import QFontMetrics
from PySide.QtGui import QFont
from PySide.QtGui import QBrush

nodes_font = QFont("Impact", 19)


class ClassyNode(QGraphicsItem):
    def __init__(self):
        QGraphicsItem.__init__(self)
        self.label = "Node"
        self.edges_in = []
        self.edges_out = []

        self.metrics = QFontMetrics(nodes_font)

        self._b_width = 0
        self._b_height = 0
        self._x = 0
        self._y = 0

        self.margin = 5

        self.node_pen = QPen(QColor(30, 30, 30))
        self.selected_pen = QPen(QColor(200, 200, 30))
        self.node_brush = QBrush(QColor(120, 120, 30))
        self._update_size()

        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRect(self._x,
                     self._y,
                     self._b_width,
                     self._b_height)

    def _update_size(self):
        self._b_width = self.metrics.averageCharWidth() * (len(self.label) + 1) + (self.margin * 2)
        self._b_height = self.metrics.height() + (self.margin * 2)

        self._x = -(self._b_width / 2) - self.margin
        self._y = -(self._b_height / 2) - self.margin

    def paint(self, painter, option, widget=None):
        """
        Override of QGraphicsItem.paint method. Implement this in your child classes to
        make nodes with the look you want.
            :param QPainter painter:
            :param option:
            :param widget:
        """
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Distinguish the selected nodes from the unselected ones.
        if self.isSelected():
            painter.setPen(self.selected_pen)
        else:
            painter.setPen(self.node_pen)
        painter.setBrush(self.node_brush)

        r = self.boundingRect()
        painter.drawRect(r)

        # --- Draw name of the node
        painter.setPen(self.node_pen)
        painter.setFont(nodes_font)
        painter.drawText(r.bottomLeft().x() + self.margin, r.bottomLeft().y() - self.margin, self.label)
