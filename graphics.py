from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
import numpy as np
from vispy.util.transforms import *

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
        self.y = 0
        self.z = 0
        self.up = 0
        self.right = 0

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
        self.mouse = MouseState()
        # glutIdleFunc(self.draw)

        # load shaders
        VERTEX_SHADER = shaders.compileShader(open('shaders/obj.vs').read(), GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(open('shaders/obj.fs').read(), GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        # projection matrix
        shaders.glUseProgram(self.program)
        projection_matrix_location = glGetUniformLocation(self.program, 'u_projection')
        glUniformMatrix4fv(projection_matrix_location, 1, GL_TRUE, self._projection_matrix())
        shaders.glUseProgram(0)

        # load VBOs
        self.vbos = []
        self.objects = []
        for obj in scene:
            vertices = []
            for poly in obj:
                vertices.extend(poly.vertices)
            self.vbos.append(vbo.VBO(np.array(vertices)))
            self.objects.append(obj)

        # start main loop
        glutMainLoop()

    def _projection_matrix(self):
        # return perspective(self.height, self.width/self.height, 1, 100)
        return ortho(-10, 10, -10, 10, 0, 100)

    def _view_matrix(self):
        return rotate(self.camera.up, (1,0,0)) * rotate(self.camera.right, (0,1,0)) * translate((0,0,-500))

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
        smooth_factor = 10
        if self.mouse.left_button == True:
            self.camera.up += (x - self.mouse.x)/smooth_factor
            self.camera.right += (y - self.mouse.y)/smooth_factor
        self.mouse.x = x
        self.mouse.y = y


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shaders.glUseProgram(self.program)
        view_matrix_location = glGetUniformLocation(self.program, 'u_view')
        glUniformMatrix4fv(view_matrix_location, 1, GL_TRUE, self._view_matrix())
        for i, vbo in enumerate(self.vbos):
            try:
                vbo.bind()
                try:
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glVertexPointerf(vbo)
                    glDrawArrays(GL_TRIANGLES, 0, sum([len(obj.vertices) for obj in self.objects[i]]))
                finally:
                    glDisableClientState(GL_VERTEX_ARRAY)
            finally:
                vbo.unbind()
        shaders.glUseProgram(0)


        glutSwapBuffers()
        glutPostRedisplay();