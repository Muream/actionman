import logging
from math import pi
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
        self.action = context.object.animation_data.action

        if self.action.name != self.action.actionman.name_backup:
            self.rename_action_references()

        self.create_or_update_constraints(context)

        armature = bpy.context.object.data
        enforce_constraint_order(armature, self.action)

        return {"FINISHED"}

    def create_or_update_constraints(self, context):
        for group in self.action.groups:  # each group corresponds to a bone
            obj = context.object
            bone = obj.pose.bones[group.name]
            self.create_or_update_action_constraints(bone)

        self.create_or_update_limit_constraints()

    def rename_action_references(self):
        """rename the actions in the constraints as well as the armature.actionman_actions."""
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                armature = obj.data
                for prop in armature.actionman_actions:
                    if prop.action == self.action:
                        prop.name = self.action.name
                for bone in obj.pose.bones:
                    for constraint in bone.constraints:
                        if constraint.type == "ACTION":
                            if constraint.name == self.action.actionman.name_backup:
                                constraint.name = self.action.name
        self.action.actionman.name_backup = self.action.name

    def create_or_update_action_constraints(self, bone):
        if self.action.name in [c.name for c in bone.constraints]:
            logger.info(
                "Action Constraint `{}` already exists on `{}`, updating its values only.".format(
                    self.action.name, bone.name
                )
            )
            constraint = bone.constraints[self.action.name]
        else:
            logger.info("Adding action constraint on {}".format(bone))
            constraint = bone.constraints.new("ACTION")
            constraint.name = self.action.name
            constraint.show_expanded = False

        target = bpy.data.objects[self.action.actionman.target]
        constraint.target = target
        if self.action.actionman.subtarget:
            constraint.subtarget = self.action.actionman.subtarget

        constraint.transform_channel = self.action.actionman.transform_channel
        constraint.target_space = self.action.actionman.target_space

        constraint.action = self.action

        constraint.frame_start = self.action.frame_range[0]
        constraint.frame_end = self.action.frame_range[1]

        constraint.min = self.action.actionman.activation_start
        constraint.max = self.action.actionman.activation_end

    def create_or_update_limit_constraints(self):
        target = self.action.actionman.target
        subtarget = self.action.actionman.subtarget
        actions = [
            a
            for a in bpy.data.actions
            if a.actionman.target == target and a.actionman.subtarget == subtarget
        ]

        if target:
            target = bpy.data.objects[target]
            if subtarget:
                subtarget = target.pose.bones[subtarget]
                controller = subtarget
            else:
                logger.warning(
                    "No Controller specified, skipping limit constraint creation"
                )
                return

        data = {"LOCATION": {}, "ROTATION": {}, "SCALE": {}}
        for action in actions:
            if not action.actionman.manage:
                continue
            if (
                action.actionman.target == target.name
                and action.actionman.subtarget == subtarget.name
            ):
                transform_channel = action.actionman.transform_channel
                transform, axis = transform_channel.split("_")
                end = action.actionman.activation_end

                if end < 0:
                    data[transform]["min_" + axis] = end

                if end > 0:
                    data[transform]["max_" + axis] = end

        for transform in ["LOCATION", "ROTATION", "SCALE"]:
            if data[transform]:
                constraint = self.create_or_get_limit_constraint(controller, transform)
                for axis in "XYZ":
                    start = data[transform].get("min_" + axis, 0)
                    end = data[transform].get("max_" + axis, 0)
                    if transform == "ROTATION":
                        setattr(constraint, "use_limit_" + axis.lower(), True)
                        start = start * (pi / 180)
                        end = end * (pi / 180)
                    else:
                        setattr(constraint, "use_min_" + axis.lower(), True)
                        setattr(constraint, "use_max_" + axis.lower(), True)

                    if start:
                        setattr(constraint, "min_" + axis.lower(), start)
                    if end:
                        setattr(constraint, "max_" + axis.lower(), end)

    def create_or_get_limit_constraint(self, controller, transform_type):
        constraint_name = "Limit " + transform_type.title()
        constraint_type = "LIMIT_" + transform_type.upper()

        existing_constraints_names = [c.name for c in controller.constraints]
        if constraint_name in existing_constraints_names:
            constraint = controller.constraints[constraint_name]
        else:
            constraint = controller.constraints.new(constraint_type)
            constraint.owner_space = "LOCAL"
            constraint.use_transform_limit = True

        return constraint

