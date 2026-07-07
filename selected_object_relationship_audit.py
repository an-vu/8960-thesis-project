#!/usr/bin/env python3

# Selected Object Relationship Audit

# This Blender script audits the relationship and dependency structure of the currently selected object.
# It reports the object’s parent, children, collections, shared mesh data, materials, modifiers, constraints, animation data, drivers, shape keys, and any incoming driver references.
# It also checks for drivers that read scene custom properties. The result is written into a Blender text block named `RELATIONSHIP_AUDIT_OUTPUT`.

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

def safe_name(x):
    return x.name if x else "None"

obj = bpy.context.object

if obj is None:
    raise Exception("Select an object first.")

log("===== RELATIONSHIP AUDIT =====")
log(f"Selected object: {obj.name}")
log(f"Type: {obj.type}")

# Basic object relationship
log("")
log("## Object Relations")
log(f"Parent: {safe_name(obj.parent)}")
log(f"Parent type: {obj.parent_type}")
log(f"Children: {len(obj.children)}")

for child in obj.children:
    log(f"- Child: {child.name} | Type: {child.type}")

log("")
log("Collections:")
for col in obj.users_collection:
    log(f"- {col.name}")

# Shared mesh data
log("")
log("## Mesh Data Sharing")
if obj.data:
    log(f"Mesh datablock: {obj.data.name}")
    log(f"Mesh users: {obj.data.users}")

    if obj.data.users > 1:
        log("Objects sharing this same mesh data:")
        for other in bpy.data.objects:
            if other.data == obj.data and other != obj:
                log(f"- {other.name}")

# Materials
log("")
log("## Materials")
for slot in obj.material_slots:
    mat = slot.material
    if mat:
        log(f"- {mat.name} | Users: {mat.users}")
    else:
        log("- Empty material slot")

# Modifiers
log("")
log("## Modifiers")
if len(obj.modifiers) == 0:
    log("No modifiers found.")
else:
    for mod in obj.modifiers:
        log(f"- {mod.name} | Type: {mod.type}")

        for attr in ["object", "mirror_object", "target", "offset_object"]:
            if hasattr(mod, attr):
                target = getattr(mod, attr)
                if target:
                    log(f"  {attr}: {target.name}")

# Constraints
log("")
log("## Constraints")
if len(obj.constraints) == 0:
    log("No constraints found.")
else:
    for con in obj.constraints:
        log(f"- {con.name} | Type: {con.type} | Influence: {con.influence}")

        if hasattr(con, "target") and con.target:
            log(f"  Target: {con.target.name}")

        if hasattr(con, "subtarget") and con.subtarget:
            log(f"  Subtarget: {con.subtarget}")

# Animation data on object
log("")
log("## Object Animation Data")
if obj.animation_data:
    if obj.animation_data.action:
        log(f"Action: {obj.animation_data.action.name}")

        for fc in obj.animation_data.action.fcurves:
            log(f"- FCurve: {fc.data_path} [{fc.array_index}] | Keyframes: {len(fc.keyframe_points)}")
    else:
        log("No active action.")

    if obj.animation_data.drivers:
        log("")
        log("Object Drivers:")
        for drv in obj.animation_data.drivers:
            log(f"- Driven property: {drv.data_path} [{drv.array_index}]")
            log(f"  Expression: {drv.driver.expression}")

            for var in drv.driver.variables:
                log(f"  Variable: {var.name} | Type: {var.type}")

                for target in var.targets:
                    log(f"    Target ID: {safe_name(target.id)}")
                    log(f"    Data path: {target.data_path}")
    else:
        log("No object drivers.")
else:
    log("No object animation data.")

# Shape keys / mesh animation
log("")
log("## Mesh / Shape Key Data")
if obj.data and hasattr(obj.data, "shape_keys") and obj.data.shape_keys:
    log(f"Shape keys found: {obj.data.shape_keys.name}")

    for kb in obj.data.shape_keys.key_blocks:
        log(f"- Shape key: {kb.name} | Value: {kb.value}")

    if obj.data.shape_keys.animation_data and obj.data.shape_keys.animation_data.drivers:
        log("Shape key drivers:")
        for drv in obj.data.shape_keys.animation_data.drivers:
            log(f"- Driven property: {drv.data_path} [{drv.array_index}]")
            log(f"  Expression: {drv.driver.expression}")
else:
    log("No shape keys found.")

# Incoming driver references
log("")
log("## Incoming Drivers Referencing This Object")
found_incoming = False

def scan_drivers(id_block, owner_name):
    global found_incoming

    ad = getattr(id_block, "animation_data", None)
    if not ad or not ad.drivers:
        return

    for drv in ad.drivers:
        for var in drv.driver.variables:
            for target in var.targets:
                if target.id == obj or target.id == obj.data:
                    found_incoming = True
                    log(f"- {owner_name}")
                    log(f"  Driven: {drv.data_path} [{drv.array_index}]")
                    log(f"  Variable: {var.name}")
                    log(f"  Target path: {target.data_path}")

for other in bpy.data.objects:
    scan_drivers(other, f"Object: {other.name}")

for scene in bpy.data.scenes:
    scan_drivers(scene, f"Scene: {scene.name}")

for mat in bpy.data.materials:
    scan_drivers(mat, f"Material: {mat.name}")

if not found_incoming:
    log("No incoming drivers directly referencing this object or its mesh data.")

# Drivers using Scene custom properties
log("")
log("## Drivers Reading Scene Custom Properties")
found_scene_props = False

for other in bpy.data.objects:
    ad = other.animation_data
    if not ad or not ad.drivers:
        continue

    for drv in ad.drivers:
        for var in drv.driver.variables:
            for target in var.targets:
                if target.id and target.id.__class__.__name__ == "Scene":
                    found_scene_props = True
                    log(f"- Object: {other.name}")
                    log(f"  Driven: {drv.data_path} [{drv.array_index}]")
                    log(f"  Scene target: {target.id.name}")
                    log(f"  Data path: {target.data_path}")
                    log(f"  Expression: {drv.driver.expression}")

if not found_scene_props:
    log("No object drivers reading Scene custom properties found.")

log("")
log("===== END RELATIONSHIP AUDIT =====")

# Write output into Blender text block
text_name = "RELATIONSHIP_AUDIT_OUTPUT"

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