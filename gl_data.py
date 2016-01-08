from collada import *
from collada.scene import GeometryNode
import numpy as np

class Material:
    def __init__(self, mat):
        self.effect = mat.effect
        
class Geometry:
    def __init__(self, geo):
        self.vertices = []
        self.normals = []
        self.materials = []
        for prim in geo.primitives():
            self.vertices.append(prim.vertex[prim.vertex_index][:,[0,2,1]])
            self.normals.append(prim.normal[prim.normal_index][:,[0,2,1]])
            self.materials.append(Material(prim.material))
        self.translation = np.array([0, 0, 0], dtype=np.float32) # translate to world origin
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scaling = np.array([1, 1, 1], dtype=np.float32)

# Load all geometries from Collada and put them in our own structure. Load materials and effects too
data = Collada('data/chessboard+man.dae')
geometries = {}
for i, node in enumerate(data.scene.nodes):
    for geo in node.objects('geometry'):
        name = "".join(node.id.split('_')[:2])
        geometries[name] = Geometry(geo)

geometries['Chessboard'].normals = []
board = data.scene.nodes[19].children[0].geometry
for prim in board.primitives:
    geometries['Chessboard'].normals.append(prim.normal[prim.normal_index][:,[0,2,1]])


# Adjust some specific things
geometries['Chessboard'].scaling = np.array([1.5, 1, 1.5])
for key, geo in geometries.items():
    if key != 'Chessboard':
        geo.translation = np.array([-14,0,-13.5])
