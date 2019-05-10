import bpy


class ActionMoveOperator(bpy.types.Operator):
    bl_idname = "actionman.action_move"
    bl_label = "Action Move"
    bl_options = {"INTERNAL"}

    direction: bpy.props.StringProperty()
    action: bpy.props.StringProperty()

    def execute(self, context):
        if self.direction == "UP":
            print("Moving {} UP".format(self.action))
        if self.direction == "DOWN":
            print("Moving {} DOWN".format(self.action))
        return {"FINISHED"}
