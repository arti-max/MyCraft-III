from ursina import *

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
            highlight_color=color.gray  # Цвет подсветки при наведении
            #pressed_color=color.red      # Цвет при нажатии
        )
        self.block_type = block_type

    # def on_click(self):
    #     # Логика, которая выполняется при нажатии на блок
    #     print(f"Block of type {self.block_type} at {self.position} clicked!")
    #     # Можно добавить логику для разрушения или изменения блока
