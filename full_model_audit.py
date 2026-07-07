#!/usr/bin/env python3

# Full Model Audit

# This Blender script performs a full model audit by scanning the scene and reporting key performance metrics, including file size, total objects, mesh objects, vertices, faces, triangles, materials, and textures.
# It also lists the top 20 heaviest mesh objects by triangle count and outputs texture resolution, file size, and file paths.
# The audit result is written into a new Blender text block named MODEL_AUDIT_OUTPUT.

# In Blender:
# - Go to **Scripting**
# - Click **New**
# - Paste this
# - Click **Run Script**

import bpy
import os

lines = []

def log(text=""):
    lines.append(str(text))

log("===== MODEL AUDIT =====")

# File info
blend_path = bpy.data.filepath
if blend_path:
    blend_size_mb = os.path.getsize(blend_path) / (1024 * 1024)
    log(f"Blend file: {blend_path}")
    log(f"Blend file size: {blend_size_mb:.2f} MB")
else:
    log("Blend file: Not saved yet")

# Objects
all_objects = bpy.context.scene.objects
mesh_objects = [obj for obj in all_objects if obj.type == "MESH"]

log("")
log(f"Total objects: {len(all_objects)}")
log(f"Mesh objects: {len(mesh_objects)}")

# Geometry
depsgraph = bpy.context.evaluated_depsgraph_get()

total_vertices = 0
total_faces = 0
total_triangles = 0
heavy_objects = []

for obj in mesh_objects:
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    mesh.calc_loop_triangles()

    v_count = len(mesh.vertices)
    f_count = len(mesh.polygons)
    tri_count = len(mesh.loop_triangles)

    total_vertices += v_count
    total_faces += f_count
    total_triangles += tri_count

    heavy_objects.append((obj.name, tri_count, v_count, f_count))

    eval_obj.to_mesh_clear()

log("")
log(f"Total vertices: {total_vertices:,}")
log(f"Total faces: {total_faces:,}")
log(f"Total triangles: {total_triangles:,}")

log("")
log("Top 20 heaviest mesh objects:")
for name, tris, verts, faces in sorted(heavy_objects, key=lambda x: x[1], reverse=True)[:20]:
    log(f"{name}: {tris:,} tris | {verts:,} verts | {faces:,} faces")

# Materials
materials = list(bpy.data.materials)
used_materials = set()

for obj in mesh_objects:
    for slot in obj.material_slots:
        if slot.material:
            used_materials.add(slot.material)

log("")
log(f"Total materials in file: {len(materials)}")
log(f"Used materials on mesh objects: {len(used_materials)}")

# Textures
images = list(bpy.data.images)
file_images = [img for img in images if img.source == "FILE"]

log("")
log(f"Total image datablocks: {len(images)}")
log(f"External file textures: {len(file_images)}")

log("")
log("Texture list:")
for img in file_images:
    width, height = img.size
    filepath = bpy.path.abspath(img.filepath)

    if filepath and os.path.exists(filepath):
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        size_text = f"{size_mb:.2f} MB"
    else:
        size_text = "missing/unloaded"

    log(f"{img.name}: {width}x{height} | {size_text} | {filepath}")

log("")
log("===== END AUDIT =====")

# Write output into Blender Text Editor
text_name = "MODEL_AUDIT_OUTPUT"

if text_name in bpy.data.texts:
    text_block = bpy.data.texts[text_name]
    text_block.clear()
else:
    text_block = bpy.data.texts.new(text_name)

text_block.write("\n".join(lines))

# Switch current text editor to output if possible
for area in bpy.context.screen.areas:
    if area.type == "TEXT_EDITOR":
        area.spaces.active.text = text_block
        break