from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Final, Any

from . import base, commons, prim
from . import block


@dataclass(init=True)
class ShadowStatus:
    idx: int
    name: str

    def __repr__(self):
        return f"<ShadowStatus {self.name!r} ({self.idx})>"


class ShadowStatuses:
    # Not an enum so you don't need to do .value
    # Uh why?
    HAS_SHADOW: Final[ShadowStatus] = ShadowStatus(1, "has shadow")
    NO_SHADOW: Final[ShadowStatus] = ShadowStatus(2, "no shadow")
    OBSCURED: Final[ShadowStatus] = ShadowStatus(3, "obscured")

    @classmethod
    def find(cls, idx: int) -> ShadowStatus:
        for status in (cls.HAS_SHADOW, cls.NO_SHADOW, cls.OBSCURED):
            if status.idx == idx:
                return status

        if not 1 <= idx <= 3:
            raise ValueError(f"Invalid ShadowStatus idx={idx}")


class Input(base.BlockSubComponent):
    def __init__(self, _shadow: ShadowStatus | None = ShadowStatuses.HAS_SHADOW,
                 _value: prim.Prim | block.Block | list[block.Block] | str = None, _id: str = None,
                 _obscurer: prim.Prim | block.Block | str = None, *, _obscurer_id: str = None,
                 _block: block.Block = None):
        """
        An input for a scratch block
        https://en.scratch-wiki.info/wiki/Scratch_File_Format#Blocks:~:text=inputs,it.%5B9%5D
        """
        super().__init__(_block)

        if isinstance(_value, list):
            _value = _value[0]

        elif not (isinstance(_value, prim.Prim) or isinstance(_value, block.Block)):
            _value = prim.Prim(_value=_value, _primtype=prim.PrimTypes.STRING)

        if _obscurer is not None or _obscurer_id is not None:
            _shadow = ShadowStatuses.OBSCURED

            # Some defaulting if you are editing a project using python
            if isinstance(_value, block.Block):
                _value.is_shadow = True
            if isinstance(_obscurer, block.Block):
                _obscurer.is_shadow = False

        # If the shadow is None, we'll have to work it out later
        self.shadow = _shadow
        self.value: prim.Prim | block.Block = _value
        self.obscurer: prim.Prim | block.Block = _obscurer

        self._id = _id
        """
        ID referring to the input value. Upon project initialisation, this will be set to None and the value attribute will be set to the relevant object
        """
        self._obscurer_id = _obscurer_id
        """
        ID referring to the obscurer. Upon project initialisation, this will be set to None and the obscurer attribute will be set to the relevant block
        """

    def __repr__(self):
        if self._id is not None:
            return f"<Input<id={self._id!r}>"
        else:
            return f"<Input {self.value!r}>"

    @staticmethod
    def from_json(data: list):
        _shadow = ShadowStatuses.find(data[0])

        _value, _id = None, None
        if isinstance(data[1], list):
            _value = prim.Prim.from_json(data[1])
        else:
            _id = data[1]

        _obscurer_data = commons.safe_get(data, 2)

        _obscurer, _obscurer_id = None, None
        if isinstance(_obscurer_data, list):
            _obscurer = prim.Prim.from_json(_obscurer_data)
        else:
            _obscurer_id = _obscurer_data
        return Input(_shadow, _value, _id, _obscurer, _obscurer_id=_obscurer_id)

    def to_json(self) -> list:
        data = [self.shadow.idx]

        def add_pblock(pblock: prim.Prim | block.Block | None):
            """
            Adds a primitive or a block to the data in the right format
            """
            if pblock is None:
                return

            if isinstance(pblock, prim.Prim):
                data.append(pblock.to_json())

            elif isinstance(pblock, block.Block):
                data.append(pblock.id)

            else:
                warnings.warn(f"Bad prim/block {pblock!r} of type {type(pblock)}")

        # If there is an obscured shadow, it comes after the obscurer (i.e. obscurer comes before shadow if there is an obscurer)
        add_pblock(self.obscurer)
        add_pblock(self.value)

        return data

    def link_using_block(self):
        # Link to value
        if self._id is not None:
            new_value = self.sprite.find_block(self._id, "id")
            if new_value is not None:
                self.value = new_value
                self._id = None

        # Link to obscurer
        if self._obscurer_id is not None:
            new_block = self.sprite.find_block(self._obscurer_id, "id")
            if new_block is not None:
                self.obscurer = new_block
                self._obscurer_id = None

        # Link value to sprite
        if isinstance(self.value, prim.Prim):
            self.value.sprite = self.sprite
            self.value.link_using_sprite()

        # Link obscurer to sprite
        if self.obscurer is not None:
            self.obscurer.sprite = self.sprite


def gen_inp(value: Any | Input):
    if isinstance(value, Input):
        return value
    else:
        return Input(_value=value)
