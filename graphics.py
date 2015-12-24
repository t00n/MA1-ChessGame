from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
import numpy as np
from vispy.util.transforms import *

class Window:
    def __init__(self, scene, width=1366, height=768):
        self.scene = scene
        self.width = width
        self.height = height

        # init window and context
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_ALPHA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow('Chess Game')
        glutDisplayFunc(self.draw)
        # glutIdleFunc(self.draw)

        # init scene
        VERTEX_SHADER = shaders.compileShader(open('shaders/obj.vs').read(), GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader(open('shaders/obj.fs').read(), GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
        # shaders.glUseProgram(self.program)
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
        return perspective(self.height, self.width/self.height, 1, 100)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shaders.glUseProgram(self.program)
        projection_matrix_location = glGetUniformLocation(self.program, 'u_projection')
        matrix = self._projection_matrix()
        glUniformMatrix4fv(projection_matrix_location, 1, GL_TRUE, matrix)
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