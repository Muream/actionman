import logging
import bpy

from ..utils import enforce_constraint_order


logger = logging.getLogger(__name__)


class ApplyActionChanges(bpy.types.Operator):
    """Removes all the useless fcurves and groups of the active action."""

    bl_idname = "actionman.apply"
    bl_label = "Create Action Constraints"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        action = context.object.animation_data.action
        action_exists = action is not None
        is_managed = action.actionman.manage
        return action_exists and is_managed

    def execute(self, context):
        """Execute the operator."""
        action = context.object.animation_data.action

        if action.name != action.name_backup:
            # rename the constraints to the new action name
            for obj in bpy.data.objects:
                if obj.type == "ARMATURE":
                    armature = obj.data
                    for prop in armature.actionman_actions:
                        if prop.action == action:
                            prop.name = action.name
                    for bone in obj.pose.bones:
                        for constraint in bone.constraints:
                            if constraint.type == "ACTION":
                                if constraint.name == action.actionman.name_backup:
                                    constraint.name = action.name
            action.name_backup = action.name

        for group in action.groups:  # each group corresponds to a bone
            obj = context.object
            bone = obj.pose.bones[group.name]

            if action.name in [c.name for c in bone.constraints]:
                logger.info(
                    "Action Constraint `{}` already exists on `{}`, updating its values only.".format(
                        action.name, bone.name
                    )
                )
                constraint = bone.constraints[action.name]
            else:
                logger.info("Adding action constraint on {}".format(bone))
                constraint = bone.constraints.new("ACTION")
                constraint.name = action.name
                constraint.show_expanded = False

            target = bpy.data.objects[action.actionman.target]
            constraint.target = target
            if action.actionman.subtarget:
                constraint.subtarget = action.actionman.subtarget

            constraint.transform_channel = action.actionman.transform_channel
            constraint.target_space = action.target_space

            constraint.action = action

            constraint.frame_start = action.actionman.frame_range[0]
            constraint.frame_end = action.actionman.frame_range[1]

            constraint.min = action.actionman.activation_start
            constraint.max = action.actionman.activation_end

        armature = bpy.context.object.data
        enforce_constraint_order(armature, action)

        return {"FINISHED"}
