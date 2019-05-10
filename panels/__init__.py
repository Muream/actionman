import bpy
import logging


logging.getLogger(__name__)


class ActionManPanel(bpy.types.Panel):
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
        row.prop(action, "face_action")

        if not action.face_action:
            return

        row = layout.row()
        row.operator("action.clean")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.prop_search(action, "target", bpy.data, "objects")
        target = bpy.data.armatures.get(action.target)
        if target is not None:
            if type(target) == bpy.types.Armature:
                row = layout.row()
                row.prop_search(action, "subtarget", target, "bones", text="Bone")

        row = layout.row()
        row.prop(action, "transform_channel")

        row = layout.row()
        row.label(text="Activation Range:")

        split = layout.split()
        col = split.column(align=True)
        col.prop(action, "activation_start", text="Start")
        col.prop(action, "activation_end", text="End")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.operator("action.create_constraint", text="Create/Update Constraints")

        row = layout.row()
        row.label(text="Delete Constraints:")
        row = layout.row(align=True)
        row.operator("action.delete_useless_constraints", text="Useless")
        row.operator("action.delete_all_constraints", text="All")
