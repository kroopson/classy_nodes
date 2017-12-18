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

    def add_node(self, name):
        if name in self.nodes:
            return self.nodes.get(name)

        node = ClassyNode(name)
        self.nodes[name] = node
        self.addItem(node)

    def add_edge(self, node_from, node_to, two_way=False):
        edge = ClassyEdge()
        edge.set_node_from(self.nodes.get(node_from))
        edge.set_node_to(self.nodes.get(node_to))
        self.addItem(edge)
        self.edges.append(edge)
