# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 19:42:41 2017

@author: Alexandre

This screen is meant to verify the positioning of the field of view of the
camera, to ensure the user's face is centrally positioned.
"""

import kivy
kivy.require('1.7.2')

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

class CheckCamScreen(Screen):
    '''
    This window displays a video feed from the camera. Shows the position
    of the lower eyelids and center of the eyebrows of the user, in green.
    Show the position of points on the nose and jaw in pink.
    These are detected by the kivyCam object used by this window.
    
    This window contains two buttons:
        Back: goes back to the main window
        Launch Calibration: Launches the data collection for the calibration
                            procedure.
    '''
    
    def __init__(self, kvCam, previousScreen, **kwargs):
        '''
        Constructor method
        '''
        super(CheckCamScreen, self).__init__(**kwargs)
        
        self.kvCam = kvCam
        self.previousScreen = previousScreen
        
        layout = FloatLayout()
        back_btn = Button(text = 'Back',
                          size_hint = (0.25, 0.1),
                          pos_hint={'center_x': 0.5, 'center_y':0.05})
        
        back_btn.bind(on_release = self.toPreviousScreen)
        
        camCanvas = BoxLayout(size_hint = (1.0, 0.8),
                              pos_hint = {'center_x':.5, 'center_y':.5})
        camCanvas.add_widget(kvCam)
        
        layout.add_widget(back_btn)
        layout.add_widget(camCanvas)
        
        self.add_widget(layout)
        
        '''
        On entering this window, starts the camera. On exiting this window,
        stops the camera. This is done to prevent the camera processes from
        executing when not needed, which would slow down the application.
        '''
        self.bind(on_pre_enter = self.kvCam.resume)
        self.bind(on_leave = self.kvCam.suspend)
    
    def toPreviousScreen(self, obj):
        '''
        Event bound to the 'Back' button. Sets the main window as the active
        window.
        '''
        self.parent.transition.direction = 'right'
        self.parent.current = self.previousScreen
