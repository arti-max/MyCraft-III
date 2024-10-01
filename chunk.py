from ursina import *
from block import Block

class Chunk(Entity):
    def __init__(self, position=(0, 0, 0), size=4, height=4):
        super().__init__()
        self.blocks = {}  # Хранение блоков в словаре
        self.size = size
        self.height = height
        self.position = position
        self.generate_chunk(position)
    
    def generate_chunk(self, start_position):
        from world import world_dict
        x_start, y_start, z_start = start_position
        #print(f"generating chunk in {x_start}, {y_start}, {z_start}")
        #print(world_dict)

        for x in range(self.size):
            for z in range(self.size):
                for y in range(self.height):
                    global_pos = (x_start + x, y_start + y, z_start + z)
                    tuple_global_pos = tuple(global_pos)

                    # Проверяем наличие блока в world_dict
                    if tuple_global_pos in world_dict and global_pos not in self.blocks:
                        #print(f"block_creating in {x}, {y}, {z}")
                        block_type = world_dict[global_pos]
                        block = Block(position=global_pos, block_type=block_type)
                        self.blocks[global_pos] = block
        
        self.update_visibility()

    def update_visibility(self):
        for block in self.blocks.values():
            block.visible = distance(block.world_position, camera.world_position) < 20

    def create_block(self, local_position, block_type, global_pos, world_dict):
        """Создает блок указанного типа в локальной позиции чанка."""
        if tuple(global_pos) not in self.blocks:
            block = Block(position=global_pos, block_type=block_type)
            self.blocks[tuple(global_pos)] = block
            self.update_global_level(global_pos, block_type, world_dict)

    def destroy_block(self, global_pos, world_dict):
        """Удаляет блок в локальной позиции чанка."""
        global_pos_tuple = tuple(global_pos)
        if global_pos_tuple in self.blocks:
            destroy(self.blocks[global_pos_tuple])
            del self.blocks[global_pos_tuple]
            # Удалите запись из world_dict
            self.update_global_level(global_pos, None, world_dict)

    def update_global_level(self, global_pos, block_type, world_dict):
        global_pos_tuple = tuple(global_pos)
        if block_type is None:
            # Удалите блок из world_dict
            if global_pos_tuple in world_dict:
                del world_dict[global_pos_tuple]
        else:
            # Обновите или добавьте новый блок в world_dict
            world_dict[global_pos_tuple] = block_type

    def destroy(self):
        for block in self.blocks.values():
            destroy(block)
        self.blocks.clear()
        destroy(self)

    def update(self):
        self.update_visibility()

    def load(self, world_dict):
        for global_pos, block_type in world_dict.items():
            chunk_pos = (global_pos[0] // self.size, global_pos[2] // self.size)
            if chunk_pos == (self.position[0] // self.size, self.position[2] // self.size):
                local_pos = (global_pos[0] % self.size, global_pos[1], global_pos[2] % self.size)
                self.create_block(local_pos, block_type, global_pos, world_dict)

    def unload(self, world_dict):
        for global_pos, block in self.blocks.items():
            global_pos_tuple = tuple(global_pos)
            if global_pos_tuple in world_dict:
                world_dict[global_pos_tuple] = block.block_type
            else:
                # Добавьте блок, если его нет в world_dict
                world_dict[global_pos_tuple] = block.block_type