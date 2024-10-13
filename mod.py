# mod.py

from lupa import LuaRuntime
from ursina import *

class Mod:
    def __init__(self, world, ui_manager, sound_manager, block_types, player, eo):
        self.world = world
        self.ui_manager = ui_manager
        self.sound_manager = sound_manager
        self.block_types = block_types
        self.EntityObject = eo
        self.player = player
        self.lua = LuaRuntime(unpack_returned_tuples=True)

        self.on_start = None
        self.on_update = None
        self.on_key = None 

        self.register_functions()


    def register_functions(self):
        # Определяем функции, которые будут доступны из Lua

        def setBlk(x, y, z, blockID):
            # Преобразование blockID в block_type
            if blockID < len(self.block_types):
                block_type = self.block_types[blockID]
                self.world.create_block((x, y, z), block_type)
                print(f"Установка блока {block_type} в позиции ({x}, {y}, {z})")
            else:
                print(f"Некорректный blockID: {blockID}")

        def removeBlk(x, y, z):
            self.world.destroy_block((x, y, z))
            print(f"Удаление блока в позиции ({x}, {y}, {z})")

        def spwnEntity(x, y, z):
            entity = self.EntityObject(position=(x, y, z))
            print(f"Создание сущности в позиции ({x}, {y}, {z})")

        def playSound(sound_path):
            self.sound_manager.play_sound(sound_path)
            print(f"Playing sound: {sound_path}")

        def createUi(ui_type, position, scale, params):
            position = (position['x'], position['y'])
            scale = Vec2(scale['x'], scale['y'])
            if ui_type == 1:
                button = self.ui_manager.create_texture_button(texture=params, position=position, scale=scale)
            elif ui_type == 2:
                text = self.ui_manager.create_text(content=params, position=position, scale=scale.x)
            elif ui_type == 3:
                image = self.ui_manager.add_image(image_path=params, position=position, scale=scale)
            print(f"Creating UI with type {ui_type}, position {position}, scale {scale} and params {params}")

        def addBlock(texture_path, sound_path):
            self.sound_manager.load_sound(texture_path, sound_path)
            # Добавление нового типа блока
            self.block_types.append(texture_path)
            block_id = self.block_types.index(texture_path)
            print(f"Adding block with ID {block_id} and texture {texture_path}")
            return block_id


        def getPlayerX():
            return self.player.position.x

        def getPlayerY():
            return self.player.position.y

        def getPlayerZ():
            return self.player.position.z

        def setPlayerX(x):
            self.player.position.x = x

        def setPlayerY(y):
            self.player.position.y = y

        def setPlayerZ(z):
            self.player.position.z = z

        def getBlockAt(x, y, z):
            block_type = self.world.get_block_type_at_position((x, y, z))
            return block_type if block_type else 'air'  # Возвращаем 'air', если блока нет

        def typeToID(block_type):
            if block_type in self.block_types:
                return self.block_types.index(block_type)
            else:
                return -1  # Возвращаем -1, если тип блока не найден

        def addMusic(music_path):
            music_name = music_path.split('/')[-1]  # Используем имя файла как ключ
            self.sound_manager.load_music(music_name, music_path)
            print(f"Музыка {music_path} добавлена в список.")

        # Регистрируем новые функции в Lua
        self.lua.globals().setBlk = setBlk
        self.lua.globals().removeBlk = removeBlk
        self.lua.globals().spwnEntity = spwnEntity
        self.lua.globals().playSound = playSound
        self.lua.globals().createUi = createUi
        self.lua.globals().addBlock = addBlock
        self.lua.globals().getPlayerX = getPlayerX
        self.lua.globals().getPlayerY = getPlayerY
        self.lua.globals().getPlayerZ = getPlayerZ
        self.lua.globals().setPlayerX = setPlayerX
        self.lua.globals().setPlayerY = setPlayerY
        self.lua.globals().setPlayerZ = setPlayerZ
        self.lua.globals().getBlockAt = getBlockAt
        self.lua.globals().typeToID = typeToID
        self.lua.globals().addMusic = addMusic

        # Также регистрируем onKey
        self.lua.globals().onKey = None  # Инициализируем как None

    def load_script(self, script_path):
        # Загружаем и выполняем Lua-скрипт
        with open(script_path, 'r') as lua_file:
            lua_code = lua_file.read()

        try:
            self.lua.execute(lua_code)
            # Получаем функции
            self.on_start = self.lua.globals().onStart
            self.on_update = self.lua.globals().onUpdate
            self.on_key = self.lua.globals().onKey  # Добавляем onKey

            # Вызываем onStart, если она определена
            if self.on_start is not None:
                self.on_start()
            else:
                print("Функция onStart не определена в Lua-скрипте.")
        except Exception as e:
            print(f"Ошибка при выполнении Lua-скрипта: {e}")
            raise

    def update(self):
        # Вызываем onUpdate каждое обновление игры, если функция определена
        if self.on_update:
            try:
                self.on_update()
            except Exception as e:
                print(f"Ошибка при выполнении onUpdate: {e}")