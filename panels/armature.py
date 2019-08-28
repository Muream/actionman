import bpy
import logging


logging.getLogger(__name__)


class ActionManArmaturePanel(bpy.types.Panel):
    bl_label = "Action Man"
    bl_idname = "ARMATURE_PT_action_man"
    bl_space_type = "PROPERTIES"
    bl_context = "data"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        return context.armature

    def draw(self, context):
        layout = self.layout
        armature = context.armature

        row = layout.row()
        row.template_list(
            "UI_UL_list",
            "actions",
            armature,
            "actionman_actions",
            armature,
            "actionman_active_action_index",
            rows=5,
            type="DEFAULT",
        )

        col = row.column(align=True)
        operator = col.operator("actionman.action_move", icon="TRIA_UP", text="")
        operator.direction = "UP"
        operator = col.operator("actionman.action_move", icon="TRIA_DOWN", text="")
        operator.direction = "DOWN"
