import os
import re

from PySide.QtGui import QWidget, QMessageBox
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QMenuBar
from PySide.QtGui import QMenu
from PySide.QtGui import QFileDialog
from PySide.QtGui import QAction

from PySide.QtCore import Slot, SIGNAL
from PySide.QtCore import QSettings


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
        # self.scene.add_node('node1')
        # self.scene.add_node('node2')
        # self.scene.add_node('node3')
        # self.scene.add_node('node4')
        # self.scene.add_node('node5')
        # self.scene.add_node('node6')
        # self.scene.add_node('node7')
        #
        # self.scene.add_edge('node1', 'node3', conditional_to=True)
        #
        # self.scene.add_edge('node1', 'node2')
        #
        # self.scene.add_edge('node1', 'node5')
        #
        # self.scene.add_edge('node4', 'node6', two_way=True, conditional_to=True, conditional_from=False)

    @Slot()
    def open_file(self):
        last_dir = self.settings.value("last_dir")
        if last_dir is None:
            last_dir = ''
        file_path = QFileDialog.getOpenFileName(self, "Select tweakdb file", last_dir, "*.tweak")

        if file_path[0]:
            tweak_file = file_path[0]
            self.settings.setValue("last_dir", os.path.dirname(tweak_file))
        else:
            return

        self._process_db_file(file_path[0])
        try:
            pass
        except Exception as e:
            # noinspection PyCallByClass
            QMessageBox.critical(self, "Error", "Error while loading {0}: {1}".format(file_path, str(e)))

    def _process_db_file(self, file_path):

        class TweakClass(object):
            def __init__(self, name, base=""):
                self.name = name
                self.base = base

                self.transitions_to = []
                self.transitions_conditions = []

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
                spl = line.split("=")[1].strip()[1:-1]

                transitions = [x.strip().strip("\"") for x in spl.split(",")]
                current_class.transitions_conditions = [True if x.strip() == 'true' else False for x in transitions]
                print current_class.transitions_conditions

        self.scene.clear()

        for node_key in classes:
            # g.add_node(str(node_key),
            #            shape_fill="#aaaa33",
            #            shape="roundrectangle",
            #            font_style="bolditalic",
            #            label=classes.get(node_key).name)
            self.scene.add_node(node_key)

        for node_key in classes:
            print node_key
            for t in classes.get(node_key).transitions_to:
                if len(classes.get(node_key).transitions_conditions) == len(classes.get(node_key).transitions_to):
                    label = str(
                        classes.get(node_key).transitions_conditions[classes.get(node_key).transitions_to.index(t)])
                    print label
                    self.scene.add_edge(str(node_key), str(t))
                else:
                    self.scene.add_edge(str(node_key), str(t))

