import bpy


def on_update_manage(self, context):
    armature = context.active_object.data
    action = context.active_object.animation_data.action
    value = self.manage
    if value:
        existing_actions = [a.action for a in armature.actionman_actions]
        if self in existing_actions:
            return
        prop = armature.actionman_actions.add()
        prop.name = action.name
        prop.action = action
    else:
        index = armature.actionman_actions.find(action.name)
        if index > -1:
            armature.actionman_actions.remove(index)


class ActionManProperties(bpy.types.PropertyGroup):
    manage: bpy.props.BoolProperty(name="Manage", update=on_update_manage)
    name_backup: bpy.props.StringProperty(name="Name Backup")
    target: bpy.props.PointerProperty(name="Target", type=bpy.types.Object)
    subtarget: bpy.props.StringProperty(name="Sub Target")

    transform_channel: bpy.props.EnumProperty(
        name="Transform Channel",
        items=[
            ("LOCATION_X", " X Location", " X Location", 1),
            ("LOCATION_Y", " Y Location", " Y Location", 2),
            ("LOCATION_Z", " Z Location", " Z Location", 3),
            ("ROTATION_X", "X Rotation", "X Rotation", 4),
            ("ROTATION_Y", "Y Rotation", "Y Rotation", 5),
            ("ROTATION_Z", "Z Rotation", "Z Rotation", 6),
            ("SCALE_X", "X Scale", "X Scale", 7),
            ("SCALE_Y", "Y Scale", "Y Scale", 8),
            ("SCALE_Z", "Z Scale", "Z Scale", 9),
        ],
    )
    target_space: bpy.props.EnumProperty(
        name="Target Space",
        items=[
            ("WORLD", "World Space", "World Space", 1),
            ("POSE", "Pose Space", "Pose Space", 2),
            ("LOCAL_WITH_PARENT", "Local With Parent", "Local With Parent", 3),
            ("LOCAL", "Local Space", "Local Space", 4),
        ],
        default="LOCAL",
    )

    activation_start: bpy.props.FloatProperty("Activation Start", unit="LENGTH")
    activation_end: bpy.props.FloatProperty("Activation End", unit="LENGTH")

    activation_start_location: bpy.props.FloatProperty("Activation Start Location", unit="LENGTH")
    activation_end_location: bpy.props.FloatProperty("Activation End Location", unit="LENGTH")

    activation_start_rotation: bpy.props.FloatProperty("Activation Start Rotation", unit="ROTATION")
    activation_end_rotation: bpy.props.FloatProperty("Activation End Rotation", unit="ROTATION")

    activation_start_scale: bpy.props.FloatProperty("Activation Start Scale")
    activation_end_scale: bpy.props.FloatProperty("Activation End Scale")
    index: bpy.props.IntProperty("Index")
