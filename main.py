from ursina import *
from player import Player
from world import World
from ui import UI
from configManager import ConfigManager
import random
import configparser



app = Ursina(title="MyCraft III", icon="res/stone.ico", development_mode=False, borderless = False)
window.exit_button.enabled = False
window.cog_button.enabled = False
window.fullscreen = False
window.position=Vec2(100, 100)

# Создаем игрока
player = Player()
ui = UI()
config_manager = ConfigManager()

# Настройки мира
chunk_size = 4
world_size = 64
render_distance = int(config_manager.get_setting('render-distance'))
world_height = 4  # Настраиваемая высота мира
ver = "0.1.0"

x = random.randrange(1, world_size)
z = random.randrange(1, world_size)
player.position = (x, 15, z)

# Создаем мир с системой чанков и настройками высоты
world = World(player=player, chunk_size=chunk_size, world_size=world_size, render_distance=render_distance, world_height=world_height)

# Список доступных типов блоков
block_types = ['grass', 'stone']
selected_block_index = 0

scene.fog_color = color.rgb(200, 200, 200)  # Цвет тумана (светло-серый)
scene.fog_density = 0.2 / render_distance  # Плотность тумана, зависящая от расстояния прорисовки
camera.fog = True  # Включение тумана для камеры
camera.fog_density = 0.2 / render_distance  # Плотность тумана, зависящая от расстояния прорисовки

skybox = Entity(
    model='sphere',  # используем сферическую модель для skybox
    scale=render_distance*11,  # задаем размер skybox вручную
    texture='res/sky.png',  # укажите путь к вашей текстуре skybox
    double_sided=True
)
skybox.fog = True

blockImg = ui.add_image(image_path=f'res/{block_types[selected_block_index]}.png', position=(0.75, 0.43), scale=(0.1, 0.1))

# Обработка ввода
def input(key):
    global selected_block_index

    if key == 'right mouse down':
        destroy_block()
    elif key == 'left mouse down':
        place_block()
    elif key == 'scroll up':
        selected_block_index = (selected_block_index + 1) % len(block_types)
        blockImg.texture = f'res/{block_types[selected_block_index]}.png'
    elif key == 'scroll down':
        selected_block_index = (selected_block_index - 1) % len(block_types)
        blockImg.texture = f'res/{block_types[selected_block_index]}.png'
    elif key == 'enter':
        world.save_world()  # Вызов функции сохранения мира при нажатии Enter
    elif key == 'r':
        x = random.randrange(1, world_size)
        z = random.randrange(1, world_size)
        player.position = (x, 15, z)

def place_block():
    selected_block_type = block_types[selected_block_index]
    # Получаем позицию блока, куда игрок смотрит
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        # Рассчитываем позицию для нового блока
        position = hit_info.entity.position + hit_info.normal
        world.create_block(position, selected_block_type)

def destroy_block():
    # Получаем позицию блока, который игрок пытается разрушить
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit:
        position = hit_info.entity.position
        world.destroy_block(position)

# Обновление мира каждый кадр
def update():
    skybox.position = player.position
    world.update()
    # Отображение текущего выбранного типа блока
    #print(f"Selected block type: {block_types[selected_block_index]}")

def on_button_click():
    print("Button clicked!")

# Создание кнопки в стиле Minecraft
# ui.create_texture_button(
#     position=(0, 0),
#     scale=(0.4, 0.2),
#     on_click=on_button_click,
#     texture='res/button.png'
# )

# Создание текста
ui.create_text(
    content=f"version: {ver}",
    position=(-0.78, 0.5),
    scale=2
)


app.run()
