# @version 0.3.10
"""
@title SimpleStorage
@author Throttle
"""

val: uint256

@external
def __init__(_val: uint256):
    self.val = _val


@external
def store(_val: uint256):
    self.val = _val

@external
@view
def get() -> uint256:
    return self.val