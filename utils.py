import bpy
import logging


logger = logging.getLogger(__name__)


def enforce_constraint_order(armature, action):
    bones = get_affected_bones(armature, action)
    current_active_bone = armature.bones.active
    for bone in bones:
        constraints = bone.constraints

        action_constraints = [c.name for c in constraints if c.type == "ACTION"]
        translate_constraints = sorted(
            [c for c in action_constraints if "translate" in c]
        )
        rotate_scale_constraints = sorted(
            [c for c in action_constraints if "rotate_scale" in c]
        )
        unsplit_constraints = sorted(
            list(
                set(action_constraints)
                - set(translate_constraints)
                - set(rotate_scale_constraints)
            )
        )

        ordered_action_names = (
            translate_constraints + rotate_scale_constraints + unsplit_constraints
        )

        armature.bones.active = bone.bone
        reorder_constraints(bone, ordered_action_names)
    armature.bones.active = current_active_bone


def get_affected_bones(armature, action):
    armature_ob = bpy.data.objects[armature.name]
    return [b for b in armature_ob.pose.bones if b.name in action.groups]


def reorder_constraints(bone, ordered_action_names):
    def sort_constraint_as_actions(item):
        return ordered_action_names.index(item.name)

    constraints = [c for c in bone.constraints if c.type == "ACTION"]

    ordered_constraints = sorted(constraints, key=sort_constraint_as_actions)

    for expected_index, constraint in enumerate(ordered_constraints):

        ctx = bpy.context.copy()
        ctx["constraint"] = constraint

        current_index = bone.constraints.find(constraint.name)
        if current_index > expected_index:
            while current_index != expected_index:
                previous_index = current_index
                bpy.ops.constraint.move_up(
                    ctx, constraint=constraint.name, owner="BONE"
                )
                current_index = bone.constraints.find(constraint.name)
                if previous_index == current_index:
                    raise Exception(
                        "Failed to move the constraint {}. The bone {} is probably hidden".format(
                            constraint.name, bone.name
                        )
                    )
        elif current_index < expected_index:
            while current_index != expected_index:
                previous_index = current_index
                bpy.ops.constraint.move_down(
                    ctx, constraint=constraint.name, owner="BONE"
                )
                current_index = bone.constraints.find(constraint.name)
                if previous_index == current_index:
                    raise Exception(
                        "Failed to move the constraint {}. The bone {} is probably hidden".format(
                            constraint.name, bone.name
                        )
                    )
