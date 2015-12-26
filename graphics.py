from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
import numpy as np
from vispy.util.transforms import *
from util import look_at, normalize
import math

class MouseState:
    def __init__(self):
        self.left_button = False
        self.middle_button = False
        self.right_button = False
        self.x = 0
        self.y = 0

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 10
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
        print(np.linalg.norm([self.x, self.z]))

    def go_up(self, dist=0.1):
        perpendicular = normalize([])

class Window:
    def __init__(self, scene, width=1366, height=768):
        self.scene = scene
        self.width = width
        self.height = height
        self.camera = Camera()

        # init window and context
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_ALPHA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow('Chess Game')
        glutDisplayFunc(self.draw)
        glutMouseFunc(self.onclick)
        glutMotionFunc(self.onmouse)
        glutPassiveMotionFunc(self.onmouse)
        glutKeyboardFunc(self.onkeyboard)
        self.mouse = MouseState()
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
        self.scene = scene
        self.vertices = {}
        self.normals = {}
        for name, geo in self.scene.items():
            vertices = []
            normals = []
            for prim in geo.primitives:
                vertices.extend(prim.vertex[prim.vertex_index])
                normals.extend(prim.normal[prim.normal_index])
            self.vertices[name] = vbo.VBO(np.concatenate((np.array(vertices)[:,[0,2,1]], np.array(normals)[:,[0,2,1]]), axis=1))
            # self.normals[name] = vbo.VBO(np.array(normals))

        self.view_matrix_location = glGetUniformLocation(self.program, 'u_view')
        self.position_location = glGetAttribLocation( self.program, 'a_position' )
        self.normal_location = glGetAttribLocation(self.program, 'a_normal')

        # start main loop
        glutMainLoop()

    def _projection_matrix(self):
        return perspective(90, self.width/self.height, 0.1, 100)
        # return ortho(-10, 10, -10, 10, 0, 10)

    def _view_matrix(self):
        return look_at((self.camera.x, self.camera.y, self.camera.z), (0,0,0), (0,1,0))

    def onclick(self, button, state, x, y):
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

    def onmouse(self, x, y):
        smooth_factor = 5
        if self.mouse.left_button == True:
            dx = (x - self.mouse.x)/smooth_factor
            dy = (y - self.mouse.y)/smooth_factor
            self.camera.go_right(dx)
            self.camera.go_up(dy)
        self.mouse.x = x
        self.mouse.y = y

    def onkeyboard(self, key, x, y):
        if key == b'a':
            self.camera.x -= 0.1
        elif key == b'e':
            self.camera.x += 0.1
        elif key == b'z':
            self.camera.y += 0.1
        elif key == b's':
            self.camera.y -= 0.1
        elif key == b'q':
            self.camera.z += 0.1
        elif key == b'd':
            self.camera.z -= 0.1
        print(self.camera.x, self.camera.y, self.camera.z)


    def _draw(self, name):
        vertex = self.vertices[name]
        # normal = self.normals[name]
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
        self._draw('BlackKnight')
        shaders.glUseProgram(0)

        glutSwapBuffers()