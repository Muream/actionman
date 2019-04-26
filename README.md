# Action Man
Action Man is a simple tool allowing you to use blender actions to their full potential.  
This only works on armature objects, adapting the tool to work with other object would be really easy but I don't need that for my personal workflow so I haven't implemented it.

# Features
- Clean action: Removes all the animation data for a channel if the keyframes all have equal values.  
- Create/Update Constraints: Creates an action constraint on every object (usually bones) affected by the action.  
    All the settings above the `Create Constraints` will directly be used on the action constraint.  
    This operator also renames automatically the constraints if the action has been renamed  
- Delete all the actions constraints related to an action that aren't usefull (ie: constraints that exist on a bone that isn't affected by the action). this is usefull in two cases:  
    - You simplified an action and some bones aren't affectecte by it anymore.  
    - You forgot to click the `clean action` button before clicking the `create constraints` button.  

# Upcoming features
- [ ] Extract bones world transformation in a new action.
    This will be really usefull for making believable poses and then having multiple actions that when combined re-create that pose.
    For example splitting a smile in two actions: one with the translate Z data and the other with the translate X.
- [ ] Create mirror action
