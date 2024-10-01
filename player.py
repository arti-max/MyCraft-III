from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = 0.5
        self.collider = BoxCollider(self, size=Vec3(1, 1, 1))
        self.mouse_sensitivity = (155, 155)
        self.camera_pivot.y = 1.5
        self.jump_height = 1.2
        self.cursor.texture = 'res/cursor.png'
        self.cursor.color = color.white
        self.cursor.scale = 0.02
