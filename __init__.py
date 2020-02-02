# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Action Man",
    "author": "Loïc Pinsard",
    "description": "Action Man lets you easily create and manage action constraint for a given action.",
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "category": "Rigging",
}

import bpy

from .operators import (
    CleanAction,
    ApplyActionChanges,
    DeleteUselessConstraints,
    DeleteAllConstraints,
    ActionMoveOperator,
)
from .panels import ActionManActionPanel
from .properties import ActionManItemProperty, ActionManProperties


CLASSES_TO_REGISTER = (
    # operators
    CleanAction,
    ApplyActionChanges,
    DeleteUselessConstraints,
    DeleteAllConstraints,
    ActionMoveOperator,
    # panels
    ActionManActionPanel,
    # properties
    ActionManItemProperty,
    ActionManProperties,
)


def select_active_action(self, context):
    armature = context.active_object
    index = self.actionman_active_action_index
    action = self.actionman_actions.values()[index].action
    armature.animation_data.action = action


def register():
    """Register the addon."""

    for cls in CLASSES_TO_REGISTER:
        bpy.utils.register_class(cls)

    bpy.types.Action.actionman = bpy.props.PointerProperty(
        type=ActionManProperties, name="Action Man Properties"
    )
    bpy.types.Armature.actionman_actions = bpy.props.CollectionProperty(
        type=ActionManItemProperty
    )
    bpy.types.Armature.actionman_active_action_index = bpy.props.IntProperty(
        update=select_active_action
    )


def unregister():
    """Unregister the addon."""

    for cls in CLASSES_TO_REGISTER:
        bpy.utils.unregister_class(cls)
