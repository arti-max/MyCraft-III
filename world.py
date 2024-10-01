from ursina import *
from chunk import Chunk
import asyncio
import pickle
import os

# Глобальный словарь для хранения состояния всех блоков в мире
world_dict = {}
world_list = []

class World(Entity):
    def __init__(self, player, chunk_size=4, world_size=64, render_distance=3, world_height=4):
        super().__init__()
        self.player = player
        self.chunk_size = chunk_size
        self.world_size = world_size
        self.render_distance = render_distance
        self.world_height = world_height
        self.chunks = {}
        self.loaded_chunks = set()
        self.last_player_chunk_position = None
        self.loop = asyncio.get_event_loop()
        self.initialize_world_blocks()
        self.update_chunks()  # Инициализация загрузки чанков

    def save_world(self):
        """Сохраняет состояние мира в файл level.dat."""
        with open('level.dat', 'wb') as file:
            pickle.dump(world_list, file)
        print("Мир сохранен в level.dat")

    def initialize_world_blocks(self):
        global world_dict, world_list

        # Проверяем, существует ли файл level.dat
        if os.path.exists('level.dat'):
            # Загружаем данные из файла
            with open('level.dat', 'rb') as file:
                world_list = pickle.load(file)

            # Конвертируем world_list обратно в world_dict
            for block in world_list:
                x, y, z, block_type = block
                world_dict[(x, y, z)] = block_type
            print("Мир загружен из level.dat")
            
        else:
            # Если файла нет, выполняем стандартную инициализацию
            for x in range(self.world_size):
                for y in range(self.world_height):  # Используем self.world_height
                    for z in range(self.world_size):
                        pos = (x, y, z)
                        if y < 3:
                            world_dict[tuple(pos)] = 'stone'
                        else:
                            world_dict[tuple(pos)] = 'grass'

            # Заполняем world_list на основе world_dict
            world_list = [[x, y, z, block_type] for (x, y, z), block_type in world_dict.items()]
            print("Мир инициализирован по умолчанию")

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