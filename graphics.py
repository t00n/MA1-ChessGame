from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLU import gluUnProject
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4 import QtCore
import numpy as np
from vispy.util.transforms import *
from util import look_at, normalize
import math
from collections import defaultdict
from functools import reduce

from chess import King, Queen, Bishop, Knight, Rook, Pawn, Color

class MixinHasPosition:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y 
        self.z = z

    @property
    def position(self):
        return [self.x, self.y, self.z]

class MixinHasDirection:
    def __init__(self, x, y, z):
        self.dir_x = x
        self.dir_y = y
        self.dir_z = z

    @property
    def direction(self):
        return [self.dir_x, self.dir_y, self.dir_z]

class Mouse:
    def __init__(self):
        self.left_button = False
        self.middle_button = False
        self.right_button = False
        self.x = 0
        self.y = 0

class Camera(MixinHasPosition):
    def __init__(self):
        super(Camera, self).__init__(0,40,-40)

    # camera always looks to origin (0,0,0)
    @property
    def direction(self):
        return (-self.x, -self.y, -self.z)

    def go_right(self, dist=0.1):
        perpendicular = normalize([-self.z, self.x])
        previous_norm = np.linalg.norm([self.x, self.z])
        self.x += perpendicular[0] * dist
        self.z += perpendicular[1] * dist
        new_norm = np.linalg.norm([self.x, self.z])
        self.x *= previous_norm / new_norm
        self.z *= previous_norm / new_norm

    def go_up(self, dist=0.1):
        direction = normalize(self.direction)
        previous_norm = np.linalg.norm([self.x, self.y, self.z])
        self.x += direction[0] * dist
        self.y += dist
        self.z += direction[2] * dist
        if self.y < 1:
            self.y = 1
        new_norm = np.linalg.norm([self.x, self.y, self.z])
        self.x *= previous_norm / new_norm
        self.y *= previous_norm / new_norm
        self.z *= previous_norm / new_norm

class Light(MixinHasPosition):
    def __init__(self):
        super(Light, self).__init__(0,20,0)
        self._intensities = [1,1,1,1]

    def intensities():
        doc = "The intensities of the lights."
        def fget(self):
            return self._intensities
        def fset(self, value):
            self._intensities = value
        def fdel(self):
            del self._intensities
        return locals()
    intensities = property(**intensities())

    def set_x(self, val):
        self.x = val

    def set_y(self, val):
        self.y = val

    def set_z(self, val):
        self.z = val

    def set_R(self, val):
        self._intensities[0] = val/255

    def set_G(self, val):
        self._intensities[1] = val/255

    def set_B(self, val):
        self._intensities[2] = val/255

class LightSlider(QSlider):
    def __init__(self, min_val, max_val, callback, gl):
        super(LightSlider, self).__init__(QtCore.Qt.Horizontal)
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

class GLWidget(QGLWidget):
    def __init__(self, geometries, board, parent):
        format = QGLFormat()
        format.setSampleBuffers(True)
        format.setSamples(8)
        super(GLWidget, self).__init__(format, parent)
        self.camera = Camera()
        self.light = Light()
        self.mouse = Mouse()
        self.geometries = geometries
        self.board = board

    def initializeGL(self):
        # init window and context
        glClearColor(0.5, 0.5, 1.0, 1.0)

        # load shaders
        VERTEX_SHADER = shaders.compileShader(open('shaders/obj.vs').read(), GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(open('shaders/obj.fs').read(), GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        # load VBOs
        self.VBOs = defaultdict(lambda: [])
        for name, geo in self.geometries.items():
            for i in range(len(geo.vertices)):
                vertices = geo.vertices[i]
                normals = geo.normals[i]
                self.VBOs[name].append(vbo.VBO(np.concatenate((np.array(vertices), np.array(normals)), axis=1)))

        # get variables location
        self.projection_matrix_location = glGetUniformLocation(self.program, 'u_projection')
        self.view_matrix_location = glGetUniformLocation(self.program, 'u_view')
        self.model_matrix_location = glGetUniformLocation(self.program, 'u_model')
        self.light_position_location = glGetUniformLocation(self.program, 'u_light_position')
        self.light_intensities_location = glGetUniformLocation(self.program, 'u_light_intensities')
        self.camera_position_location = glGetUniformLocation(self.program, 'u_camera_position')
        self.position_location = glGetAttribLocation( self.program, 'a_position' )
        self.normal_location = glGetAttribLocation(self.program, 'a_normal')
        self.diffuse_location = glGetUniformLocation(self.program, 'u_diffuse')
        self.ambient_location = glGetUniformLocation(self.program, 'u_ambient')
        self.specular_location = glGetUniformLocation(self.program, 'u_specular')
        self.shininess_location = glGetUniformLocation(self.program, 'u_shininess')
        self.index_of_refraction_location = glGetUniformLocation(self.program, 'u_index_of_refraction')

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glEnable(GL_DEPTH_TEST)

    def _draw(self, name, position=(0,0)):
        vbos = self.VBOs[name]
        geo = self.geometries[name]
        for i in range(len(vbos)):
            vbo = vbos[i]
            effect = geo.materials[i].effect
            glUniform4fv(self.diffuse_location, 1, effect.diffuse)
            glUniform4fv(self.ambient_location, 1, effect.ambient)
            glUniform4fv(self.specular_location, 1, effect.specular)
            glUniform1f(self.shininess_location, effect.shininess)
            glUniform1f(self.index_of_refraction_location, effect.index_of_refraction)
            model = self._model_matrix(geo, position)
            glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, model)
            try:
                vbo.bind()
                try:
                    glEnableVertexAttribArray(self.position_location)
                    glEnableVertexAttribArray(self.normal_location)
                    glVertexAttribPointer(self.position_location, 3, GL_FLOAT, False, 24, vbo)
                    glVertexAttribPointer(self.normal_location, 3, GL_FLOAT, False, 24, vbo+12)
                    glDrawArrays(GL_TRIANGLES, 0, len(vbo))
                finally:
                    glDisableVertexAttribArray(self.normal_location)
                    glDisableVertexAttribArray(self.position_location)
            finally:
                vbo.unbind()

    def _projection_matrix(self):
        return perspective(45, self.width()/self.height(), 0.1, 100)
        # return ortho(-50, 50, -50, 50, 0, 100)

    def _view_matrix(self):
        return look_at((self.camera.x, self.camera.y, self.camera.z), (0,0,0), (0,1,0))

    def _model_matrix(self, geo, position):
        return reduce(np.dot, [translate([(position[0])*6, 0, (position[1])*6]),
                                    translate(geo.translation),
                                    rotate(geo.rotation[2], [0, 0, 1]),
                                    rotate(geo.rotation[1], [0, 1, 0]),
                                    rotate(geo.rotation[0], [1, 0, 0]),
                                    scale(geo.scaling)])

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shaders.glUseProgram(self.program)
        glUniformMatrix4fv(self.view_matrix_location, 1, GL_FALSE, self._view_matrix())
        glUniform3fv(self.light_position_location, 1, self.light.position)
        glUniform4fv(self.light_intensities_location, 1, self.light.intensities)
        glUniform3fv(self.camera_position_location, 1, self.camera.position)
        self._draw('Chessboard')
        for cell in self.board:
            if isinstance(cell, King):
                if cell.color == Color.WHITE:
                    self._draw('WhiteKing', cell.position)
                else:
                    self._draw('BlackKing', cell.position)
            elif isinstance(cell, Queen):
                if cell.color == Color.WHITE:
                    self._draw('WhiteQueen', cell.position)
                else:
                    self._draw('BlackQueen', cell.position)
            elif isinstance(cell, Bishop):
                if cell.color == Color.WHITE:
                    self._draw('WhiteBishop', cell.position)
                else:
                    self._draw('BlackBishop', cell.position)
            elif isinstance(cell, Knight):
                if cell.color == Color.WHITE:
                    self._draw('WhiteKnight', cell.position)
                else:
                    self._draw('BlackKnight', cell.position)
            elif isinstance(cell, Rook):
                if cell.color == Color.WHITE:
                    self._draw('WhiteRook', cell.position)
                else:
                    self._draw('BlackRook', cell.position)
            elif isinstance(cell, Pawn):
                if cell.color == Color.WHITE:
                    self._draw('WhitePawn', cell.position)
                else:
                    self._draw('BlackPawn', cell.position)
        shaders.glUseProgram(0)

    def resizeGL(self, x, y):
        # projection matrix
        self.adjustSize()
        shaders.glUseProgram(self.program)
        glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, self._projection_matrix())
        shaders.glUseProgram(0)

    def mousePressEvent(self, event):
        self.mouse.x = event.pos().x()
        self.mouse.y = event.pos().y()
        glReadBuffer(GL_BACK)
        z = glReadPixels(self.mouse.x, self.mouse.y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        self.detect_collision(self.mouse.x, self.mouse.y, z)

    def detect_collision(self, x, y, z):
        # normalize
        x = (2 * x) / self.width() - 1
        y = 1 - (2 * y) / self.height()
        z = 2 * z - 1
        position = np.array([x, y, z, 1])
        # print(position)
        world_to_cam = self._projection_matrix().dot(self._view_matrix())
        cam_to_world = np.linalg.inv(self._view_matrix()).dot(np.linalg.inv(self._projection_matrix()))
        position = cam_to_world.dot(position)
        # print(position)
        # position = [position[i] / position[3] for i in range(4)]
        # print(position)
        # position = np.linalg.inv(self._projection_matrix()).dot(position)
        position = np.array(list(map(lambda x: round(x, 3), position)))
        print(position)
        print()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.camera.go_right(event.pos().x() - self.mouse.x)
            self.camera.go_up(event.pos().y() - self.mouse.y)
            self.updateGL()

        self.mouse.x = event.pos().x()
        self.mouse.y = event.pos().y()
