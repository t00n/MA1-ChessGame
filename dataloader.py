from collada import *

data = Collada('data/chessboard+man.dae')

geometries = data.geometries

scene = {}
for i, node in enumerate(data.scene.nodes):
    try:
        name = "".join(node.id.split('_')[:2])
        scene[name] = node.children[0].geometry
        print(i, name, node.children[0].geometry)
    except:
        pass