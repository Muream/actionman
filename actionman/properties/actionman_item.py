import bpy


class ActionManItemProperty(bpy.types.PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action)
