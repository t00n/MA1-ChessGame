from collada import *

data = Collada('data/chessboard+man.dae')

class Geometry:
    pass


geometries = {}
for i, node in enumerate(data.scene.nodes):
    try:
        name = "".join(node.id.split('_')[:2])
        geo = node.children[0].geometry
        my_geo = Geometry()
        my_geo.vertices = []
        my_geo.normals = []
        for prim in geo.primitives:
            my_geo.vertices.extend(prim.vertex[prim.vertex_index][:,[0,2,1]])
            my_geo.normals.extend(prim.normal[prim.normal_index][:,[0,2,1]])
        geometries[name] = my_geo
    except AttributeError:
        pass