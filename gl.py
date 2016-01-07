from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
import numpy as np
from vispy.util.transforms import *
from collections import defaultdict
from functools import reduce
from util import look_at
from gl_component import Mouse, Light, Camera, Animation

from chess import King, Queen, Bishop, Knight, Rook, Pawn, Color

def load_shaders(vert, frag):
    VERTEX_SHADER = shaders.compileShader(open('shaders/' + vert).read(), GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader(open('shaders/' + frag).read(), GL_FRAGMENT_SHADER)
    return shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)


class Program:
    def __enter__(self):
        shaders.glUseProgram(self.program)

    def __exit__(self, exc_type, exc_value, traceback):
        shaders.glUseProgram(0)

class MainProgram(Program):
    def __init__(self, vertex_shader = 'obj.vs', fragment_shader = 'obj.fs'):
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

class TextureProgram(Program):
    def __init__(self):
        self.program = load_shaders('texture.vs', 'texture.fs')
        self.square = vbo.VBO(np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]], dtype=np.float32))

        self.texture_location = glGetUniformLocation(self.program, 'u_texture')
        self.position_location = glGetAttribLocation(self.program, 'a_position')
        self.width_location = glGetUniformLocation(self.program, 'u_width')
        self.height_location = glGetUniformLocation(self.program, 'u_height')

    def draw(self, texture):
        shaders.glUseProgram(self.program)
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, texture);
        glUniform1i(self.texture_location, 0);
        try:
            self.square.bind()
            try:
                glEnableVertexAttribArray(self.position_location)
                glVertexAttribPointer(self.position_location, 2, GL_FLOAT, False, 8, self.square)
                glDrawArrays(GL_QUADS, 0, len(self.square))
            finally:
                glDisableVertexAttribArray(self.position_location)
        finally:
            self.square.unbind()
        shaders.glUseProgram(0)

    def resize(self, width, height):
        with self:
            glUniform1f(self.width_location, width)
            glUniform1f(self.height_location, height)


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

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glEnable(GL_DEPTH_TEST)

        self.fbo, self.texture, self.depth = self.create_fbo()
        self.main_program = MainProgram()
        self.texture_program = TextureProgram()

        self.animations = [Animation(self.board.board[0][0], [7,0])]

        QTimer.singleShot(0, self.update)

    def paintGL(self):
        # self.bind_fbo(self.fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._draw_scene(self.main_program)
        # self.unbind_fbo()

        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # self.texture_program.draw(self.texture)

    def resizeGL(self, width, height):
        # projection matrix
        glViewport(0, 0, self.width(), self.height())
        self.main_program.set_projection_matrix(self._projection_matrix())
        self.texture_program.resize(width, height)

    def mousePressEvent(self, event):
        self.mouse.x = event.pos().x()
        self.mouse.y = event.pos().y()
        glReadBuffer(GL_BACK)
        z = glReadPixels(self.mouse.x, self.mouse.y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        self._detect_collision(self.mouse.x, self.mouse.y, z)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.camera.go_right(event.pos().x() - self.mouse.x)
            self.camera.go_up(event.pos().y() - self.mouse.y)
            self.updateGL()

        self.mouse.x = event.pos().x()
        self.mouse.y = event.pos().y()

    def update(self):
        try:
            for i in range(len(self.animations)):
                anim = self.animations[i]
                if anim.update():
                    del self.animations[i]
            self.updateGL()
        finally:
            QTimer.singleShot(0, self.update)

    def _detect_collision(self, x, y, z):
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

    def _projection_matrix(self):
        return perspective(45, self.width()/self.height(), 0.1, 100)
        # return ortho(-50, 50, -50, 50, 0, 100)

    def _view_matrix(self):
        return look_at(self.camera.position, self.camera.direction, (0,1,0))

    def _model_matrix(self, geo, position):
        return reduce(np.dot, [scale(geo.scaling),
                               rotate(geo.rotation[0], [1, 0, 0]),
                               rotate(geo.rotation[1], [0, 1, 0]),
                               rotate(geo.rotation[2], [0, 0, 1]),
                               translate(geo.translation),
                               translate([(position[0])*4, 0, (position[1])*4])])

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

    def bind_fbo(self, fbo):
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    def unbind_fbo(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _draw_scene_object(self, program, name, position=[0,0]):
        vbos = self.VBOs[name]
        geo = self.geometries[name]
        for i in range(len(vbos)):
            vbo = vbos[i]
            effect = geo.materials[i].effect
            model = self._model_matrix(geo, position)
            program.draw(vbo, model, effect)

    def _draw_scene(self, program):
        program.set_view_matrix(self._view_matrix())
        program.set_light(self.light)
        program.set_camera(self.camera)

        with program:
            self._draw_scene_object(program, 'Chessboard')
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
                self._draw_scene_object(program, name, cell.position)
