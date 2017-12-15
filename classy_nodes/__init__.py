from PySide.QtGui import QApplication
from app import ClassyWidget


application = QApplication([])
c = ClassyWidget()
c.show()
application.exec_()
