from ursinanetworking import *
from ursina import Vec3, Entity
from entity import EntityObject

class PlayerNetwork:
    def __init__(self, ip, port):
        self.client = UrsinaNetworkingClient(ip, port)
        self.easy = EasyUrsinaNetworkingClient(self.client)
        self.isConnected = True
        self.other_players = {}
        self.SelfID = -1
        self.PlayersTargetPos = {}
        self.PlayersTargetRot = {}
        self.Players = {}
        self.isNetwork = False
        print('PlayerNetwork inited')

    def setIsNetwork(self):
        self.isNetwork = True


    # def reg_client_func(self):
    #     @self.client.event
    #     def onConnect():
    #         print("Подключено к серверу.")

    #     @self.client.event
    #     def onDisconnect():
    #         print("Отключено от сервера.")

    #     @self.client.event
    #     def setSpawnPos(pos):
    #         self.player.position = pos
    #         #self.world.update_chunks()

    #     @self.client.event
    #     def getWorldList(level):
    #         print('level list get suc')
    #         self.world.load_server_level(level)
    #         self.player.enabled = True
    #         self.isNetwork = True


    #     @self.easy.event
    #     def onReplicatedVariableUpdated(variable):
    #         self.PlayersTargetPos[variable.name] = {'pos': variable.content["position"], 'rot': variable.content["rotate"]}


    #     @self.easy.event
    #     def onReplicatedVariableRemoved(variable):
    #         variable_name = variable.name
    #         variable_type = variable.content["type"]
    #         if variable_type == "block":
                
    #             del LEVELBLOCKS[variable_name]
    #         elif variable_type == "player":
    #             destroy(Players[variable_name])
    #             del Players[variable_name]

    #     @self.easy.event
    #     def onReplicatedVariableCreated(variable):
    #         global Client
    #         variable_name = variable.name
    #         variable_type = variable.content["type"]
    #         if variable_type == "block":
    #             position = variable_name
    #             block_type = variable.content["block_type"]
    #             self.world.create_block(position, block_type)

    #         elif variable_type == "player":
    #             self.PlayersTargetPos[variable_name] = Vec3(5, 10, 5)
    #             self.Players[variable_name] = EntityObject(ai=False)
    #             if self.SelfID == int(variable.content["id"]):
    #                 self.Players[variable_name].color = color.red
    #                 self.Players[variable_name].visible = False
    #                 self.Players[variable_name].head_rotation_target = 0
    #         elif variable_type == "level1":
    #             self.player.enabled = True

    #         print(Players)

    #     @self.client.event
    #     def GetId(Id):
    #         self.SelfID = Id
    #         print(f"My ID is : {self.SelfID}")

    # def update(self):
    #     try:
    #         if self.Players[f"player_{self.SelfID}"].position != tuple(self.player.position + (0, 1.5, 0)):
    #             Client.send_message("MyPosition", tuple(self.player.position + (0, 1.5, 0)), self.player.rotation_y)
    #     except Exception as e2: print(e2)

    #     if self.player.position[1] < -13:
    #         self.player.position = (randrange(0, 64), 10, randrange(0, 64))

    #     for p in self.Players:
    #         try:
    #             self.Players[p].position = Vec3(self.PlayersTargetPos[p]['pos'])
    #             self.Players[p].position = Vec3(self.PlayersTargetPos[p]['pos'])
    #         except Exception as e: print(e)

    #     self.easy.process_net_events()
