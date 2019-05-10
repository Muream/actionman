import logging
import bpy


logger = logging.getLogger(__name__)


class DeleteAllConstraints(bpy.types.Operator):
    """Remove all the action constraints named like the active action."""

    bl_idname = "action.delete_all_constraints"
    bl_label = "Delete All Constraints"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        action = context.object.animation_data.action
        action_exists = action is not None
        is_face_action = action.face_action
        return action_exists and is_face_action

    def execute(self, context):
        """Execute the operator."""
        action = context.object.animation_data.action
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                for bone in obj.pose.bones:
                    for constraint in bone.constraints:
                        if constraint.type == "ACTION":
                            if action.name == constraint.name:
                                logger.info(
                                    "Removing Constraint `{}` on bone `{}`".format(
                                        constraint.name, bone.name
                                    )
                                )
                                bone.constraints.remove(constraint)

        return {"FINISHED"}
