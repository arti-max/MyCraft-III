from ursina import *
from ursina.shaders import *
from shadow import ShadowObject

class Block(Button):
    def __init__(self, position=(0, 0, 0), block_type='grass'):
        super().__init__(
            parent=scene,
            model='cube',
            color=color.white,
            position=position,
            collider='box',
            texture=f'res/{block_type}.png',
            scale=1,
            highlight_color=color.gray,
            shader=lit_with_shadows_shader  # Используем шейдер с тенями
            # pressed_color=color.red      # Цвет при нажатии
        )
        self.block_type = block_type
        self.type = 0
        self.breakable = True
        #self.shadow = ShadowObject(self)  # Создаем оптимизированный объект тени

    def destroy(self):
        #self.shadow.destroy()  # Удаляем объект тени при удалении блока
        super().destroy()

    # def on_click(self):
    #     # Логика, которая выполняется при нажатии на блок
    #     print(f"Block of type {self.block_type} at {self.position} clicked!")
    #     # Можно добавить логику для разрушения или изменения блока