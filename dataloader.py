from collada import *

class Mesh:
    def __init__(self, geo):
        self.vertices = vertices
        self.normals = normals
        self.texcoord = texcoord
        self.texture = texture

data = Collada('data/chessboard+man.dae')

geometries = data.geometries

scene = {}
scene['board'] = geometries[16]