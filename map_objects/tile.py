class Tile:
    """
    A tile on a map. Can be traversible and/or opaque.
    """
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.block_sight = block_sight if block_sight is not None else blocked
