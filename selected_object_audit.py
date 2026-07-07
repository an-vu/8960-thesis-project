#!/usr/bin/env python3

# Selected Object Audit

# This Blender script audits the currently selected object and reports its key mesh information.
# It shows the object name, type, evaluated geometry counts, original mesh datablock, mesh users, material slots, assigned materials, and any modifiers.
# The result is written into a Blender text block named `SELECTED_OBJECT_AUDIT_OUTPUT`.

# In Blender:
# - Go to **Scripting**
# - Click **New**
# - Paste this
# - Select an object
# - Click **Run Script**

import bpy

lines = []

def log(text=""):
    lines.append(str(text))

obj = bpy.context.object

if obj is None:
    raise Exception("Select one object first.")

log("===== SELECTED OBJECT AUDIT =====")
log(f"Object: {obj.name}")
log(f"Type: {obj.type}")

if obj.type != "MESH":
    log("Selected object is not a mesh.")
else:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    mesh.calc_loop_triangles()

    log("")
    log("## Evaluated Geometry")
    log(f"Vertices: {len(mesh.vertices):,}")
    log(f"Edges: {len(mesh.edges):,}")
    log(f"Faces: {len(mesh.polygons):,}")
    log(f"Triangles: {len(mesh.loop_triangles):,}")

    eval_obj.to_mesh_clear()

    log("")
    log("## Original Mesh Data")
    log(f"Mesh datablock: {obj.data.name}")
    log(f"Mesh users: {obj.data.users}")
    log(f"Material slots: {len(obj.material_slots)}")

    log("")
    log("## Materials")
    for slot in obj.material_slots:
        mat = slot.material
        if mat:
            log(f"- {mat.name} | Users: {mat.users}")
        else:
            log("- Empty material slot")

    log("")
    log("## Modifiers")
    if obj.modifiers:
        for mod in obj.modifiers:
            log(f"- {mod.name} | Type: {mod.type}")
    else:
        log("No modifiers.")

log("")
log("===== END SELECTED OBJECT AUDIT =====")

text_name = "SELECTED_OBJECT_AUDIT_OUTPUT"

if text_name in bpy.data.texts:
    text_block = bpy.data.texts[text_name]
    text_block.clear()
else:
    text_block = bpy.data.texts.new(text_name)

text_block.write("\n".join(lines))

for area in bpy.context.screen.areas:
    if area.type == "TEXT_EDITOR":
        area.spaces.active.text = text_block
        break