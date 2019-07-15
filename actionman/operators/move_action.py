import bpy
import logging

from ..utils import enforce_constraint_order


logger = logging.getLogger(__name__)


class ActionMoveOperator(bpy.types.Operator):
    bl_idname = "actionman.action_move"
    bl_label = "Action Move"
    bl_options = {"INTERNAL"}

    direction: bpy.props.StringProperty()

    def invoke(self, context, event):
        self.armature = context.object.data
        self.index = self.armature.actionman_active_action_index
        self.action = self.armature.actionman_actions.values()[self.index].action

        if event.shift:
            print("SHIFT")
            self.move_max()
        else:
            print("NOT SHIFT")
            self.move_once()

        return {"FINISHED"}

    def move_max(self):
        can_move = True
        while can_move:
            can_move = self.move_once()

    def move_once(self):

        if self.direction == "UP":
            new_index = self.index - 1
        if self.direction == "DOWN":
            new_index = self.index + 1

        if new_index < 0 or new_index >= len(self.armature.actionman_actions):
            return False

        other_action = self.armature.actionman_actions.values()[new_index].action

        self.armature.actionman_actions.move(self.index, new_index)
        self.armature.actionman_active_action_index = new_index
        self.index = new_index

        enforce_constraint_order(self.armature, self.action)
        enforce_constraint_order(self.armature, other_action)

        return True
