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

def load_shaders(vert, frag):
    VERTEX_SHADER = shaders.compileShader(open(vert).read(), GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader(open(frag).read(), GL_FRAGMENT_SHADER)
    return shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)


class MainProgram:
    def __init__(self, vertex_shader = 'shaders/obj.vs', fragment_shader = 'shaders/obj.fs'):
        self.program = load_shaders(vertex_shader, fragment_shader)

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

    def __enter__(self):
        shaders.glUseProgram(self.program)

    def __exit__(self, exc_type, exc_value, traceback):
        shaders.glUseProgram(0)

    def set_projection_matrix(self, matrix):
        with self:
            glUniformMatrix4fv(self.projection_matrix_location, 1, GL_FALSE, matrix)

    def set_view_matrix(self, matrix):
        with self:
            glUniformMatrix4fv(self.view_matrix_location, 1, GL_FALSE, matrix)

    def set_light(self, light):
        with self:
            glUniform3fv(self.light_position_location, 1, light.position)
            glUniform4fv(self.light_intensities_location, 1, light.intensities)

    def set_camera(self, camera):
        with self:
            glUniform3fv(self.camera_position_location, 1, camera.position)

    def draw(self, vbo, model, effect):
        glUniform4fv(self.diffuse_location, 1, effect.diffuse)
        glUniform4fv(self.ambient_location, 1, effect.ambient)
        glUniform4fv(self.specular_location, 1, effect.specular)
        glUniform1f(self.shininess_location, effect.shininess)
        glUniform1f(self.index_of_refraction_location, effect.index_of_refraction)
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

        VERTEX_SHADER = shaders.compileShader(open('shaders/texture.vs').read(), GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(open('shaders/texture.fs').read(), GL_FRAGMENT_SHADER)
        self.program_texture = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        # load VBOs
        self.VBOs = defaultdict(lambda: [])
        for name, geo in self.geometries.items():
            for i in range(len(geo.vertices)):
                vertices = geo.vertices[i]
                normals = geo.normals[i]
                self.VBOs[name].append(vbo.VBO(np.concatenate((np.array(vertices), np.array(normals)), axis=1)))

        self.all_cube = vbo.VBO(np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]], dtype=np.float32))

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glEnable(GL_DEPTH_TEST)

        # self.fbo, self.texture, self.depth = self.create_fbo()
        self.main_program = MainProgram()

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

    def create_fbo(self):
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        texture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width(), self.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        depth = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depth)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width(), self.height())

        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth)

        glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])

        self.unbind_fbo()

        return fbo, texture, depth

    def bind_fbo(self, fbo, texture, depth):
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    def unbind_fbo(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _draw_texture(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shaders.glUseProgram(self.program_texture)
        texture_location = glGetUniformLocation(self.program_texture, 'u_texture')
        position_location = glGetAttribLocation(self.program_texture, 'a_position')
        # glUniform1i(texture_location, self.texture)
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glUniform1i(texture_location, 0);
        try:
            self.all_cube.bind()
            try:
                glEnableVertexAttribArray(position_location)
                glVertexAttribPointer(position_location, 2, GL_FLOAT, False, 8, self.all_cube)
                glDrawArrays(GL_QUADS, 0, len(self.all_cube))
            finally:
                glDisableVertexAttribArray(position_location)
        finally:
            self.all_cube.unbind()
        shaders.glUseProgram(0)

    def draw_scene_object(self, name, position=[0,0]):
        vbos = self.VBOs[name]
        geo = self.geometries[name]
        for i in range(len(vbos)):
            vbo = vbos[i]
            effect = geo.materials[i].effect
            model = self._model_matrix(geo, position)
            self.main_program.draw(vbo, model, effect)


    def paintGL(self):
        # self.bind_fbo(self.fbo, self.texture, self.depth)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.main_program.set_view_matrix(self._view_matrix())
        self.main_program.set_light(self.light)
        self.main_program.set_camera(self.camera)

        with self.main_program:
            self.draw_scene_object('Chessboard')
            for cell in self.board:
                if isinstance(cell, King):
                    if cell.color == Color.WHITE:
                        name = 'WhiteKing'
                    else:
                        name = 'BlackKing'
                elif isinstance(cell, Queen):
                    if cell.color == Color.WHITE:
                        name = 'WhiteQueen'
                    else:
                        name = 'BlackQueen'
                elif isinstance(cell, Bishop):
                    if cell.color == Color.WHITE:
                        name = 'WhiteBishop'
                    else:
                        name = 'BlackBishop'
                elif isinstance(cell, Knight):
                    if cell.color == Color.WHITE:
                        name = 'WhiteKnight'
                    else:
                        name = 'BlackKnight'
                elif isinstance(cell, Rook):
                    if cell.color == Color.WHITE:
                        name = 'WhiteRook'
                    else:
                        name = 'BlackRook'
                elif isinstance(cell, Pawn):
                    if cell.color == Color.WHITE:
                        name = 'WhitePawn'
                    else:
                        name = 'BlackPawn'
                self.draw_scene_object(name, cell.position)
        # self.unbind_fbo()

        # self._draw_texture()

    def resizeGL(self, x, y):
        # projection matrix
        self.adjustSize()
        self.main_program.set_projection_matrix(self._projection_matrix())

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
