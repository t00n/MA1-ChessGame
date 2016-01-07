from collada import *
from collada.scene import GeometryNode
import numpy as np
# from vispy.util.transforms import *

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

# Adjust some specific things
geometries['Chessboard'].scaling = np.array([1.5, 1, 1.5])
for key, geo in geometries.items():
    if key != 'Chessboard':
        geo.translation = np.array([-14,0,-13.5])
# print(geometries['Chessboard'].vertices)
# geometries['Chessboard'].vertices = np.apply_along_axis(lambda x: [x[0], x[1], x[2]], 2, geometries['Chessboard'].vertices)
# geometries['WhiteRook'].scaling = np.array([0.4,0.4,0.4])
# geometries['BlackRook'].scaling = np.array([0.4,0.4,0.4])
# geometries['WhiteKnight'].rotation = np.array([0,90,0])
# geometries['BlackKnight'].rotation = np.array([0,-90,0])
# geometries['WhiteKnight'].scaling = np.array([1.0, 0.8, 1.0])
# geometries['BlackKnight'].scaling = np.array([1.0, 0.8, 1.0])
# geometries['WhiteKing'].scaling = np.array([1.0, 1.4, 1.0])
# geometries['BlackKing'].scaling = np.array([1.0, 1.4, 1.0])
# geometries['WhiteQueen'].scaling = np.array([1.0, 1.2, 1.0])
# geometries['BlackQueen'].scaling = np.array([1.0, 1.2, 1.0])
# geometries['WhitePawn'].scaling = np.array([0.8, 0.8, 0.8])
# geometries['BlackPawn'].scaling = np.array([0.8, 0.8, 0.8])
# geometries['WhiteBishop'].scaling = np.array([1.0, 1.4, 1.0])
# geometries['BlackBisàhop'].scaling = np.array([1.0, 1.4, 1.0])
