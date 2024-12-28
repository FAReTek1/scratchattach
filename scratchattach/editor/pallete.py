"""
Collection of block information, stating input/field names and opcodes
New version of sbuild.py

May want to completely change this later
"""
from __future__ import annotations

from typing import Self, Any, overload

from . import block, sprite, mutation, field, inputs, build_defaulting


class _Block(block.Block):
    _opc: str = None
    _init_attrs: dict[str, Any] = {}

    # Overloaded function to provide arg/kwarg hinting
    @overload
    def __init__(self, _shadow: bool = False, _top_level: bool = None,
                 _mutation: mutation.Mutation = None, _fields: dict[str, field.Field] = None,
                 _inputs: dict[str, inputs.Input] = None, x: int = 0, y: int = 0, pos: tuple[int, int] = None,

                 _next: block.Block = None, _parent: block.Block = None,
                 *, _next_id: str = None, _parent_id: str = None,
                 _sprite: sprite.Sprite = build_defaulting.SPRITE_DEFAULT): ...

    def __init__(self, **kwargs):
        for k, v in self._init_attrs.items():
            if k not in kwargs:
                kwargs[k] = v

        super().__init__(_opcode=self._opc, **kwargs)


class Motion:
    class MoveSteps(_Block):
        _opc = "motion_movesteps"

        def set_steps(self, _inp: inputs.Input | Any) -> Self:
            return self.add_input("STEPS", _inp)

    class TurnRight(_Block):
        _opc = "motion_turnright"

        def set_degrees(self, _inp: inputs.Input | Any) -> Self:
            return self.add_input("DEGREES", _inp)

    class TurnLeft(_Block):
        _opc = "motion_turnleft"

        def set_degrees(self, _inp: inputs.Input | Any) -> Self:
            return self.add_input("DEGREES", _inp)

    class GoTo(_Block):
        _opc = "motion_goto"

        def set_to(self, _inp: inputs.Input | Any) -> Self:
            return self.add_input("TO", _inp)

    class GoToMenu(_Block):
        _opc = "motion_goto_menu"
        _init_attrs = _Block._init_attrs.copy()
        _init_attrs.update({
            "_shadow": True
        })

        def set_to(self, _fld: field.Field | Any) -> Self:
            return self.add_field("TO", _fld)

    class XPosition(_Block):
        _opc = "motion_xposition"

    class YPosition(_Block):
        _opc = "motion_yposition"
