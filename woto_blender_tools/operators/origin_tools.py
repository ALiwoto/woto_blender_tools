from __future__ import annotations

from typing import Iterable, Iterator

import bpy
from mathutils import Vector


def iter_descendants(obj: bpy.types.Object) -> Iterator[bpy.types.Object]:
    for child in obj.children:
        yield child
        yield from iter_descendants(child)


def get_mesh_descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    return [obj for obj in iter_descendants(root) if obj.type == 'MESH']


def has_selected_empty_ancestor(
    obj: bpy.types.Object,
    selected_empties: set[bpy.types.Object],
) -> bool:
    parent = obj.parent
    while parent is not None:
        if parent in selected_empties:
            return True
        parent = parent.parent
    return False


def evaluated_world_bbox_points(
    obj: bpy.types.Object,
    depsgraph: bpy.types.Depsgraph,
) -> list[Vector]:
    obj_eval = obj.evaluated_get(depsgraph)
    return [obj_eval.matrix_world @ Vector(corner) for corner in obj_eval.bound_box]


def combined_bbox_center_world(
    objects: Iterable[bpy.types.Object],
    depsgraph: bpy.types.Depsgraph,
) -> Vector:
    points: list[Vector] = []

    for obj in objects:
        points.extend(evaluated_world_bbox_points(obj, depsgraph))

    if not points:
        raise ValueError("No bounding box points found.")

    min_v = Vector((
        min(p.x for p in points),
        min(p.y for p in points),
        min(p.z for p in points),
    ))
    max_v = Vector((
        max(p.x for p in points),
        max(p.y for p in points),
        max(p.z for p in points),
    ))

    return (min_v + max_v) * 0.5


def vertex_average_center_world(
    objects: Iterable[bpy.types.Object],
    depsgraph: bpy.types.Depsgraph,
) -> Vector:
    total = Vector((0.0, 0.0, 0.0))
    count = 0

    for obj in objects:
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()

        try:
            for vertex in mesh.vertices:
                total += obj_eval.matrix_world @ vertex.co
                count += 1
        finally:
            obj_eval.to_mesh_clear()

    if count == 0:
        raise ValueError("No vertices found.")

    return total / count


def move_empty_preserve_children_world(
    empty: bpy.types.Object,
    new_world_location: Vector,
    context: bpy.types.Context,
) -> None:
    saved_child_world = {
        child: child.matrix_world.copy()
        for child in empty.children
    }

    new_world_matrix = empty.matrix_world.copy()
    new_world_matrix.translation = new_world_location
    empty.matrix_world = new_world_matrix

    context.view_layer.update()

    for child, world_matrix in saved_child_world.items():
        child.matrix_world = world_matrix

    context.view_layer.update()


class OriginToChildrenGeometryOperator(bpy.types.Operator):
    bl_idname = "woto.origin_to_children_geometry"
    bl_label = "Origin To Children Geometry"
    bl_description = (
        "Move selected Empty objects to the center of all mesh descendants "
        "while keeping their children visually in place"
    )
    bl_options = {'REGISTER', 'UNDO'}

    center_mode: bpy.props.EnumProperty(
        name="Center Mode",
        description="How to compute the new pivot location",
        items=[
            (
                'BOUNDING_BOX',
                "Bounding Box",
                "Fast: center of combined descendant mesh bounding boxes",
            ),
            (
                'VERTEX_AVERAGE',
                "Vertex Average",
                "Slower but more exact: average of all descendant mesh vertices in world space",
            ),
        ],
        default='BOUNDING_BOX',
    )

    skip_nested_selected: bpy.props.BoolProperty(
        name="Skip Nested Selected Empties",
        description=(
            "If a selected empty has another selected empty above it in the hierarchy, skip it "
            "to avoid double-processing"
        ),
        default=True,
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return any(obj.type == 'EMPTY' for obj in context.selected_objects)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        if layout is None:
            return

        layout.prop(self, "center_mode")
        layout.prop(self, "skip_nested_selected")

    def execute(self, context: bpy.types.Context):
        selected_empties = [
            obj for obj in context.selected_objects
            if obj.type == 'EMPTY'
        ]

        if not selected_empties:
            self.report({'WARNING'}, "Select at least one Empty object.")
            return {'CANCELLED'}

        selected_set = set(selected_empties)

        if self.skip_nested_selected:
            empties_to_process: list[bpy.types.Object] = []
            nested_skipped = 0

            for obj in selected_empties:
                if has_selected_empty_ancestor(obj, selected_set):
                    nested_skipped += 1
                else:
                    empties_to_process.append(obj)
        else:
            empties_to_process = selected_empties
            nested_skipped = 0

        depsgraph = context.evaluated_depsgraph_get()

        moved_count = 0
        no_mesh_count = 0
        exact_fallback_count = 0

        for empty in empties_to_process:
            mesh_descendants = get_mesh_descendants(empty)

            if not mesh_descendants:
                no_mesh_count += 1
                continue

            if self.center_mode == 'VERTEX_AVERAGE':
                try:
                    center = vertex_average_center_world(mesh_descendants, depsgraph)
                except ValueError:
                    center = combined_bbox_center_world(mesh_descendants, depsgraph)
                    exact_fallback_count += 1
            else:
                center = combined_bbox_center_world(mesh_descendants, depsgraph)

            move_empty_preserve_children_world(empty, center, context)
            moved_count += 1

        if moved_count == 0:
            self.report({'WARNING'}, "No selected empties had mesh descendants.")
            return {'CANCELLED'}

        msg = f"Moved {moved_count} empt{'y' if moved_count == 1 else 'ies'}"

        extras = []
        if no_mesh_count:
            extras.append(f"{no_mesh_count} without mesh descendants")
        if nested_skipped:
            extras.append(f"{nested_skipped} nested selected skipped")
        if exact_fallback_count:
            extras.append(f"{exact_fallback_count} exact-mode fallback to bounding box")

        if extras:
            msg += " | " + ", ".join(extras)

        self.report({'INFO'}, msg)
        return {'FINISHED'}


def menu_func_object(self, context: bpy.types.Context) -> None:
    self.layout.separator()
    self.layout.operator(
        OriginToChildrenGeometryOperator.bl_idname,
        text="Origin To Children Geometry",
    )
