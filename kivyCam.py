# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 19:24:24 2017

@author: Alexandre
"""

import cv2
import kivy
kivy.require('1.7.2')

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import platform
if platform.system() == 'Windows':
    from win32api import GetSystemMetrics
    win_width = GetSystemMetrics(0)
    win_height = GetSystemMetrics(1)
else:
    from kivy.core.window import Window
    win_width, win_height = Window.size

_CENTERS_ = [(x,y) for x in [0.05,0.5,0.95] for y in [0.05,0.5,0.95]]

class KivyCamera(Image):
    '''
    This image object updates itself automatically by querying the camera given
    as a parameter at instanciation. While many instances of this object can
    exist at once, only one of them should be running at any time. This is to
    prevent slowing down the application. Thus, when the <code>resume()<\code>
    method is called on one instance, the <code>suspend()<\code>
    '''
    
    def __init__(self, capture, fps, updateTexture = False, **kwargs):
        '''
        Constructor
        
        Arguments:
            capture: an OpenCV camera capture instance.
            fps: int, the desired number of frames per second.
            drawFeatures: boolean. If true, the features returned by the facial
                feature detector will be drawn onto every frame returned by the
                instance of this class.
            updateTexture: boolean. If true, the kivyCam instance, if used as a widget in a screen,
                will display the image captured by the camera, as well as the overlay if drawFeatures is enabled.
        '''
        
        super(KivyCamera, self).__init__(**kwargs)
        self.winSize = (win_width, win_height)
        self.fps = fps
        self.updateTexture = updateTexture
        
        self.capture = capture
        
        self.frame = None

    def update(self, dt):
        '''
        Scheduled task, executed every 1/fps seconds.
        
        Gets a frame from the capture object and stores it. Since the capture object buffers frames,
        querying frames as needed yields images that are not up-to-date. To get around this, when this
        method is scheduled and until it is unscheduled, frames are queried continuously and stored here,
        overwriting the previous one. This ensures that the returned frame is up-to-date.
        '''
        ret, frame = self.capture.read()
        if ret:
            self.frame = frame
            
            if self.updateTexture:
                # convert it to texture
                buf1 = cv2.flip(self.frame, 0)
                buf = buf1.tostring()
                image_texture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                # display image from the texture
                self.texture = image_texture
    
    def resume(self, obj):
        '''
        Resumes the updates of the instance of this class.
        '''
        self.updater = Clock.schedule_interval(self.update, 1.0 / self.fps)
    
    def suspend(self, obj):
        '''
        Stops the instance of this class from updating.
        '''
        self.updater.cancel()
        #Clock.unschedule(self.updater)
    
    def getFrame(self):
        '''
        Grabs, decodes and returns the next video frame.
        
        Returns:
            frame: Array-like, 3D. The latest frame from the camera. First
                and second dimensions are the image, third dimension is the
                color channels. Color channel order is BGR.
        '''
        
        return self.frame