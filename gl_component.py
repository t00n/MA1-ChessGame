import numpy as np
from util import normalize

class MixinHasPosition:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y 
        self.z = z

    @property
    def position(self):
        return [self.x, self.y, self.z]

class MixinHasDirection:
    def __init__(self, x, y, z):
        self.dir_x = x
        self.dir_y = y
        self.dir_z = z

    @property
    def direction(self):
        return [self.dir_x, self.dir_y, self.dir_z]

class Mouse:
    def __init__(self):
        self.x = 0
        self.y = 0

class Camera(MixinHasPosition):
    def __init__(self):
        super(Camera, self).__init__(0,40,-40)

    # camera always looks to origin (0,0,0)
    @property
    def direction(self):
        return (-self.x, -self.y, -self.z)

    def go_right(self, dist=0.1):
        perpendicular = normalize([-self.z, self.x])
        previous_norm = np.linalg.norm([self.x, self.z])
        self.x += perpendicular[0] * dist
        self.z += perpendicular[1] * dist
        new_norm = np.linalg.norm([self.x, self.z])
        self.x *= previous_norm / new_norm
        self.z *= previous_norm / new_norm

    def go_up(self, dist=0.1):
        direction = normalize(self.direction)
        previous_norm = np.linalg.norm([self.x, self.y, self.z])
        self.x += direction[0] * dist
        self.y += dist
        self.z += direction[2] * dist
        if self.y < 1:
            self.y = 1
        new_norm = np.linalg.norm([self.x, self.y, self.z])
        self.x *= previous_norm / new_norm
        self.y *= previous_norm / new_norm
        self.z *= previous_norm / new_norm

class Light(MixinHasPosition):
    def __init__(self):
        super(Light, self).__init__(0,20,0)
        self._intensities = [1,1,1,1]

    def intensities():
        doc = "The intensities of the lights."
        def fget(self):
            return self._intensities
        def fset(self, value):
            self._intensities = value
        def fdel(self):
            del self._intensities
        return locals()
    intensities = property(**intensities())

    def set_x(self, val):
        self.x = val

    def set_y(self, val):
        self.y = val

    def set_z(self, val):
        self.z = val

    def set_R(self, val):
        self._intensities[0] = val/255

    def set_G(self, val):
        self._intensities[1] = val/255

    def set_B(self, val):
        self._intensities[2] = val/255