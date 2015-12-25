from collada import *

class Mesh:
    def __init__(self, geo):
        self.vertices = vertices
        self.normals = normals
        self.texcoord = texcoord
        self.texture = texture

data = Collada('data/chessboard+man.dae')

geo = data.geometries[16]
poly = geo.primitives[0]

scene = []
scene.append(poly)
scene.append(geo.primitives[1])