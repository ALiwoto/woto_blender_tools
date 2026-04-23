import bpy

from . import operators, ui

bl_info = {
    "name": "Woto Blender Tools",
    "author": "woto",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Woto",
    "description": "Custom tools for pivots, hierarchy, and workflow helpers",
    "category": "Object",
}


def register() -> None:
    operators.register()
    ui.register()


def unregister() -> None:
    ui.unregister()
    operators.unregister()
