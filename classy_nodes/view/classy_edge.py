import weakref
from PySide.QtCore import QRect, QPointF, Qt
from PySide.QtGui import QGraphicsItem, QPainter, QPen, QVector2D, QTransform, QBrush
from config import CONDITIONAL_TRANSITION_COLOR
from config import NON_CONDITIONAL_TRANSITION_COLOR


class ClassyEdge(QGraphicsItem):
    def __init__(self, conditional_to=False, two_way=False, conditional_from=False):
        QGraphicsItem.__init__(self)

        self.node_from = None
        self.node_to = None

        self.conditional_to = conditional_to
        self.conditional_from = conditional_from

        if conditional_to:
            self.pen = QPen(CONDITIONAL_TRANSITION_COLOR)
            self.brush = QBrush(CONDITIONAL_TRANSITION_COLOR)
        else:
            self.pen = QPen(NON_CONDITIONAL_TRANSITION_COLOR)
            self.brush = QBrush(NON_CONDITIONAL_TRANSITION_COLOR)

        self.arrow_length = 10
        self.two_way = two_way

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

        f = self.get_node_from_pos()
        t = self.get_node_to_pos()
        if not self.two_way:
            if self.conditional_to:
                pen = QPen(CONDITIONAL_TRANSITION_COLOR)
                pen.setWidth(4)
                painter.setPen(pen)
                painter.setBrush(CONDITIONAL_TRANSITION_COLOR)
            else:
                pen = QPen(NON_CONDITIONAL_TRANSITION_COLOR)
                pen.setWidth(4)
                painter.setPen(pen)
                painter.setBrush(NON_CONDITIONAL_TRANSITION_COLOR)
            self._draw_arrow(painter, f, t, self.arrow_length)
            return

        to_vector = QVector2D(t - f)
        to_vector.normalize()
        to_vector *= self.arrow_length

        xform = QTransform()
        xform.rotate(90)

        mapped = xform.map(to_vector.toPointF())

        from_start = mapped + f
        from_end = mapped + t
        if self.conditional_to:
            pen = QPen(CONDITIONAL_TRANSITION_COLOR)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(CONDITIONAL_TRANSITION_COLOR)
        else:
            pen = QPen(NON_CONDITIONAL_TRANSITION_COLOR)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(NON_CONDITIONAL_TRANSITION_COLOR)
        self._draw_arrow(painter, from_start, from_end, self.arrow_length)

        from_start = -mapped + t
        from_end = -mapped + f
        if self.conditional_from:
            pen = QPen(CONDITIONAL_TRANSITION_COLOR)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(CONDITIONAL_TRANSITION_COLOR)
        else:
            pen = QPen(NON_CONDITIONAL_TRANSITION_COLOR)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.setBrush(NON_CONDITIONAL_TRANSITION_COLOR)
        self._draw_arrow(painter, from_start, from_end, self.arrow_length)


    @staticmethod
    def _draw_arrow(painter, from_point, to_point, arrow_size=5):
        painter.drawLine(from_point, to_point)
        painter.setPen(Qt.NoPen)
        center = (from_point + to_point) / 2

        center_to_t = QVector2D(to_point - center)

        center_to_t.normalize()

        center_to_t *= arrow_size
        t = QTransform()
        arrow_points = [center + center_to_t.toPointF()]
        t.rotate(120)
        arrow_points.append(center + t.map(center_to_t.toPointF()))
        t.rotate(120)
        arrow_points.append(center + t.map(center_to_t.toPointF()))
        painter.drawPolygon(arrow_points)
