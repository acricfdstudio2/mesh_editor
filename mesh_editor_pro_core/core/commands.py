# ===================================================================================
# Python file : commands.py
# Description:
# Implements the Command design pattern to provide robust undo/redo
# functionality. This is pure backend logic with no GUI dependencies.
# ===================================================================================

class Command:
    """Base class for commands to enable a unified undo/redo interface."""
    def execute(self): raise NotImplementedError
    def undo(self): raise NotImplementedError

class AddActorCommand(Command):
    """Command to add a new actor to the scene."""
    def __init__(self, renderer, actor): self.renderer, self.actor = renderer, actor
    def execute(self): self.renderer.AddActor(self.actor)
    def undo(self): self.renderer.RemoveActor(self.actor)

class DeleteActorCommand(Command):
    """Command to remove an actor from the scene."""
    def __init__(self, renderer, actor): self.renderer, self.actor = renderer, actor
    def execute(self): self.renderer.RemoveActor(self.actor)
    def undo(self): self.renderer.AddActor(self.actor)

class ReplaceActorCommand(Command):
    """Command to replace one actor with another."""
    def __init__(self, renderer, new_actor, old_actor): self.renderer, self.new_actor, self.old_actor = renderer, new_actor, old_actor
    def execute(self): self.renderer.RemoveActor(self.old_actor); self.renderer.AddActor(self.new_actor)
    def undo(self): self.renderer.RemoveActor(self.new_actor); self.renderer.AddActor(self.old_actor)

class BooleanOperationCommand(Command):
    """Command for boolean operations."""
    def __init__(self, renderer, new_actor, old_actor1, old_actor2): self.renderer, self.new_actor, self.old_actor1, self.old_actor2 = renderer, new_actor, old_actor1, old_actor2
    def execute(self): self.renderer.RemoveActor(self.old_actor1); self.renderer.RemoveActor(self.old_actor2); self.renderer.AddActor(self.new_actor)
    def undo(self): self.renderer.RemoveActor(self.new_actor); self.renderer.AddActor(self.old_actor1); self.renderer.AddActor(self.old_actor2)