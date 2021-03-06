from PySide.QtCore import QPointF
from PySide.QtGui import QTransform
from PySide.QtGui import QGraphicsScene

from classy_nodes.view import ClassyNode, ClassyEdge


class ClassyScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

        self.nodes = dict()
        self.edges = []

    def get_node_at_point(self, pos):
        """
        Iterate all the items that occlude with the point passed as pos and see if there is a GungNode among them.
        If not then return None
            :param pos: QPoint
            :rtype: GungNode or None
        """
        hit_items = self.items(pos)
        if not len(hit_items):
            return
        hit_item = None
        for hi in hit_items:
            if isinstance(hi, ClassyNode):
                hit_item = hi
                break

        return hit_item

    def get_next_node_z_value(self):
        if not self.nodes:
            return 10.0
        z = max([self.nodes.get(x).zValue() for x in self.nodes])
        return z + 0.01

    def add_node(self, name):
        if name in self.nodes:
            return self.nodes.get(name)

        node = ClassyNode(name)
        self.nodes[name] = node
        self.addItem(node)
        node.setZValue(self.get_next_node_z_value())

    def get_node(self, node_name):
        return self.nodes.get(node_name, None)

    def add_edge(self, node_from, node_to, conditional_to=False, two_way=False, conditional_from=False):
        edge = ClassyEdge(two_way=two_way, conditional_to=conditional_to, conditional_from=conditional_from)
        edge.set_node_from(self.nodes.get(node_from))
        edge.set_node_to(self.nodes.get(node_to))
        self.addItem(edge)
        self.edges.append(edge)
        edge.update()

    def clear(self):
        QGraphicsScene.clear(self)
        self.nodes = dict()
        self.edges = list()

    def layout_nodes(self):
        nodes_count = len(self.nodes)
        if nodes_count == 0:
            return

        step = 360 / nodes_count

        total_width = 0
        for node_name in self.nodes:
            total_width += self.nodes.get(node_name).boundingRect().width()

        index = 0
        for node in self.nodes:
            # noinspection PyUnresolvedReferences
            xform = QTransform()
            angle = index * step
            xform.rotate(angle)

            mapped = xform.map(QPointF(total_width / 2, 0))
            self.nodes.get(node).setPos(mapped)
            index += 1
