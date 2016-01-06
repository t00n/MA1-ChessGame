from collada import *
from collada.scene import GeometryNode
import numpy as np

def get_material(symbol):
    for mat in data.materials:
        if mat.id == symbol:
            return mat
    return None

def get_effect(id):
    for effect in data.effects:
        if effect.id == id:
            return effect
    return None

class Material:
    def __init__(self, mat):
        self.effect = get_effect(mat.effect.id)
        
class Geometry:
    def __init__(self, geo):
        self.vertices = []
        self.normals = []
        self.materials = []
        for prim in geo.primitives:
            self.vertices.append(prim.vertex[prim.vertex_index][:,[0,2,1]])
            self.normals.append(prim.normal[prim.normal_index][:,[0,2,1]])
            self.materials.append(Material(get_material(prim.material)))
        self.translation = np.array([-21, 0, -18], dtype=np.float32) # translate to world origin
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scaling = np.array([1, 1, 1], dtype=np.float32)

# Load all geometries from Collada and put them in our own structure. Load materials and effects too
data = Collada('data/chessboard+man.dae')
geometries = {}
for i, node in enumerate(data.scene.nodes):
    for child in node.children:
        if isinstance(child, GeometryNode):
            name = "".join(node.id.split('_')[:2])
            geometries[name] = Geometry(child.geometry)

# Adjust some specific things
geometries['Chessboard'].translation = np.array([0, -15, 0])
