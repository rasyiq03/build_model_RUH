import bpy
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        print(obj.name)
