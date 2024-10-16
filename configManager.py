import configparser
import os
from ursina import *

class ConfigManager:
    def __init__(self, config_file='config.cfg'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

        # Инициализация конфигурационного файла
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.create_default_config()
        else:
            self.config.read(self.config_file)
            self.ensure_all_settings()

    def update_setting(self, key, value):
        if key in self.config['Settings']:
            self.config['Settings'][key] = value
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        else:
            print('Setting not found')

    def create_default_config(self):
        self.config['Settings'] = {
            'render-distance': '2',
            'music':'100',
            'sounds':'100',
            'save-file':'1',
            'server-ip':'0.0.0.0',
            'server-port':'25565',
            'player-name':'player'
            # Добавьте другие параметры по умолчанию здесь
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def ensure_all_settings(self):
        # Проверяем наличие всех необходимых параметров
        default_settings = {
            'render-distance': '2',
            'music':'1',
            'sounds':'1',
            'save-file':'1',
            'server-ip':'0.0.0.0',
            'server-port':'25565',
            'player-name':'player'
            # Добавьте другие параметры по умолчанию здесь
        }

        updated = False
        for key, value in default_settings.items():
            if key not in self.config['Settings']:
                self.config['Settings'][key] = value
                updated = True

        if updated:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)

    def get_setting(self, key):
        return self.config['Settings'].get(key, None)