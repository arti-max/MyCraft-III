from ursina import *
from chunk import Chunk
import asyncio
import pickle
import os
from noise import pnoise2 
from structures import Structures  

# Глобальный словарь для хранения состояния всех блоков в мире
world_dict = {}
world_list = []

class World(Entity):
    def __init__(self, player, chunk_size=4, world_size=64, render_distance=3, world_height=20, save_file='level1.dat'):
        super().__init__()
        self.player = player
        self.chunk_size = chunk_size
        self.world_size = world_size
        self.render_distance = render_distance
        self.world_height = world_height
        self.chunks = {}
        self.loaded_chunks = set()
        self.last_player_chunk_position = None
        self.save_file = save_file
        self.loop = asyncio.get_event_loop()
        self.structures = Structures()  # Инициализируем класс Structures
        self.initialize_world_blocks()
        self.update_chunks()

    def set_load_file(self, file_name):
        self.save_file = file_name

    def load_level(self, params=0):
        global world_dict
        world_dict.clear()

        for chunk_key in list(self.loaded_chunks):
            self.unload_chunk(chunk_key)

        # Очистка текущих данных мира
        self.chunks.clear()
        self.loaded_chunks.clear()

        # Загрузка нового уровня из выбранного файла
        if self.save_file and os.path.exists(self.save_file) and params == 0:
            with open(self.save_file, 'rb') as file:
                world_list = pickle.load(file)
            for block in world_list:
                x, y, z, block_type = block
                world_dict[(x, y, z)] = block_type


            self.update_chunks()
            print(f"Level loaded from {self.save_file}")

        elif params==1:
            print('old level clearing...')
            self.initialize_world_blocks(1)
            self.update_chunks()
            print('New level succefully generated')

        else:
            print(f"File {self.save_file} not exists")

    def save_world(self):
        """Сохраняет состояние мира в файл level.dat."""
        with open(self.save_file, 'wb') as file:
            pickle.dump(world_list, file)
        print(f"Level saved in {self.save_file}")

    def set_save_file(self, file_name):
        self.save_file = file_name
        print(f"Save file changed to {self.save_file}")

    def initialize_world_blocks(self, params=0):
        global world_dict, world_list

        if os.path.exists(self.save_file) and params == 0:
            with open(self.save_file, 'rb') as file:
                world_list = pickle.load(file)
                #print(world_list)

            for block in world_list:
                x, y, z, block_type = block
                world_dict[(x, y, z)] = block_type
            print("Мир загружен из level.dat")
            
        else:
            # Инициализация мира с использованием шума Перлина
            scale = 50.0  # Масштаб для шума Перлина
            octaves = 35  # Количество октав
            persistence = 0.5  # Стойкость
            lacunarity = 2.0  # Лакунарность

            for x in range(self.world_size):
                for z in range(self.world_size):
                    height = int((pnoise2(x / scale, z / scale, octaves=octaves, 
                                          persistence=persistence, lacunarity=lacunarity) + 1) / 2 * self.world_height)
                    height = max(1, height)

                    for y in range(height):
                        pos = (x, y, z)
                        if y < height - 1:
                            world_dict[tuple(pos)] = 'stone'
                        else:
                            world_dict[tuple(pos)] = 'grass'

                    # Добавляем деревья с некоторой вероятностью
                    if height > 1 and random.random() < 0.02:  # 10% шанс появления дерева
                        self.add_structure('tree', x, height, z)

            world_list = [[x, y, z, block_type] for (x, y, z), block_type in world_dict.items()]
            print("Level initialized using perlin noise")
            
    def add_structure(self, structure_name, x, y, z):
        structure = self.structures.get_structure(structure_name)
        for (dx, dy, dz), block_type in structure.items():
            world_dict[(x + dx, y + dy, z + dz)] = block_type

    def get_chunk_position(self, world_position):
        return (
            int(world_position[0] // self.chunk_size),
            int(world_position[2] // self.chunk_size)
        )

    def update_chunks(self):
        player_chunk_position = self.get_chunk_position(self.player.position)

        if player_chunk_position == self.last_player_chunk_position:
            return

        self.last_player_chunk_position = player_chunk_position

        # Загрузка новых чанков асинхронно
        tasks = []
        for x in range(-self.render_distance, self.render_distance + 1):
            for z in range(-self.render_distance, self.render_distance + 1):
                chunk_x = player_chunk_position[0] + x
                chunk_z = player_chunk_position[1] + z
                chunk_key = (chunk_x, chunk_z)

                if chunk_key not in self.loaded_chunks:
                    if 0 <= chunk_x < self.world_size // self.chunk_size and 0 <= chunk_z < self.world_size // self.chunk_size:
                        tasks.append(self.load_chunk(chunk_key))

        # Выполнение всех задач загрузки
        if tasks:
            self.loop.run_until_complete(asyncio.gather(*tasks))

        # Отгрузка старых чанков
        for chunk_key in list(self.loaded_chunks):
            if not self.is_chunk_in_render_distance(chunk_key, player_chunk_position):
                self.unload_chunk(chunk_key)

    async def load_chunk(self, chunk_key):
        await asyncio.sleep(0)  # Симуляция асинхронной операции
        chunk_position = (chunk_key[0] * self.chunk_size, 0, chunk_key[1] * self.chunk_size)
        chunk = Chunk(position=chunk_position, size=self.chunk_size, height=self.world_height)
        self.chunks[chunk_key] = chunk
        self.loaded_chunks.add(chunk_key)
        chunk.load(world_dict)  # Загружаем состояние из глобального словаря world_dict

    def unload_chunk(self, chunk_key):
        if chunk_key in self.chunks:
            chunk = self.chunks.pop(chunk_key)
            chunk.unload(world_dict)  # Сохраняем состояние в глобальный словарь world_dict
            chunk.destroy()  # Удаляем все блоки и сам чанк
            self.loaded_chunks.remove(chunk_key)

    def is_chunk_in_render_distance(self, chunk_key, player_chunk_position):
        dx = chunk_key[0] - player_chunk_position[0]
        dz = chunk_key[1] - player_chunk_position[1]
        return dx**2 + dz**2 <= self.render_distance**2

    def destroy_block(self, position):
        chunk_coords = self.get_chunk_coords(position)
        if chunk_coords in self.chunks:
            chunk = self.chunks[chunk_coords]
            local_position = self.get_local_position(position)
            # Удаляем блок из чанка и world_list
            chunk.destroy_block((position[0], position[1], position[2]), world_dict)
            self.remove_from_world_list(position)

    def create_block(self, position, block_type):
        chunk_coords = self.get_chunk_coords(position)
        if chunk_coords in self.chunks:
            chunk = self.chunks[chunk_coords]
            local_position = self.get_local_position(position)
            # Создаем блок в чанке и добавляем в world_list
            chunk.create_block(local_position, block_type, (position[0], position[1], position[2]), world_dict)
            self.add_to_world_list(position, block_type)

    def add_to_world_list(self, position, block_type):
        global world_list
        entry = [position[0], position[1], position[2], block_type]
        if entry not in world_list:
            world_list.append(entry)

    def remove_from_world_list(self, position):
        global world_list
        world_list = [entry for entry in world_list if entry[:3] != list(position)]
        #print(world_list)

    def get_chunk_coords(self, position):
        return int(position[0] // self.chunk_size), int(position[2] // self.chunk_size)

    def get_local_position(self, position):
        return int(position[0] % self.chunk_size), int(position[1]), int(position[2] % self.chunk_size)

    def update(self):
        self.update_chunks()