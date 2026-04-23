
import bpy

from .origin_tools import OriginToChildrenGeometryOperator, menu_func_object

CLASSES = (
    OriginToChildrenGeometryOperator,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object.append(menu_func_object)


def unregister() -> None:
    bpy.types.VIEW3D_MT_object.remove(menu_func_object)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
