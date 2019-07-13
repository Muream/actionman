import bpy
import logging

from ..utils import enforce_constraint_order


logger = logging.getLogger(__name__)


class ActionMoveOperator(bpy.types.Operator):
    bl_idname = "actionman.action_move"
    bl_label = "Action Move"
    bl_options = {"INTERNAL"}

    direction: bpy.props.StringProperty()

    def execute(self, context):
        armature = context.object.data
        index = armature.actionman_active_action_index
        action = armature.actionman_actions.values()[index].action

        if self.direction == "UP":
            new_index = index - 1
        if self.direction == "DOWN":
            new_index = index + 1

        if new_index < 0 or new_index >= len(armature.actionman_actions):
            logger.warning("Can't move the current action")
            return {"FINISHED"}
        other_action = armature.actionman_actions.values()[new_index].action

        armature.actionman_actions.move(index, new_index)
        armature.actionman_active_action_index = new_index

        enforce_constraint_order(armature, action)
        enforce_constraint_order(armature, other_action)

        return {"FINISHED"}
