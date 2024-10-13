from ursina import *
import random

entityID = 0

class EntityObject(Entity):
    def __init__(self, position=(0, 0, 0), texture_folder='res/Entityes/char', **kwargs):
        super().__init__(
            scale=(1, 1, 1),
            position=position,
            **kwargs
        )

        global entityID

        # Физика
        self.gravity = 0.5
        self.y_velocity = 0
        self.on_ground = False
        self.jump_height = 1.2 # Высота прыжка
        self.health = 1000
        self.entityID = entityID
        entityID += 1

        # Загрузка текстур
        self.head = Entity(
            parent=self,
            model='res/block',
            texture=f'{texture_folder}/head.png',
            scale=(0.23, 0.23, 0.23),
            position=(0, 1.5, 0)
        )
        self.body = Entity(
            parent=self,
            model='cube',
            texture=f'{texture_folder}/body.png',
            scale=(0.28, 1.4, 0.28),
            position=(0, 1, 0)
        )

        # Движение
        self.speed = 4
        self.direction = Vec3(0, 0, 0)
        self.is_moving = False

        # Поворот головы
        self.head_rotation_speed = 2
        self.head_rotation_target = 0

        print(f'New entity spawned at {self.position} with id: {self.entityID}')

    def jump(self):
        if self.on_ground:
            self.y_velocity = self.jump_height
            self.on_ground = False

    def move(self):
        # Используем поворот головы для направления движения
        self.direction = Vec3(cos(self.head.rotation_y), 0, sin(self.head.rotation_y))
        self.is_moving = True

    def update(self):
        self.health -= 2

        move_type = random.randrange(1, 6)
        if move_type == 1:
            self.rotate_head(random.randrange(-10, 10))
            self.move()
        elif move_type == 3:
            self.jump()


        if self.is_moving:
            self.position += self.direction * self.speed * time.dt
            if self.position.y < -2:
                self.position.y = 5

        # Проверка столкновения с землей
        hit_info = raycast(self.position, Vec3(0, -0.9, 0), distance=0.01)
        try:
            isPlayer = hit_info.entity.type
        except:
            isPlayer = 0

        if hit_info.hit and isPlayer==0:

            self.y_velocity = 0
            self.on_ground = True
        else:
            # Физика падения, только если под персонажем нет блока
            self.y_velocity -= self.gravity * time.dt
            self.y += self.y_velocity * time.dt
            self.on_ground = False

        # Поворот головы
        if self.head_rotation_target != 0:
            self.head.rotation_y = lerp(self.head.rotation_y, self.head_rotation_target, self.head_rotation_speed * time.dt)
            if abs(self.head.rotation_y - self.head_rotation_target) < 0.1:
                self.head_rotation_target = 0

        if(self.health < 1):
            print(f'Entity killed with id: {self.entityID}')
            destroy(self)


    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroy()

    def on_collision_enter(self, other):
        if isinstance(other, Block):
            self.is_moving = False
            self.direction = Vec3(0, 0, 0)

    def rotate_head(self, target_rotation):
        self.head_rotation_target += target_rotation*5