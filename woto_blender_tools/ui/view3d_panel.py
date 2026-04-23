import bpy


class WotoPivotToolsPanel(bpy.types.Panel):
    bl_label = "Pivot Tools"
    bl_idname = "WOTO_PT_pivot_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Woto'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        if layout is None:
            return

        col = layout.column(align=True)
        col.label(text="Selected empties only")

        op = col.operator(
            "woto.origin_to_children_geometry",
            text="Children Geometry (Fast)",
        )
        op.center_mode = 'BOUNDING_BOX'
        op.skip_nested_selected = True

        op = col.operator(
            "woto.origin_to_children_geometry",
            text="Children Geometry (Exact)",
        )
        op.center_mode = 'VERTEX_AVERAGE'
        op.skip_nested_selected = True

        box = layout.box()
        box.label(text="Fast = combined bounding box center")
        box.label(text="Exact = average of all child mesh vertices")
        box.label(text="Children stay visually in place")
