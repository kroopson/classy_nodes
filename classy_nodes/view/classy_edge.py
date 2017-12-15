from PySide.QtCore import QRect, QPointF, Qt
from PySide.QtGui import QGraphicsItem, QPainter, QPen, QColor, QVector2D, QTransform, QBrush
import weakref


class ClassyEdge(QGraphicsItem):
    def __init__(self):
        QGraphicsItem.__init__(self)

        self.node_from = None
        self.node_to = None

        self.pen = QPen(QColor(50, 90, 50))
        self.brush = QBrush(QColor(50, 90, 50))
        self.pen.setWidth(4)
        self.arrow_length = 10

    def boundingRect(self):
        if not self.node_from or not self.node_to:
            return QRect()

        n1 = self.node_from()
        n2 = self.node_to()

        if n1 is None or n2 is None:
            return QRect()

        node_from_pos = n1.pos()
        node_to_pos = n2.pos()

        bbox = QRect(min(node_from_pos.x(), node_to_pos.x()),
                     min(node_from_pos.y(), node_to_pos.y()),
                     abs(node_from_pos.x() - node_to_pos.x()),
                     abs(node_from_pos.y() - node_to_pos.y()))
        return bbox

    def get_node_from_pos(self):
        if self.node_from is None:
            return QPointF()
        n1 = self.node_from()

        if n1 is None:
            return QPointF()

        return n1.pos()

    def get_node_to_pos(self):
        if self.node_to is None:
            return QPointF()
        n2 = self.node_to()

        if n2 is None:
            return QPointF()

        return n2.pos()

    def set_node_from(self, node):
        self.node_from = weakref.ref(node)

    def set_node_to(self, node):
        self.node_to = weakref.ref(node)

    def paint(self, painter, option, widget=None):
        """
        Override of QGraphicsItem.paint method. Implement this in your child classes to
        make nodes with the look you want.
            :param QPainter painter:
            :param option:
            :param widget:
        """
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(self.pen)

        r = self.boundingRect()

        f = self.get_node_from_pos()
        t = self.get_node_to_pos()

        painter.drawLine(f, t)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        center = (f + t) / 2

        center_to_t = QVector2D(t - center)

        center_to_t.normalize()

        center_to_t *= self.arrow_length
        t = QTransform()
        arrow_points = [center + center_to_t.toPointF()]
        t.rotate(120)
        arrow_points.append(center + t.map(center_to_t.toPointF()))
        t.rotate(120)
        arrow_points.append(center + t.map(center_to_t.toPointF()))
        painter.drawPolygon(arrow_points)

