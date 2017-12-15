from PySide.QtGui import QGraphicsScene

from classy_nodes.view import ClassyNode


class ClassyScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

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
