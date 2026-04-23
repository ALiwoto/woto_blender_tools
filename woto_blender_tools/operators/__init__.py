from typing import Any

import bpy

from .origin_tools import OriginToChildrenGeometryOperator, menu_func_set_origin

CLASSES = (
    OriginToChildrenGeometryOperator,
)

SET_ORIGIN_MENU_NAME = "VIEW3D_MT_object_set_origin"


def get_set_origin_menu() -> Any:
    return getattr(bpy.types, SET_ORIGIN_MENU_NAME)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    get_set_origin_menu().append(menu_func_set_origin)


def unregister() -> None:
    get_set_origin_menu().remove(menu_func_set_origin)

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
