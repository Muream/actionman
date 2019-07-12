import bpy
import logging


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

        ordered_action_names = [a.name for a in armature.actionman_actions.values()]

        enforce_constraint_order(armature, action, ordered_action_names)
        enforce_constraint_order(armature, other_action, ordered_action_names)

        return {"FINISHED"}

def enforce_constraint_order(armature, action, ordered_action_names):
    bones = get_affected_bones(armature, action)
    current_active_bone = armature.bones.active
    for bone in bones:
        armature.bones.active = bone.bone
        reorder_constraints(bone, ordered_action_names)
    armature.bones.active = current_active_bone

def get_affected_bones(armature, action):
    armature_ob = bpy.data.objects[armature.name]
    return [b for b in armature_ob.pose.bones if b.name in action.groups]
    

def reorder_constraints(bone, ordered_action_names):
    
    def sort_constraint_as_actions(item):
        return ordered_action_names.index(item.name)

    constraints = [c for c in bone.constraints if c.type == 'ACTION']

    ordered_constraints = sorted(constraints, key=sort_constraint_as_actions)

    for expected_index, constraint in enumerate(ordered_constraints):

        ctx = bpy.context.copy()
        ctx['constraint'] = constraint

        current_index = bone.constraints.find(constraint.name)
        if current_index > expected_index:
            while current_index != expected_index:
                previous_index = current_index
                bpy.ops.constraint.move_up(ctx, constraint=constraint.name, owner='BONE')
                current_index = bone.constraints.find(constraint.name)
                if previous_index == current_index:
                    raise Exception("Failed to move the constraint {}. The bone {} is probably hidden".format(constraint.name, bone.name))
        elif current_index < expected_index:
            while current_index != expected_index:
                previous_index = current_index
                bpy.ops.constraint.move_down(ctx, constraint=constraint.name, owner='BONE')
                current_index = bone.constraints.find(constraint.name)
                if previous_index == current_index:
                    raise Exception("Failed to move the constraint {}. The bone {} is probably hidden".format(constraint.name, bone.name))