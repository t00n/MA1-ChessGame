from collada import *
import numpy as np
from vispy.util.transforms import rotate
from util import normalize
import json

def compute_tangents(normals):
    tangents = np.zeros(shape=(len(normals), 3))
    bitangents = np.zeros(shape=(len(normals), 3))
    for i, normal in enumerate(normals):
        if normal[0] == 0 and normal[2] == 0:
            tangents[i] = normal[[0,2,1]]
        else:
            axis_x = normalize(np.array([normal[0], 0, normal[2]]))
            axis_y = np.array([0,1,0])
            axis_z = np.cross(axis_x, axis_y)
            rotation = rotate(-90, axis_z)
            tangents[i] = rotation.dot(np.append(normal, [0]))[:3]
            bitangents[i] = np.cross(normal, tangents[i])
    return tangents, bitangents

class dict(dict):
    def __init__(self, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class Material(dict):
    def __init__(self, mat):
        self.__dict__ = self
        effect = mat.effect
        self.diffuse = effect.diffuse
        self.ambient = effect.ambient
        self.index_of_refraction = effect.index_of_refraction
        self.specular = effect.specular
        self.shininess = effect.shininess
        
class Geometry(dict):
    def __init__(self, geo):
        self.__dict__ = self
        self.vertices = []
        self.normals = []
        self.tangents = []
        self.bitangents = []
        self.materials = []
        for prim in geo.primitives():
            self.vertices.append(prim.vertex[prim.vertex_index][:,[0,2,1]].tolist())
            self.normals.append(prim.normal[prim.normal_index][:,[0,2,1]])
            tangents, bitangents = compute_tangents(self.normals[-1])
            self.tangents.append(tangents.tolist())
            self.bitangents.append(bitangents.tolist())
            self.normals[-1] = self.normals[-1].tolist()
            self.materials.append(Material(prim.material))
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scaling = [1, 1, 1]

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
    geometries['Chessboard'].normals.append(prim.normal[prim.normal_index][:,[0,2,1]].tolist())

# Adjust some specific things
geometries['Chessboard'].scaling = [1.5, 1, 1.5]
for key, geo in geometries.items():
    if key != 'Chessboard':
        geo.translation = [-14,0,-13.5]

json.dump(geometries, open('data/data.json', 'w'))