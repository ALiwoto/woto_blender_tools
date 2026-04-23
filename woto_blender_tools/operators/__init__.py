from typing import Any, cast

import bpy

from .origin_tools import OriginToChildrenGeometryOperator, WotoSetOriginMenu

CLASSES = (
    OriginToChildrenGeometryOperator,
    WotoSetOriginMenu,
)

ORIGINAL_VIEW3D_MT_OBJECT_DRAW: Any | None = None


def draw_view3d_mt_object(self, context: bpy.types.Context) -> None:
    layout = self.layout
    if layout is None:
        return

    ob = context.object

    layout.menu("VIEW3D_MT_transform_object")
    layout.menu(WotoSetOriginMenu.bl_idname, text="Set Origin")
    layout.menu("VIEW3D_MT_mirror")
    layout.menu("VIEW3D_MT_object_clear")
    layout.menu("VIEW3D_MT_object_apply")
    layout.menu("VIEW3D_MT_snap")

    layout.separator()

    layout.operator("object.duplicate_move")
    layout.operator("object.duplicate_move_linked")
    layout.operator("object.join")

    layout.separator()

    layout.operator("view3d.copybuffer", text="Copy Objects", icon='COPYDOWN')
    layout.operator("view3d.pastebuffer", text="Paste Objects", icon='PASTEDOWN')

    layout.separator()

    layout.menu("VIEW3D_MT_object_asset", icon='ASSET_MANAGER')
    layout.menu("VIEW3D_MT_object_collection")

    layout.separator()

    layout.menu("VIEW3D_MT_object_liboverride", icon='LIBRARY_DATA_OVERRIDE')
    layout.menu("VIEW3D_MT_object_relations")
    layout.menu("VIEW3D_MT_object_parent")
    layout.menu("VIEW3D_MT_object_modifiers", icon='MODIFIER')
    layout.menu("VIEW3D_MT_object_constraints", icon='CONSTRAINT')
    layout.menu("VIEW3D_MT_object_track")
    layout.menu("VIEW3D_MT_make_links")

    layout.separator()

    layout.operator("object.shade_smooth")
    if ob and ob.type == 'MESH':
        layout.operator("object.shade_auto_smooth")
    layout.operator("object.shade_flat")

    layout.separator()

    layout.menu("VIEW3D_MT_object_animation")
    layout.menu("VIEW3D_MT_object_rigid_body")

    layout.separator()

    layout.menu("VIEW3D_MT_object_quick_effects")

    layout.separator()

    layout.menu("VIEW3D_MT_object_convert")

    layout.separator()

    layout.menu("VIEW3D_MT_object_showhide")
    layout.menu("VIEW3D_MT_object_cleanup")

    layout.separator()

    layout.operator_context = 'EXEC_REGION_WIN'
    layout.operator("object.delete", text="Delete").use_global = False
    layout.operator("object.delete", text="Delete Global").use_global = True

    layout.template_node_operator_asset_menu_items(catalog_path="Object")


def patch_object_menu_draw() -> None:
    global ORIGINAL_VIEW3D_MT_OBJECT_DRAW

    view3d_mt_object = cast(Any, bpy.types.VIEW3D_MT_object)

    if ORIGINAL_VIEW3D_MT_OBJECT_DRAW is None:
        ORIGINAL_VIEW3D_MT_OBJECT_DRAW = view3d_mt_object.draw

    view3d_mt_object.draw = draw_view3d_mt_object


def restore_object_menu_draw() -> None:
    global ORIGINAL_VIEW3D_MT_OBJECT_DRAW

    if ORIGINAL_VIEW3D_MT_OBJECT_DRAW is None:
        return

    view3d_mt_object = cast(Any, bpy.types.VIEW3D_MT_object)
    view3d_mt_object.draw = ORIGINAL_VIEW3D_MT_OBJECT_DRAW
    ORIGINAL_VIEW3D_MT_OBJECT_DRAW = None


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    patch_object_menu_draw()


def unregister() -> None:
    restore_object_menu_draw()

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
