
import bpy

from .view3d_panel import WotoPivotToolsPanel

CLASSES = (
    WotoPivotToolsPanel,
)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
