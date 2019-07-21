import bpy
import logging


logging.getLogger(__name__)


class ActionManActionPanel(bpy.types.Panel):
    bl_category = "Action Man"
    bl_label = "Action Man"
    bl_idname = "FR_PT_panel"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        """Make sure there's an active action."""
        active_object = context.object
        if not active_object:
            return False

        animation_data = active_object.animation_data
        if not animation_data:
            return False

        action = animation_data.action
        if not action:
            return False

        return True

    def draw(self, context):
        action = context.object.animation_data.action

        layout = self.layout

        row = layout.row()
        row.prop(action.actionman, "manage")

        if not action.actionman.manage:
            return

        row = layout.row()
        row.prop(action.actionman, "target")
        target = action.actionman.target

        if target is not None:
            if type(target.data) == bpy.types.Armature:
                row = layout.row()
                row.prop_search(action.actionman, "subtarget", target.data, "bones", text="Bone")

        row = layout.row()
        row.prop(action.actionman, "transform_channel")

        row = layout.row()
        row.prop(action.actionman, "target_space")

        row = layout.row()
        row.label(text="Activation Range:")

        split = layout.split()
        col = split.column(align=True)

        transform_channel = action.actionman.transform_channel.split("_")[0]
        col.prop(action.actionman, "activation_start_" + transform_channel.lower(), text="Start")
        col.prop(action.actionman, "activation_end_" + transform_channel.lower(), text="End")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.operator("actionman.clean")

        row = layout.row()
        row.operator("actionman.apply", text="Apply")

        row = layout.row()
        row.label(text="Delete Constraints:")
        row = layout.row(align=True)
        row.operator("actionman.delete_useless_constraints", text="Useless")
        row.operator("actionman.delete_all_constraints", text="All")
