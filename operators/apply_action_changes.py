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

        if self.action.actionman.split_transformations:
            self.split_transformations()

        self.create_or_update_constraints(context)

        armature = bpy.context.object.data
        enforce_constraint_order(armature, self.action)

        return {"FINISHED"}

    def split_transformations(self):
        translate_action = self.create_sub_action("translate")
        for fcurve in translate_action.fcurves:
            if not "location" in fcurve.data_path:
                translate_action.fcurves.remove(fcurve)

        rotate_scale_action = self.create_sub_action("rotate_scale")
        for fcurve in rotate_scale_action.fcurves:
            if "location" in fcurve.data_path:
                rotate_scale_action.fcurves.remove(fcurve)

    def create_sub_action(self, action_component):
        action_name = action_component + "_subaction"
        action = getattr(self.action.actionman, action_name, None)

        if action:
            bpy.data.actions.remove(action, do_unlink=True)

        action = self.action.copy()
        self.clear_action(action)

        setattr(self.action.actionman, action_name, action)
        action.name = f"{self.action.name}.{action_component}"

        return action

    def clear_action(self, action):
        """resets the action's actionman attributs to their default."""
        manage = False
        index = 0
        name_backup = ""

        target = None
        subtarget = ""

        transform_channel = "LOCATION_X"
        target_space = "LOCAL"

        activation_start = 0
        activation_end = 0

        activation_start_location = 0
        activation_end_location = 0
        activation_start_rotation = 0
        activation_end_rotation = 0
        activation_start_scale = 0
        activation_end_scale = 0

        split_transformations = False
        translate_subaction = None
        rotate_scale_subaction = None

    def create_or_update_constraints(self, context):
        for group in self.action.groups:  # each group corresponds to a bone
            obj = context.object
            bone = obj.pose.bones[group.name]

            self.remove_unwanted_constraints(bone)
            if self.action.actionman.split_transformations:
                translate_constraint = self.create_or_get_action_constraint(
                    bone, self.action.name + ".translate"
                )
                self.set_constraint_settings(translate_constraint)
                rotate_scale_constraint = self.create_or_get_action_constraint(
                    bone, self.action.name + ".rotate_scale"
                )
                self.set_constraint_settings(rotate_scale_constraint)
            else:
                constraint = self.create_or_get_action_constraint(
                    bone, self.action.name
                )
                self.set_constraint_settings(constraint)

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

    def create_or_get_action_constraint(self, bone, constraint_name):
        if constraint_name in [c.name for c in bone.constraints]:
            logger.info(
                "Action Constraint `{}` already exists on `{}`, updating its values only.".format(
                    constraint_name, bone.name
                )
            )
            constraint = bone.constraints[constraint_name]
        else:
            logger.info("Adding action constraint on {}".format(bone))
            constraint = bone.constraints.new("ACTION")
            constraint.name = constraint_name
            constraint.show_expanded = False
        return constraint

    def set_constraint_settings(self, constraint):
        target = self.action.actionman.target
        constraint.target = target
        if self.action.actionman.subtarget:
            constraint.subtarget = self.action.actionman.subtarget

        constraint.transform_channel = self.action.actionman.transform_channel
        constraint.target_space = self.action.actionman.target_space

        constraint.action = self.action

        constraint.frame_start = self.action.frame_range[0]
        constraint.frame_end = self.action.frame_range[1]

        transform = self.action.actionman.transform_channel.split("_")[0]

        value_min = getattr(
            self.action.actionman, "activation_start_" + transform.lower()
        )
        value_max = getattr(
            self.action.actionman, "activation_end_" + transform.lower()
        )

        if transform == "ROTATION":
            value_min = value_min * (180 / pi)
            value_max = value_max * (180 / pi)

        constraint.min = value_min
        constraint.max = value_max

    def remove_unwanted_constraints(self, bone):
        """Remove the action constraints that shouldn't exist.
            if the action is split, remove the main action from the constraint.
            if it's not split, remove the components.
        """
        if self.action.actionman.split_transformations:
            # remove the potential unsplit action from the constraints
            if self.action.name in [c.name for c in bone.constraints]:
                bone.constraints.remove(bone.constraints[self.action.name])
        else:
            # remove the potential split actions from the constraint
            translate_action = self.action.actionman.translate_subaction
            if translate_action:
                if translate_action.name in [c.name for c in bone.constraints]:
                    bone.constraints.remove(bone.constraints[translate_action.name])
            rotate_scale_action = self.action.actionman.rotate_scale_subaction
            if rotate_scale_action:
                if rotate_scale_action.name in [c.name for c in bone.constraints]:
                    bone.constraints.remove(bone.constraints[rotate_scale_action.name])

    def create_or_update_limit_constraints(self):
        target = self.action.actionman.target
        subtarget = self.action.actionman.subtarget
        actions = [
            a
            for a in bpy.data.actions
            if a.actionman.target == target and a.actionman.subtarget == subtarget
        ]

        if target:
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
                action.actionman.target == target
                and action.actionman.subtarget == subtarget.name
            ):
                transform_channel = action.actionman.transform_channel
                transform, axis = transform_channel.split("_")
                end = getattr(action.actionman, "activation_end_" + transform.lower())
                if transform == "ROTATION":
                    end = end * (180 / pi)

                if transform == "SCALE":
                    if end < 1:
                        data[transform]["min_" + axis] = end

                    if end > 1:
                        data[transform]["max_" + axis] = end
                else:
                    if end < 0:
                        data[transform]["min_" + axis] = end

                    if end > 0:
                        data[transform]["max_" + axis] = end

        for transform in ["LOCATION", "ROTATION", "SCALE"]:
            if data[transform]:
                constraint = self.create_or_get_limit_constraint(controller, transform)
                for axis in "XYZ":
                    if transform == "SCALE":
                        start = data[transform].get("min_" + axis, 1)
                        end = data[transform].get("max_" + axis, 1)
                    else:
                        start = data[transform].get("min_" + axis, 0)
                        end = data[transform].get("max_" + axis, 0)
                    if transform == "ROTATION":
                        setattr(constraint, "use_limit_" + axis.lower(), True)
                        start = start * (180 / pi)
                        end = end * (180 / pi)
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
            constraint.show_expanded = False

        return constraint

