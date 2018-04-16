"""
Created on 2018-03-18
@author: Alexandre Drouin-Picaro
@copyright: innodem neurosciences
"""

import csv
import cv2
import time

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from os.path import join, isdir
from os import makedirs

_FPS = 60

INSTRUCTIONS_ = {'Saccades':'Saccade instructions',
                 'Smooth Pursuit':'Smooth pursuit instructions',
                 'Fixation':'Fixation instructions',
                 'Antisaccades':'Antisaccade instructions',
                 'Landscape':'Landscape instructions',
                 'Face':'Face instructions'}

class InstructionScreen(FloatLayout):
    def __init__(self, stimName, **kwargs):
        super(InstructionScreen, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(0,0,0,1)
            self.rect = Rectangle(pos = self.pos, size = self.size)
        self.bind(pos=self._updateRect, size=self._updateRect)
        
        startButton = Button(text = 'Start', size_hint = (0.1,0.1), pos_hint = {'center_x':0.5, 'center_y':0.1})
        instructionLabel = Label(text = INSTRUCTIONS_[stimName], size_hint = (1, 0.8), pos_hint = {'center_x':0.5, 'center_y':0.6})
        
        startButton.bind(on_release = self.removeSelf)
        
        self.add_widget(startButton)
        self.add_widget(instructionLabel)
        
    def removeSelf(self, obj):
        self.parent.removeInstructions()
    
    def _updateRect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class StimInterface(Screen):
    def __init__(self, capture, param, screenInfo, baseDir, stimName, **kwargs):
        super(StimInterface, self).__init__(**kwargs)
        
        self.capture = capture
        self.param = param
        self.winWidth, self.winHeight, self.milWidth, self.milHeight, self.ppc = screenInfo
        self.saveDir = join(baseDir, stimName)
        self.nextStim = None
        
        self.captureFlag = True
        
        if not isdir(self.saveDir):
            makedirs(self.saveDir)
        
        self.instructions = InstructionScreen(stimName)
        self.add_widget(self.instructions)
        
        self.data = [self.winWidth, self.winHeight, self.milWidth, self.milHeight, self.ppc]
    
    def toStimMenu(self, obj):
        self.parent.transition = NoTransition()
        self.parent.current = 'stims'
    
    def toNextStim(self, obj):
        self.captureFlag = False
        if self.nextStim is None:
            self.parent.transition = NoTransition()
            self.parent.current = 'stims'
        else:
            self.parent.transition = NoTransition()
            self.parent.current = self.nextStim
    
    def removeInstructions(self):
        self.remove_widget(self.instructions)
        self.collect()
    
    def saveData(self):
        i = 1
        if self.capture.isOpened():
            while self.captureFlag:
                ret, image = self.capture.read()
                timestamp = time.time()
                if ret:
                    metaData = ['%05d.jpg' % i, timestamp]+self.data
                    with open(join(self.saveDir, 'metadata.csv'), 'ab') as f:
                        writer = csv.writer(f, delimiter = ',')
                        writer.writerow(metaData)
                    cv2.imwrite(join(self.saveDir, '%05d.jpg' % i), image)
                    i += 1