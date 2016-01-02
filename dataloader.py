from collada import *
from collada.scene import GeometryNode

data = Collada('data/chessboard+man.dae')

class Geometry:
    def __init__(self, geo):
        self.vertices = []
        self.normals = []
        for prim in geo.primitives:
            self.vertices.extend(prim.vertex[prim.vertex_index][:,[0,2,1]])
            self.normals.extend(prim.normal[prim.normal_index][:,[0,2,1]])


geometries = {}
for i, node in enumerate(data.scene.nodes):
    for child in node.children:
        if isinstance(child, GeometryNode):
            name = "".join(node.id.split('_')[:2])
            geometries[name] = Geometry(child.geometry)