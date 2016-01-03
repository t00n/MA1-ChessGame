from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
import numpy as np
from vispy.util.transforms import *
from util import look_at, normalize
import math

from chess import King, Queen, Bishop, Knight, Rook, Pawn, Color

class Mouse:
    def __init__(self):
        self.left_button = False
        self.middle_button = False
        self.right_button = False
        self.x = 0
        self.y = 0

class Camera:
    def __init__(self):
        self.x = 20
        self.y = 20
        self.z = 20

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

class Light:
    def __init__(self):
        self.x = 10
        self.y = 10
        self.z = 0

    @property
    def position(self):
        return [self.x, self.y, self.z]

class Window:
    def __init__(self, geometries, board, width=1366, height=768):
        self.board = board
        self.width = width
        self.height = height
        self.camera = Camera()
        self.light = Light()

        # init window and context
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_ALPHA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow('Chess Game')
        self.mouse = Mouse()
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
        self.VBOs = {}
        for name, geo in geometries.items():
            self.VBOs[name] = vbo.VBO(np.concatenate((np.array(geo.vertices), np.array(geo.normals)), axis=1))

        # get variables location
        self.view_matrix_location = glGetUniformLocation(self.program, 'u_view')
        self.model_matrix_location = glGetUniformLocation(self.program, 'u_model')
        self.light_position_location = glGetUniformLocation(self.program, 'u_light_position')
        self.position_location = glGetAttribLocation( self.program, 'a_position' )
        self.normal_location = glGetAttribLocation(self.program, 'a_normal')

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glEnable(GL_DEPTH_TEST)

        glutMainLoop()

    def _projection_matrix(self):
        return perspective(60, self.width/self.height, 0.1, 100)
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

    def _draw(self, name, position=(0,0), y=0):
        vertex = self.VBOs[name]
        model = translate([(position[0]-4)*5, y*5, (position[1]-4)*5])
        glUniformMatrix4fv(self.model_matrix_location, 1, GL_FALSE, model)
        try:
            vertex.bind()
            try:
                glEnableVertexAttribArray(self.position_location)
                glEnableVertexAttribArray(self.normal_location)
                glVertexAttribPointer(self.position_location, 3, GL_FLOAT, False, 24, vertex)
                glVertexAttribPointer(self.normal_location, 3, GL_FLOAT, False, 24, vertex+12)
                glDrawArrays(GL_TRIANGLES, 0, len(vertex))
            finally:
                glDisableVertexAttribArray(self.normal_location)
                glDisableVertexAttribArray(self.position_location)
        finally:
            vertex.unbind()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shaders.glUseProgram(self.program)
        glUniformMatrix4fv(self.view_matrix_location, 1, GL_FALSE, self._view_matrix())
        glUniform3fv(self.light_position_location, 1, self.light.position)
        self._draw('Chessboard', y=-5)
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