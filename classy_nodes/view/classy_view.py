from PySide.QtCore import Qt, QRectF, QPointF, QPoint, QRect
from PySide.QtGui import QGraphicsView, QTransform, QGraphicsItem, QPen, QColor, QBrush, QRubberBand

from classy_nodes.view.classy_node import ClassyNode


class ClassyView(QGraphicsView):

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.prev_mouse_pos = None
        self.setSceneRect(-64000, -64000, 128000, 128000)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.current_scale = 1
        self.max_zoom = 3.0
        self.base_size = None

        # self.text_pen = QPen(QColor(128, 128, 128))
        # self.text_brush = QBrush(QColor(128, 128, 128))
        # self.font = QFont("Impact", 18)
        # self.name_font = QFont("Impact", 8)

        self.zoom_start = QPoint()
        self.zoom_start_transform = QTransform()

        self.setFocusPolicy(Qt.WheelFocus)

        # =======================================================================
        # SELECTION OF NODES
        # =======================================================================
        # If true the widget will add to the selection
        self.extend_selection = False
        self.remove_selection = False
        self.selection_start = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):
        """
        Called whenever the mouse is pressed inside the view
            :param QMouseEvent event:
        """
        # --- If shift is pressed items will be added to selection
        if event.modifiers() == Qt.ShiftModifier:
            self.extend_selection = True
        else:
            self.extend_selection = False

        # --- If alt is pressed items will be removed from selection
        if event.modifiers() == Qt.AltModifier:
            self.remove_selection = True
        else:
            self.remove_selection = False

        if event.button() == Qt.MidButton:  # Start viewport translation
            self.prev_mouse_pos = event.globalPos()
        elif event.button() == Qt.RightButton:  # Start viewport zoom
            self.zoom_start = event.pos()
            self.zoom_start_transform = self.transform()
        elif event.button() == Qt.LeftButton:  # Left mouse pressed. Either select node or start rubber band drag
            node = self.scene().get_node_at_point(self.mapToScene(event.pos()))
            if node:
                if not self.extend_selection and not node.isSelected() and not self.remove_selection:
                    for item in self.scene().selectedItems():
                        item.setSelected(False)

                if self.remove_selection:
                    node.setSelected(False)
                else:
                    node.setSelected(True)

                if self.extend_selection or self.remove_selection:
                    event.accept()
                    return
                else:
                    return QGraphicsView.mousePressEvent(self, event)
            else:
                self.selection_start = event.pos()
                self.rubber_band.setGeometry(QRect(self.selection_start, self.selection_start))
                self.rubber_band.show()
                event.accept()
        else:  # Unknown type of mouse button. Just skip it.
            return QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Called whenever the mouse is moved inside the viewport and ONE of mouse buttons is pressed.
            :param QMouseEvent event:
        """
        if event.buttons() == Qt.MidButton:  # Translate the viewport
            if self.prev_mouse_pos:
                current_mouse_pos = event.globalPos()
                x = (current_mouse_pos - self.prev_mouse_pos).x()
                y = (current_mouse_pos - self.prev_mouse_pos).y()
                self.translate(x / self.current_scale, y / self.current_scale)
            self.prev_mouse_pos = event.globalPos()
        elif event.buttons() == Qt.RightButton:  # Zoom viewport
            if event.pos().x() > self.zoom_start.x():
                scale_value = 1 + abs((event.x() - self.zoom_start.x()) / 100.0)
                self.zoom(scale_value)
            elif event.pos().x() < self.zoom_start.x():
                scale_value = 1.0 / (1 + (abs((event.x() - self.zoom_start.x())) / 100.0))
                self.zoom(scale_value)
        elif event.buttons() == Qt.LeftButton:  # Drag selection rubber band
            if self.rubber_band.isHidden():
                return QGraphicsView.mouseMoveEvent(self, event)
            selection_rect = QRect()
            point = event.pos()
            selection_rect.setX(point.x() if point.x() < self.selection_start.x() else self.selection_start.x())
            selection_rect.setY(point.y() if point.y() < self.selection_start.y() else self.selection_start.y())

            selection_rect.setWidth(abs(point.x() - self.selection_start.x()))
            selection_rect.setHeight(abs(point.y() - self.selection_start.y()))
            self.rubber_band.setGeometry(selection_rect)
            event.accept()
        else:  # Unknown type of mouse button. Just skip it.
            return QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Called whenever the mouse button is released after it's been clicked inside viewport.
            :param QMouseEvent event:
        """
        if event.button() == Qt.LeftButton:
            if not self.rubber_band.isHidden():
                # --- selection of items with rubber band is handled here
                select = True
                if event.modifiers() == Qt.ShiftModifier:
                    self.extend_selection = True
                elif event.modifiers() == Qt.AltModifier:
                    self.extend_selection = True
                    select = False
                else:
                    self.extend_selection = False
                self.select_items_in_rubber_band(self.rubber_band.geometry(), self.extend_selection, select)
            else:
                # --- selection through click is handled here
                item = self.itemAt(event.pos())
                if item is not None:
                    if not self.remove_selection:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        self.rubber_band.hide()
        QGraphicsView.mouseReleaseEvent(self, event)

    def select_items_in_rubber_band(self, rect, append=True, select=True):
        """
        Iterates all the items that collides with selection rubber band and selects them if they are selectable.
            :param QRect rect: selection rectangle (this is the rubber band geometry)
            :param bool append: if set to True an old selection will be preserved.
            :param select: if set to False those items will be unselected.
        """
        modified = False
        if append is False:
            self.scene().clearSelection()
        scene_top_left = self.mapToScene(rect.topLeft())
        scene_bottom_right = self.mapToScene(rect.bottomRight())
        items = self.scene().items(QRectF(scene_top_left, scene_bottom_right),
                                   Qt.IntersectsItemBoundingRect)
        for item in items:
            if (item.flags() & QGraphicsItem.ItemIsSelectable) == QGraphicsItem.ItemIsSelectable:
                item.setSelected(select)
                modified = True
        if modified:
            self.scene().selectionChanged.emit()
            # self.scene().emit(SIGNAL("selectionChanged()"))

    def zoom(self, scale_value):
        """
        Changes the scale of the current scene by the value provided with argument. This scale is calculated mostly
        during the right mouse dragging.
            :type scale_value: float
            :return: None
            :rtype: None
        """
        if scale_value <= 0.1:
            scale_value = .01

        current_transform = self.zoom_start_transform  # Get the current transform for calculations

        # Zoom start is a zoom focus point. The scene will be zooming in or out against this point
        translate_matrix = QTransform.fromTranslate(self.zoom_start.x(), self.zoom_start.y())
        inv_translate_matrix = translate_matrix.inverted()
        # This is current transform translated so that the zoom start point is in 0, 0
        local_current_transform = current_transform * inv_translate_matrix[0]

        # noinspection PyCallByClass,PyTypeChecker
        scale_matrix = QTransform.fromScale(scale_value, scale_value)

        scaled_transform = local_current_transform * scale_matrix * translate_matrix

        # Check if the scale exceeds the max_zoom value. Zooming too much destroys the render quality of a graph
        scaled_transform_scale = self.get_matrix_scale(scaled_transform)
        if scaled_transform_scale > self.max_zoom:
            keep_scale_value = self.max_zoom / scaled_transform_scale
            # noinspection PyCallByClass,PyTypeChecker
            scale_matrix = scale_matrix * QTransform.fromScale(keep_scale_value, keep_scale_value)
            scaled_transform = local_current_transform * scale_matrix * translate_matrix

        # set the final transform and keep the current scale in a variable
        self.setTransform(scaled_transform)
        self.get_current_scale()

    def get_current_scale(self):
        """
        Returns the scale value of current viewport matrix.
            :rtype: float
        """
        matrix = self.transform()
        map_point_zero = QPointF(0.0, 0.0)
        map_point_one = QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        self.current_scale = mapped_point_one.x() - mapped_point_zero.x()

    @staticmethod
    def get_matrix_scale(matrix):
        """
        Gets the scale component of a matrix provided as an argument
            :param matrix:
            :rtype: float
        """
        map_point_zero = QPointF(0.0, 0.0)
        map_point_one = QPointF(1.0, 0.0)

        mapped_point_zero = matrix.map(map_point_zero)
        mapped_point_one = matrix.map(map_point_one)
        return (mapped_point_one - mapped_point_zero).manhattanLength()

    def wheelEvent(self, event):
        """
        Called when user uses the mouse wheel inside the viewport.
            :param QMouseEvent event:
        """
        delta = event.delta()
        self.zoom_start_transform = self.transform()

        self.zoom_start = event.pos()
        if delta < 0:
            scale_value = .9
        else:
            scale_value = 1.1

        self.zoom(scale_value)

    def resizeEvent(self, event):
        """
        Resize the scene together with scaling of the viewport.
            :param event:
            :return: None
        """
        current_size = self.size()

        if self.base_size is None:
            self.setBaseSize()

        if self.base_size is not 0 and self.base_size is not None:
            scale_value = float(current_size.width()) / float(self.base_size.width())

            if scale_value * self.current_scale > self.max_zoom:  # Keep the maximum scale allowed
                scale_value *= self.max_zoom / (scale_value * self.current_scale)

            self.base_size = self.size()
            self.scale(scale_value, scale_value)

        self.get_current_scale()
        return QGraphicsView.resizeEvent(self, event)

    def setBaseSize(self):
        """
        """
        self.base_size = self.size()

    def fitInView(self, rect, keep_aspect_ratio):
        """
        Overrides default fitInView method to keep the maximum zoom value (we want to prevent from zooming too much)
            :param rect: Rectangle to fit in the view
            :type rect: QRectF
            :param keep_aspect_ratio: not used.
            :return: None
        """

        self.setTransform(QTransform())  # Start from identity transform

        top_left_offset = self.mapToScene(0, 0)  # This will put the 0,0 point of scene in 0,0 point of view
        top_left_transform = QTransform.fromTranslate(top_left_offset.x(), top_left_offset.y())

        current_window_size = self.size()

        # calculate the scale needed to fit this rectangle in the view keeping the max zoom in
        if self.width() / float(self.height()) >= rect.width() / rect.height():
            scale_value = min(self.height() / float(rect.height()), self.max_zoom)
        else:
            scale_value = min(self.width() / float(rect.width()), self.max_zoom)
        scale_matrix = QTransform.fromScale(scale_value, scale_value)
        scaled = scale_matrix * top_left_transform
        self.setTransform(scaled)

        # This point will be placed in a center of the view
        fit_center = rect.center()
        fit_center_scaled = scaled.map(QPoint(fit_center.x(), fit_center.y()))  # scale matrix changed this
        fit_center_matrix = QTransform.fromTranslate(fit_center_scaled.x(), fit_center_scaled.y())

        # Get the center of the viewport, add a top_left_offset to it to keep everything consistent
        translated_center = QPointF(current_window_size.width() / 2.0, current_window_size.height() / 2.0)
        to_center_offset = translated_center + top_left_offset
        to_screen_center_transform = QTransform.fromTranslate(to_center_offset.x(), to_center_offset.y())

        # Set the final transform
        self.setTransform(scaled * fit_center_matrix.inverted()[0] * to_screen_center_transform)

    def zoom_to_selected(self):
        """
        Fits the united bounding rect of selected gung nodes in the viewport keeping the maximum zoom value.
            :return: None
        """
        sel_items = self.scene().selectedItems()
        if len(sel_items) > 0:
            zoom_rect = QRectF()
            for item in sel_items:
                if not isinstance(item, ClassyNode):
                    continue
                item_rect = item.boundingRect()
                zoom_rect = zoom_rect.united(item_rect.translated(item.x(), item.y()))

            self.fitInView(zoom_rect, Qt.KeepAspectRatio)
            self.get_current_scale()

    def zoom_to_all(self):
        """
        Tries to fit the viewport so that all the items of the scene are visible.
        """
        all_nodes = self.get_nodes()
        if len(all_nodes) > 0:
            zoom_rect = all_nodes[0].boundingRect().translated(all_nodes[0].x(), all_nodes[0].y())
            for item in all_nodes[1:]:
                item_rect = item.boundingRect()
                zoom_rect = zoom_rect.united(item_rect.translated(item.x(), item.y()))
            self.fitInView(zoom_rect, Qt.KeepAspectRatio)
            self.get_current_scale()
        else:
            self.setTransform(QTransform())

    def get_nodes(self):
        return self.scene().getItems()

    def keyPressEvent(self, event):
        """
        Called whenever a keyboard button is pressed and the viewport has a keyboard focus
            :param qt_gui.QKeyEvent event:
        """
        if event.key() == Qt.Key_F:
            self.zoom_to_selected()
            event.accept()
        elif event.key() == Qt.Key_A:
            self.zoom_to_all()
            event.accept()
        else:
            return QGraphicsView.keyPressEvent(self, event)
