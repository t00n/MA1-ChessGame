import numpy as np
from util import normalize

class MixinHasPosition:
    def __init__(self, x, y, z):
        self._position = np.zeros(3)
        self.position = [x, y, z]

    def x_getter(self):
        return self._position[0]

    def x_setter(self, val):
        self._position[0] = val

    x = property(x_getter, x_setter)

    def y_getter(self):
        return self._position[1]

    def y_setter(self, val):
        if val >= 1:
            self._position[1] = val

    y = property(y_getter, y_setter)

    def z_getter(self):
        return self._position[2]

    def z_setter(self, val):
        self._position[2] = val

    z = property(z_getter, z_setter)

    def pos_getter(self):
        return self._position

    def pos_setter(self, value):
        self.x = value[0]
        self.y = value[1]
        self.z = value[2]

    position = property(pos_getter, pos_setter)

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
        return np.array([-self.x, -self.y, -self.z])

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
        new_norm = np.linalg.norm([self.x, self.y, self.z])
        self.x *= previous_norm / new_norm
        self.y *= previous_norm / new_norm
        self.z *= previous_norm / new_norm

    def go_forward(self, dist=0.1):
        self.position += self.direction * dist

class Light(MixinHasPosition):
    def __init__(self):
        super(Light, self).__init__(0,20,0)
        self._intensities = [1,1,1,1]
        self.attenuation = 0.001

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

class Animation:
    def __init__(self, chessman, destination, knight=False):
        self.chessman = chessman
        self.destination = np.array(destination)
        self.move = np.array(self.destination) - np.array(self.chessman.position)
        self.step = normalize(self.move)
        self.knight = knight

    def update(self, ms=0.05):
        if not self.knight:
            self.chessman.position += self.step * ms
        if self.destination[0] - self.chessman.position[0] < 0.01 \
        and self.destination[1] - self.chessman.position[1] < 0.01: 
            self.chessman.move(self.destination)
            return True
        return False
