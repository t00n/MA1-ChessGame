from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *

from gl import *

class LightSlider(QSlider):
    def __init__(self, min_val, max_val, callback, gl):
        super(LightSlider, self).__init__(Qt.Horizontal)
        self.setMinimum(min_val)
        self.setMaximum(max_val)
        self.callback = callback
        self.valueChanged.connect(self.valueChangedSlot)
        self.gl = gl

    def valueChangedSlot(self, val):
        self.callback(val)
        self.gl.updateGL()

class Window(QMainWindow):
    def __init__(self, geometries, board, width=1366, height=768):
        super(Window, self).__init__()
        self.setWindowTitle("Chess Game")
        self.resize(QDesktopWidget().availableGeometry(self).size())

        self.gl_widget = GLWidget(geometries, board, self)
        self.gl_widget.setMinimumSize(800, 600)
        self.gl_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.x_slider = LightSlider(-50, 50, self.gl_widget.light.set_x, self.gl_widget)
        self.x_slider.setValue(self.gl_widget.light.x)
        self.y_slider = LightSlider(0, 50, self.gl_widget.light.set_y, self.gl_widget)
        self.y_slider.setValue(self.gl_widget.light.y)
        self.z_slider = LightSlider(-50, 50, self.gl_widget.light.set_z, self.gl_widget)
        self.z_slider.setValue(self.gl_widget.light.z)
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.x_slider)
        self.left_layout.addWidget(self.y_slider)
        self.left_layout.addWidget(self.z_slider)
        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_layout)

        self.R_slider = LightSlider(0, 255, self.gl_widget.light.set_R, self.gl_widget)
        self.R_slider.setValue(self.gl_widget.light.intensities[0]*255)
        self.G_slider = LightSlider(0, 255, self.gl_widget.light.set_G, self.gl_widget)
        self.G_slider.setValue(self.gl_widget.light.intensities[1]*255)
        self.B_slider = LightSlider(0, 255, self.gl_widget.light.set_B, self.gl_widget)
        self.B_slider.setValue(self.gl_widget.light.intensities[2]*255)
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.R_slider)
        self.right_layout.addWidget(self.G_slider)
        self.right_layout.addWidget(self.B_slider)
        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.left_widget)
        self.top_layout.addWidget(self.right_widget)
        self.top_widget = QWidget()
        self.top_widget.setLayout(self.top_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.top_widget)
        self.main_layout.addWidget(self.gl_widget)
        self.main_layout.addStretch(0.2)
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)