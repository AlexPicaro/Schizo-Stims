"""
Created on 2018-03-20
@author: Alexandre Drouin-Picaro
@copyright: innodem neurosciences
"""

import cv2
import numpy as np
import random
import threading

from interface import StimInterface
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

from functools import partial

_SPST = 2 #Seconds per stim total
_STSS = 1.5 #Seconds to show stim

class Antisaccades(StimInterface):
    
    def __init__(self, capture, param, screenInfo, saveDir, **kwargs):
        super(Antisaccades, self).__init__(capture, param, screenInfo, saveDir, 'Antisaccades', **kwargs)
        
        self.image = Image()
        layout = BoxLayout()
        layout.add_widget(self.image)
        self.add_widget(layout, index = 1)
        
        self.stims = [['pro', 'left']]*30 + [['pro', 'right']]*30 + [['anti', 'left']]*30 + [['anti', 'right']]*30
        
        random.shuffle(self.stims)
        
        self.xl, self.xc, self.xr = int(0.2*self.winWidth), int(0.5*self.winWidth), int(0.8*self.winWidth)
        self.r = int(min(0.02*self.winHeight, 0.02*self.winWidth))
        
        self.data += ['N/A']
    
    def collect(self):
        self.collectionThread = threading.Thread(target=self.saveData)
        self.collectionThread.start()
        
        self.slideCount = 0
        Clock.schedule_interval(self._updateTexture, _SPST)
    
    def _updateTexture(self, dt):
        stimSide = self.stims[self.slideCount]
        print stimSide
        self.data[-1] = stimSide
        with self.canvas:
            slide = self._makeSlide('None')
            slide = cv2.flip(slide, 0)
            
            buf = slide.tostring()
            image_texture = Texture.create(size=(slide.shape[1], slide.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = image_texture
        
        if not stimSide == 'None':
            Clock.schedule_once(partial(self._showStim, stimSide), _STSS)
        
        self.slideCount += 1
        if self.slideCount == len(self.stims):
            Clock.schedule_once(self.toNextStim, float(_SPST))
            return False
    
    def _showStim(self, stimSide, dt):
        with self.canvas:
            slide = self._makeSlide(stimSide)
            slide = cv2.flip(slide, 0)
            
            buf = slide.tostring()
            image_texture = Texture.create(size=(slide.shape[1], slide.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = image_texture
    
    def _makeSlide(self, stim):
        slide = np.ones((self.winHeight, self.winWidth, 3), np.uint8)*(128)
        cv2.circle(slide, (self.xc, self.winHeight/2), self.r, (255,255,255), -1)
        color = (0,255,0) if stim[0] == 'pro' else (0,0,255)
        if stim[1] == 'right':
            cv2.circle(slide, (self.xr, self.winHeight/2), self.r, color, -1)
        elif stim[1] == 'left':
            cv2.circle(slide, (self.xl, self.winHeight/2), self.r, color, -1)
        
        return slide