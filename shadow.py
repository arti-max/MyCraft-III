from ursina import *
from threading import Thread
import time

class ShadowObject(Entity):
    def __init__(self, block, color=color.black, alpha=0.5, update_interval=0.5):
        super().__init__(
            model='cube',
            color=color,
            alpha=alpha,
            collider='box',
            parent=block   # Привязываем тень к блоку
        )
        self.block = block
        self.update_interval = update_interval
        self.enabled = True
        self.update_thread = Thread(target=self.periodic_update_shadow)
        self.update_thread.start()

    def periodic_update_shadow(self):
        while self.enabled:
            invoke(self.update_shadow, delay=0)  # Планируем обновление в основном потоке
            time.sleep(self.update_interval)

    def update_shadow(self):
        if not self.block:
            return

        # Выполняем raycast только тогда, когда это необходимо
        hit_info = raycast(self.block.world_position + Vec3(0, 0.5, 0), Vec3(0, -1, 0), distance=100)
        if hit_info.hit:
            # Расширяем тень до следующего блока
            self.position = Vec3(self.block.position.x, hit_info.world_point.y - 0.1, self.block.position.z)
            self.scale = Vec3(self.block.scale.x, abs(self.position.y - self.block.position.y) + 0.1, self.block.scale.z)
        else:
            # Сбрасываем тень, если под блоком пустота
            self.position = self.block.position
            self.scale = self.block.scale

    def destroy(self):
        self.enabled = False
        super().destroy()