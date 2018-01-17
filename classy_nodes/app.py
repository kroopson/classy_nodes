import os
import re

from PySide.QtGui import QWidget, QMessageBox
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QMenuBar
from PySide.QtGui import QMenu
from PySide.QtGui import QFileDialog
from PySide.QtGui import QAction
from PySide.QtGui import QPlainTextEdit
from PySide.QtGui import QSplitter
from PySide.QtGui import QLabel
from PySide.QtGui import QHBoxLayout

from PySide.QtCore import Slot, SIGNAL
from PySide.QtCore import QSettings
from PySide.QtCore import Qt

from classy_nodes.view.classy_edge import EdgeWidget
from view import ClassyView
from view import ClassyScene


class ClassyWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout(self)
        horiz_layout = QHBoxLayout()
        self.conditional_legend_widget = EdgeWidget(self, True)
        self.conditional_legend_widget.setMinimumHeight(15)
        horiz_layout.addWidget(self.conditional_legend_widget)

        self.conditional_legend_label = QLabel("Conditional transition", self)
        horiz_layout.addWidget(self.conditional_legend_label)

        self.unconditional_legend_widget = EdgeWidget(self, False)
        self.unconditional_legend_widget.setMinimumHeight(15)
        horiz_layout.addWidget(self.unconditional_legend_widget)
        self.unconditional_legend_label = QLabel("Non-conditional transition", self)
        horiz_layout.addWidget(self.unconditional_legend_label)

        layout.addLayout(horiz_layout)

        self.splitter = QSplitter(self)

        layout.addWidget(self.splitter)

        self.view = ClassyView(self.splitter)
        # layout.addWidget(self.view)
        self.scene = ClassyScene(self)
        self.view.setScene(self.scene)

        self._menu_bar = QMenuBar(self)
        self._menu = QMenu("&File")
        self._menu_bar.addMenu(self._menu)
        layout.setMenuBar(self._menu_bar)

        self.open_action = QAction("O&pen", self)
        self.exit_action = QAction("E&xit", self)
        self._menu.addAction(self.open_action)
        self._menu.addAction(self.exit_action)

        self.connect(self.open_action, SIGNAL("triggered()"), self.open_file)
        self.connect(self.exit_action, SIGNAL("triggered()"), self.close)

        self.settings = QSettings("CD Projekt RED", "TweakDB")

        self.log_window = QPlainTextEdit(self.splitter)
        self.splitter.setOrientation(Qt.Vertical)

        self.setWindowTitle("Classy nodes")

    @Slot()
    def open_file(self):
        last_dir = self.settings.value("last_dir")
        if last_dir is None:
            last_dir = ''
        # noinspection PyCallByClass
        file_path = QFileDialog.getOpenFileName(self, "Select tweakdb file", last_dir, "*.tweak")

        if file_path[0]:
            tweak_file = file_path[0]
            self.settings.setValue("last_dir", os.path.dirname(tweak_file))
        else:
            return

        try:
            self._process_db_file(file_path[0])
        except Exception as e:
            # noinspection PyCallByClass
            QMessageBox.critical(self, "Error", "Error while loading {0}: {1}".format(file_path, str(e)))
        self.setWindowTitle("Classy nodes - {0}".format(file_path[0]))

    @Slot(str)
    def log(self, value):
        self.log_window.appendPlainText(str(value))
        self.log_window.verticalScrollBar().scroll(0, self.log_window.verticalScrollBar().maximum())

    def _process_db_file(self, file_path):

        class TweakClass(object):
            def __init__(self, name, base=""):
                self.name = name
                self.base = base

                self.transitions_to = []
                self.transitions_conditions = []

            def has_transition(self, name):
                return name in self.transitions_to

            def transition_conditional(self, name):
                if len(self.transitions_to) != len(self.transitions_conditions):
                    raise ValueError("Transitions length does not match conditions length in {0}".format(self.name))

                if name not in name:
                    raise ValueError("Class {0} has no transition to {1}".format(self.name, name))

                return self.transitions_conditions[self.transitions_to.index(name)]

        with open(file_path, "r") as f:
            contents = f.read()

        lines = contents.split("\n")

        is_in_class = False
        is_class_declared = False
        current_class = None

        classes = {}
        parsed_line = 0
        for line in lines:
            parsed_line += 1
            if line.startswith("package"):
                continue

            if line.startswith("using"):
                continue

            if not line.strip():
                continue

            if line.startswith("//"):
                continue

            if not is_in_class and not is_class_declared:
                if line.find("=") > 0:  # static variable
                    continue

                spl = [x.strip() for x in line.strip().split(":")]

                if len(spl) == 1:
                    c = TweakClass(spl[0])
                else:
                    c = TweakClass(spl[0], spl[1])

                is_class_declared = True
                current_class = c
                classes[c.name] = c
                continue

            if not is_in_class and not line.find("{") >= 0:
                raise ValueError("Failed to parse the file {0} in line: {1}".format(file_path, parsed_line))
            else:
                is_in_class = True

            if line.find("}") >= 0:
                is_in_class = False
                is_class_declared = False
                continue

            if re.match(".+transitionTo( +||\t+)+=( +||\t+)+\[.+\]$", line.strip()):

                spl = line.split("=")[1].strip()[1:-1]
                transitions = [x.strip().strip("\"") for x in spl.split(",")]
                current_class.transitions_to = transitions
                continue

            if re.match(".+transitionCondition( +||\t+)+=( +||\t+)+\[.+\]$", line.strip()):
                spl = "=".join(line.split("=")[1:]).strip()[1:-1]
                transitions = [x.strip().strip("\"") for x in spl.split(",")]
                current_class.transitions_conditions = [True if x.strip() == '=' else False for x in transitions]
                continue

        self.scene.clear()

        # --- Create nodes
        for node_key in classes:
            # g.add_node(str(node_key),
            #            shape_fill="#aaaa33",
            #            shape="roundrectangle",
            #            font_style="bolditalic",
            #            label=classes.get(node_key).name)
            self.scene.add_node(node_key)

        edges_created = []
        # --- Create edges
        for node_key in classes:
            # --- Get each node
            current_node = classes.get(node_key)
            # --- Iterate it's "transition_to" list
            for t in current_node.transitions_to:
                # --- Find node to create transition edge to
                transition_to_node = classes.get(t)
                if transition_to_node is None:
                    self.log("Invalid transition in class {0} -> {1}".format(node_key, t))
                    continue

                # --- Check if it's a two way transition
                two_way = False
                if transition_to_node.has_transition(node_key):
                    two_way = True

                # --- make sure that these edges were not created yet
                edges_to_create = ["{0}!@#{1}".format(node_key, t)]
                if two_way:
                    edges_to_create = ["{0}!@#{1}".format(t, node_key)]

                edge_already_created = False
                for e in edges_to_create:
                    if e in edges_created:
                        edge_already_created = True
                        break
                if edge_already_created:
                    continue

                # --- Check if the transitions are conditional or not
                try:
                    conditional_to = current_node.transition_conditional(t)
                except ValueError as e:
                    self.log(str(e))
                    continue

                conditional_from = False

                if two_way:
                    conditional_from = transition_to_node.transition_conditional(node_key)

                self.scene.add_edge(current_node.name, transition_to_node.name,
                                    conditional_to=conditional_to, two_way=two_way, conditional_from=conditional_from)

                edges_created += edges_to_create

        self.scene.layout_nodes()

