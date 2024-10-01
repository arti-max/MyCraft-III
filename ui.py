from ursina import *

class UI:
    def __init__(self):
        self.elements = []

    def create_texture_button(self, text='', texture='res/button.png', position=(0, 0), scale=(0.1, 0.05), on_click=None):
        # Создаем кнопку с заданной текстурой
        button = Button(
            text=text,
            model='quad',
            texture=texture,
            position=position,
            scale=scale,
            color=color.white,  # Убедитесь, что цвет белый, чтобы текстура отображалась корректно
            on_click=on_click
        )

        self.elements.append(button)
        return button

    def create_text(self, content, position=(0, 0), scale=1, color=color.white, font='res/font.ttf'):
        text = Text(
            text=content,
            position=position,
            scale=scale,
            color=color,
            font=font
        )
        self.elements.append(text)
        return text

    def add_image(self, image_path, position=(0.75, 0.45), scale=(0.1, 0.1)):

        image_entity = Entity(
            parent=camera.ui,
            model='cube',
            texture=image_path,
            position=position,
            scale=scale
        )
        self.elements.append(image_entity)
        return image_entity

