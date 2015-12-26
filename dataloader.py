from collada import *

data = Collada('data/chessboard+man.dae')

geometries = {}
for i, node in enumerate(data.scene.nodes):
    try:
        name = "".join(node.id.split('_')[:2])
        geometries[name] = node.children[0].geometry
        print(i, name, node.children[0].geometry)
    except:
        pass