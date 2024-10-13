from ursina import *
from player import Player
from world import World
from ui import UI
from configManager import ConfigManager
from soundManager import SoundManager
from entity import EntityObject
from mod import Mod
import random
import configparser
import os

app = Ursina(title="MyCraft III", icon="res/stone.ico", development_mode=False, borderless=False)
window.exit_button.enabled = False
window.cog_button.enabled = False
window.fullscreen = False
window.position = Vec2(100, 100)

mod_managers = []
# Создаем игрока
player = Player()
ui = UI()
config_manager = ConfigManager()
sound_manager = SoundManager()

# Загрузка музыки
sound_manager.load_music('m1', 'res/music/m1.ogg')
sound_manager.load_music('m2', 'res/music/m2.ogg')
sound_manager.load_music('m3', 'res/music/m3.ogg')

# Загрузка звуков для блоков
sound_manager.load_sound('grass', 'res/sounds/grass1.ogg')
sound_manager.load_sound('leaves', 'res/sounds/leaves1.ogg')
sound_manager.load_sound('stone', 'res/sounds/stone1.ogg')
sound_manager.load_sound('wood', 'res/sounds/wood1.ogg')
sound_manager.load_sound('planks', 'res/sounds/wood1.ogg')

# Начать случайное проигрывание музыки
sound_manager.play_random_music()

# Настройки мира
chunk_size = 4
world_size = 64
render_distance = int(config_manager.get_setting('render-distance'))
world_height = 8 # Настраиваемая высота мира
ver = "0.2.0"

save_file_def = f"level{config_manager.get_setting('save-file')}.dat"

x = random.randrange(1, world_size)
z = random.randrange(1, world_size)
player.position = (x, 10, z)


# Создаем мир с системой чанков и настройками высоты
world = World(player=player, chunk_size=chunk_size, world_size=world_size, render_distance=render_distance, world_height=world_height, save_file=save_file_def)

# Список доступных типов блоков
block_types = ['grass', 'stone', 'wood', 'leaves', 'planks']
selected_block_index = 0

scene.fog_color = color.rgb(200, 200, 200)  # Цвет тумана (светло-серый)
scene.fog_density = 0.2 / render_distance  # Плотность тумана, зависящая от расстояния прорисовки
camera.fog = True  # Включение тумана для камеры
camera.fog_density = 0.2 / render_distance  # Плотность тумана, зависящая от расстояния прорисовки


for mod_file in os.listdir('./mods/'):
    if mod_file.endswith('.lua'):
        mod_path = os.path.join('./mods/', mod_file)
        mod_manager = Mod(world, ui, sound_manager, block_types, player, EntityObject)
        mod_manager.load_script(mod_path)
        mod_managers.append(mod_manager)



skybox = Entity(
    model='sphere',  # используем сферическую модель для skybox
    scale=render_distance * 11,  # задаем размер skybox вручную
    texture='res/sky.png',  # укажите путь к вашей текстуре skybox
    double_sided=True
)
skybox.fog = True

blockImg = ui.add_image(image_path=f'res/{block_types[selected_block_index]}.png', position=(0.75, 0.43), scale=(0.1, 0.1))

menu_active = False  # Флаг для отображения меню

def toggle_menu():
    global menu_active
    menu_active = not menu_active
    if menu_active:
        show_menu()
        mouse.locked = False  # Разблокировать курсор
        player.mouse_sensitivity = (15, 15)
    else:
        hide_menu()
        mouse.locked = True  # Заблокировать курсор
        player.mouse_sensitivity = (155, 155)

def show_menu():
    global menu_active
    menu_active = True

    # Создаем кнопки меню
    ui.create_texture_button(
        # Gen New Level
        position=(0, 0.25),

        scale=(0.3, 0.1),
        on_click=generate_new_level
    )
    ui.create_texture_button(
        # Load Level
        position=(0, 0.1),

        scale=(0.3, 0.1),
        on_click=lambda: show_slots('load')
    )
    ui.create_texture_button(
        # Save Level
        position=(0, -0.05),

        scale=(0.3, 0.1),
        on_click=lambda: show_slots('save')  # Используем метод сохранения из класса World
    )
    ui.create_texture_button(
        # Resume
        position=(0, -0.2),

        scale=(0.3, 0.1),
        on_click=toggle_menu
    )



    ui.create_text(
        content='Generate New Level',
        position=(-0.113, 0.27),
        scale=1.5
    )

    ui.create_text(
        content='Load Level',
        position=(-0.06, 0.117),
        scale=1.5
    )

    ui.create_text(
        content='Save Level',
        position=(-0.06, -0.03),
        scale=1.5
    )

    ui.create_text(
        content='Resume',
        position=(-0.045, -0.18),
        scale=1.5
    )

def hide_menu():
    global blockImg
    global menu_active

    mouse.locked = True  # Заблокировать курсор
    player.mouse_sensitivity = (155, 155)
    # Удаляем все элементы интерфейса
    for element in ui.elements:
        destroy(element)
    ui.elements.clear()
    menu_active = False
    blockImg = ui.add_image(image_path=f'res/{block_types[selected_block_index]}.png', position=(0.74, 0.43), scale=(0.1, 0.1))

def generate_new_level():
        hide_menu()


        mod_managers.clear()

        print(f'Генерация нового уровня')
        
        # Отключаем игрока на время загрузки
        player.enabled = False
        
        # Загрузка мира из указанного файла
        world.load_level(1)
        
        # Включаем игрока после завершения загрузки

        for mod_file in os.listdir('./mods/'):
            if mod_file.endswith('.lua'):
                mod_path = os.path.join('./mods/', mod_file)
                mod_manager = Mod(world, ui, sound_manager, block_types, player, EntityObject)
                mod_manager.load_script(mod_path)
                mod_managers.append(mod_manager)

        player.enabled = True

        x = random.randrange(1, world_size)
        z = random.randrange(1, world_size)
        player.position = (x, 7, z)

def load_level(level_id):
    file_name = f'level{level_id}.dat'
    config_manager.update_setting('save-file', f'{level_id}')
    
    # Проверяем, существует ли файл сохранения
    if os.path.exists(file_name):
        hide_menu()

        print(f'Загрузка уровня {level_id} из файла {file_name}...')
        
        # Отключаем игрока на время загрузки
        player.enabled = False
        
        # Устанавливаем файл для загрузки
        world.set_load_file(file_name)
        
        # Загрузка мира из указанного файла
        world.load_level()
        
        # Включаем игрока после завершения загрузки

        player.enabled = True

        x = random.randrange(1, world_size)
        z = random.randrange(1, world_size)
        player.position = (x, 7, z)
        
        print(f'Уровень {level_id} успешно загружен.')

    else:
        print(f'Файл {file_name} не найден. Уровень {level_id} не может быть загружен.')

def show_slots(SlotType):
    hide_menu()
    global menu_active
    menu_active = True
    mouse.locked = False  # Заблокировать курсор
    player.mouse_sensitivity = (15, 15)
    # Проверка наличия файлов
    level_1_exists = os.path.exists('level1.dat')
    level_2_exists = os.path.exists('level2.dat')

    btn1Content = ''
    btn2Content = ''

    if SlotType == 'save':

        btn1Content = 'Level 1: ' + ('Saved' if level_1_exists else '-')
        btn2Content = 'Level 2: ' + ('Saved' if level_2_exists else '-')

        # Отображение состояния слотов

        ui.create_texture_button(
            position=(0, 0.2),
            on_click=lambda: save_level(1),
            scale=(0.3, 0.1)
        )

        ui.create_texture_button(
            position=(0, 0),
            on_click=lambda: save_level(2),
            scale=(0.3, 0.1)
        )

    elif SlotType == 'load':

        btn1Content = ('Level 1' if level_1_exists else '-')
        btn2Content = ('Level 2' if level_2_exists else '-')

        ui.create_texture_button(
            position=(0, 0.2),
            on_click=lambda: load_level(1),
            scale=(0.3, 0.1)
        )

        ui.create_texture_button(
            position=(0, 0),
            on_click=lambda: load_level(2),
            scale=(0.3, 0.1)
        )

    #====

    ui.create_texture_button(
        position=(0, -0.2),
        on_click=back_to_menu,
        scale=(0.3, 0.1)
    )


    ui.create_text(
        content='Back',
        position=(-0.03, -0.18),
        scale=1.5
    )

    ui.create_text(
        content=btn2Content,
        position=(-0.07, 0.02),
        scale=1.5
    )

    ui.create_text(
        content=btn1Content,
        position=(-0.07, 0.22),
        scale=1.5
    )

def back_to_menu():
    hide_menu()
    mouse.locked = False  # Заблокировать курсор
    player.mouse_sensitivity = (15, 15)
    show_menu()

def save_level(level_id):
    file_name = f'level{level_id}.dat'
    world.set_save_file(file_name)  # Устанавливаем файл сохранения
    print(f'сохранение уровня {level_id}...')
    world.save_world()  # Сохраняем текущий мир
    hide_menu()


# Обработка ввода
def input(key):
    global selected_block_index
    global EntityObject

    for mod_manager in mod_managers:
        if mod_manager.on_key:
            try:
                mod_manager.on_key(f"{key}")
            except Exception as e:
                print(f"Ошибка при выполнении onKey: {e}")

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
        player.gravity = 0.5
        player.position = (x, 10, z)
    elif key == 'escape':
        toggle_menu()

    elif key == 'g':
        Character = EntityObject(texture_folder='res/Entityes/char', position=player.position)

def place_block():
    selected_block_type = block_types[selected_block_index]
    # Получаем позицию блока, куда игрок смотрит
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit and not menu_active:
        # Рассчитываем позицию для нового блока
        position = hit_info.entity.position + hit_info.normal
        try:
            block_type = hit_info.entity.block_type
            world.create_block(position, selected_block_type)
        except:
            pass

def destroy_block():
    # Получаем позицию блока, который игрок пытается разрушить
    hit_info = raycast(camera.world_position, camera.forward, distance=5)
    if hit_info.hit and not menu_active:
        position = hit_info.entity.position
        try:
            block_type = hit_info.entity.block_type
            world.destroy_block(position)
            # Проигрываем звук в зависимости от типа блока
            sound_manager.play_sound(block_type)
        except:
            pass

def update_image_block():
    global selected_block_index
    global block_types
    global blockImg

    blockImg.texture = f'res/{block_types[selected_block_index]}.png'


# Обновление мира каждый кадр
def update():

    #Character.move(Vec3(0, 0, 1))  # Задать направление движения

    global selected_block_index
    global update_image_block

    if not menu_active:
        for mod_manager in mod_managers:
            mod_manager.update()

        skybox.position = player.position
        world.update()

        if held_keys['1']:
           selected_block_index = 0
           update_image_block()

        if held_keys['2']:
            selected_block_index = 1
            update_image_block()

        if held_keys['3']:
            selected_block_index = 2
            update_image_block()

        if held_keys['4']:
            selected_block_index = 3
            update_image_block()

        if held_keys['5']:
            selected_block_index = 4
            update_image_block()

def on_button_click():
    print("Button clicked!")

# Создание текста
ui.create_text(
    content=f"version: {ver}",
    position=(-0.78, 0.5),
    scale=2
)

# sun = DirectionalLight()
# sun.look_at(Vec3(-.5, -1, 0))  # Настройте направление света
# sun.scale = .00001

# # Настройте параметры теней
# sun.shadow_resolution = 2048
# sun.shadow_bias = 0.005

# # Создаём Ambient Light
# ambient = AmbientLight()
# ambient.color = color.rgb(90, 90, 90)  # Настройте интенсивность и цвет окружающего света
# ambient.parent = sun  # Можно связать Ambient Light с Directional Light, но необязательно

app.run()
