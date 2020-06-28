from functools import cached_property


class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x1: int = x
        self.y1: int = y
        self.x2: int = x + w
        self.y2: int = y + h

    @cached_property
    def center(self):
        center_x = int((self.x2 + self.x1) / 2)
        center_y = int((self.y2 + self.y1) / 2)
        return (center_x, center_y)

    def intersect(self, other: "Rect"):
        x_intersection = (self.x2 >= other.x1) and (self.x1 <= other.x2)
        y_intersection = (self.y2 >= other.y1) and (self.y1 <= other.y2)
        return x_intersection and y_intersection
