# -*- coding: utf-8 -*-
"""
Created on 2018-04-13
@author: Alexandre Drouin-Picaro
"""

import kivy
kivy.require('1.7.2')

from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')
Config.write()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from mainScreen import MainScreen
from kivyCam import KivyCamera
from checkCamScreen import CheckCamScreen

FPS = 30

class CollectionApp(App):
    def build(self):
        self.manager = ScreenManager()
        
        mainScreen = MainScreen(name = 'main')
        self.manager.add_widget(mainScreen)
        self.manager.add_widget(CheckCamScreen(KivyCamera(mainScreen.capture, FPS, True), 'main', name = 'check_cam'))
        
        return self.manager
    
    def on_stop(self):
        App.on_stop(self)

if __name__ == '__main__':
    CollectionApp().run()