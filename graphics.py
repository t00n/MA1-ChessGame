from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
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

class Window:
    def __init__(self, geometries, board, width=1366, height=768):
        self.board = board
        self.width = width
        self.height = height
        self.camera = Camera()
        self.light = Light()
        self.geometries = geometries

        # init window and context
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_ALPHA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow('Chess Game')
        self.mouse = Mouse()
        glClearColor(0.5, 0.5, 1.0, 1.0)
        glutMouseFunc(self._onclick)
        glutMotionFunc(self._onmouse)
        glutPassiveMotionFunc(self._onmouse)
        glutKeyboardFunc(self._onkeyboard)
        glutDisplayFunc(self.draw)
        glutIdleFunc(self.draw)

        # load shaders
        VERTEX_SHADER = shaders.compileShader(open('shaders/obj.vs').read(), GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(open('shaders/obj.fs').read(), GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        # projection matrix
        shaders.glUseProgram(self.program)
        projection_matrix_location = glGetUniformLocation(self.program, 'u_projection')
        glUniformMatrix4fv(projection_matrix_location, 1, GL_FALSE, self._projection_matrix())
        shaders.glUseProgram(0)

        # load VBOs
        self.VBOs = defaultdict(lambda: [])
        for name, geo in geometries.items():
            for i in range(len(geo.vertices)):
                vertices = geo.vertices[i]
                normals = geo.normals[i]
                self.VBOs[name].append(vbo.VBO(np.concatenate((np.array(vertices), np.array(normals)), axis=1)))

        # get variables location
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

        glutMainLoop()

    def _projection_matrix(self):
        return perspective(45, self.width/self.height, 0.1, 100)
        # return ortho(-10, 10, -10, 10, 0, 10)

    def _view_matrix(self):
        return look_at((self.camera.x, self.camera.y, self.camera.z), (0,0,0), (0,1,0))

    def _onclick(self, button, state, x, y):
        if state == GLUT_DOWN:
            if button == GLUT_LEFT_BUTTON:
                self.mouse.left_button = True
            elif button == GLUT_MIDDLE_BUTTON:
                self.mouse.middle_button = True
            elif button == GLUT_RIGHT_BUTTON:
                self.mouse.right_button = True
        elif state == GLUT_UP:
            if button == GLUT_LEFT_BUTTON:
                self.mouse.left_button = False
            elif button == GLUT_MIDDLE_BUTTON:
                self.mouse.middle_button = False
            elif button == GLUT_RIGHT_BUTTON:
                self.mouse.right_button = False
        self.mouse.x = x
        self.mouse.y = y

    def _onmouse(self, x, y):
        smooth_factor = 5
        if self.mouse.left_button == True:
            dx = (x - self.mouse.x)/smooth_factor
            dy = (y - self.mouse.y)/smooth_factor
            self.camera.go_right(dx)
            self.camera.go_up(dy)
        self.mouse.x = x
        self.mouse.y = y

    def _onkeyboard(self, key, x, y):
        step = 0.5
        if key == b'q':
            self.camera.x += step
        elif key == b'd':
            self.camera.x -= step
        elif key == b'z':
            self.camera.y += step
        elif key == b's':
            self.camera.y -= step
        elif key == b'a':
            self.camera.z += step
        elif key == b'e':
            self.camera.z -= step

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
            model = reduce(np.dot, [translate([(position[0])*6, 0, (position[1])*6]),
                                    translate(geo.translation),
                                    rotate(geo.rotation[2], [0, 0, 1]),
                                    rotate(geo.rotation[1], [0, 1, 0]),
                                    rotate(geo.rotation[0], [1, 0, 0]),
                                    scale(geo.scaling)])
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

    def draw(self):
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

        glutSwapBuffers()