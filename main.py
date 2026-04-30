#main.py

import sys, importlib

sys.path.append("C:\\blender_poly")

import dragon

def deep_reload(pkg):
    name = pkg.__name__
    modules = list(sys.modules.items())
    for modname, mod in modules:
        if modname == name or modname.startswith(name + '.'):
            importlib.reload(mod)

deep_reload(dragon)

dragon.clear_scene()
dragon.build_dragon()