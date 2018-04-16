# -*- encoding: utf-8 -*-
"""
Created on 2018-04-13
@author: Alexandre Drouin-Picaro
"""

import cv2
import random

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle

try:
    import pylink
except:
    print 'No pylink library was found'

CALIB_TEXT = \
'Please turn to the EyeLink user interface to calibrate\n'\
' the eye tracker. Once the calibration procedure is done,\n'\
' hit "ESCAPE". This will bring you back to the EyeLink setup\n'\
' screen and will allow this program to resume its execution.'

class PartialLayout(FloatLayout):
    
    def __init__(self, **kwargs):
        super(PartialLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0,0,0,1)
            self.rect = Rectangle(size = self.size, pos = self.pos)
        self.bind(pos = self._adjustRect, size = self._adjustRect)
    
    def _adjustRect(self, instance, _):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class AntisaccadeDesigner(FloatLayout):
    
    def __init__(self, **kwargs):
        super(AntisaccadeDesigner, self).__init__(**kwargs)
        with self.canvas.before:
            Color(.2, .2, .2, 1)
            self.rect = Rectangle(size = self.size, pos = self.pos)
        self.bind(size = self._adjustRect, pos = self._adjustRect)
        
        self.addButton = Button(text = '+', size_hint = (0.095, .99), pos_hint = {'center_x': 0.95, 'center_y': 0.5})
        label = Label(text = 'Antisaccade', size_hint = (0.895, .99), pos_hint = {'center_x': 0.45, 'center_y': 0.5})
         
        self.add_widget(label)
        self.add_widget(self.addButton)
    
    def _adjustRect(self, instance, _):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class VisualSearchDesigner(FloatLayout):
    
    def __init__(self, **kwargs):
        super(VisualSearchDesigner, self).__init__(**kwargs)
        with self.canvas.before:
            Color(.2, .2, .2, 1)
            self.rect = Rectangle(size = self.size, pos = self.pos)
        self.bind(size = self._adjustRect, pos = self._adjustRect)
        
        label = Label(text = 'Visual Search', size_hint = (0.895, 0.495), pos_hint = {'center_x': 0.45, 'center_y': 0.75})
        self.addButton = Button(text = '+', size_hint = (0.095, 0.495), pos_hint = {'center_x': 0.95, 'center_y': 0.75})
        
        self.mainContrastButton = Button(text = '1 Contrast', size_hint = (0.495, 0.495), pos_hint = {'center_x': 0.25, 'center_y': 0.25})
        self.mainConditionButton = Button(text = '24 Stimuli', size_hint = (0.495, 0.495), pos_hint = {'center_x': 0.75, 'center_y': 0.25})
        
        self.add_widget(label)
        self.add_widget(self.addButton)
        self.add_widget(self.mainContrastButton)
        self.add_widget(self.mainConditionButton)
        
        dropdownContrast = DropDown()
        for s in ['1 Contrast','2 Contrasts']:
            btn = Button(text = s, size_hint_y = None, height = self.mainContrastButton.height/2)
            btn.bind(on_release=lambda btn: dropdownContrast.select(btn.text))
            dropdownContrast.add_widget(btn)
        self.mainContrastButton.bind(on_release=dropdownContrast.open)
        dropdownContrast.bind(on_select=lambda _, x: setattr(self.mainContrastButton, 'text', x))
        
        dropdownCondition = DropDown()
        for s in ['6 Stimuli','12 Stimuli','24 Stimuli','48 Stimuli','64 Stimuli']:
            btn = Button(text = s, size_hint_y = None, height = self.mainConditionButton.height/2)
            btn.bind(on_release=lambda btn: dropdownCondition.select(btn.text))
            dropdownCondition.add_widget(btn)
        self.mainConditionButton.bind(on_release=dropdownCondition.open)
        dropdownCondition.bind(on_select=lambda _, x: setattr(self.mainConditionButton, 'text', x))
    
    def _adjustRect(self, instance, _):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class StimLabel(FloatLayout):
    
    def __init__(self, text, **kwargs):
        super(StimLabel, self).__init__(**kwargs)
        
        layout = self.layout = FloatLayout(size_hint = (0.99, 0.99), pos_hint = {'center_x': 0.5, 'center_y': 0.5})
        with layout.canvas.before:
            Color(.2, .2, .2, 1)
            self.rect = Rectangle(size = layout.size, pos = layout.pos)
        layout.bind(size = self._updateRect, pos = self._updateRect)
        
        label = Label(text = text, size_hint = (0.8, 1), pos_hint = {'center_x': 0.4, 'center_y': 0.5})
        self.buttonUp = Button(text = 'Up', size_hint = (0.1, 0.5), pos_hint = {'center_x': 0.85, 'center_y': 0.25})
        self.buttonDown = Button(text = 'Down', size_hint = (0.1, 0.5), pos_hint = {'center_x': 0.95, 'center_y': 0.25})
        self.buttonRemove = Button(text = 'Remove', size_hint = (0.2, 0.5), pos_hint = {'center_x': 0.9, 'center_y': 0.75})
        
        layout.add_widget(label)
        layout.add_widget(self.buttonUp)
        layout.add_widget(self.buttonDown)
        layout.add_widget(self.buttonRemove)
        self.add_widget(layout)
    
    def _updateRect(self, instance, _):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class MainScreen(Screen):
    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
        import Tkinter
        root = Tkinter.Tk()
        self.WIN_WIDTH, self.WIN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        self.MIL_WIDTH, self.MIL_HEIGHT = root.winfo_screenmmwidth(), root.winfo_screenmmheight()
        self.PPC = 10.*(float(self.WIN_WIDTH)/self.MIL_WIDTH + float(self.WIN_HEIGHT)/self.MIL_HEIGHT)/2.
        self.SCREEN_INFO = (self.WIN_WIDTH, self.WIN_HEIGHT, self.MIL_WIDTH, self.MIL_HEIGHT, self.PPC)
        
        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, self.WIN_WIDTH)
        self.capture.set(4, self.WIN_HEIGHT)
        
        self.eyeTracker = None
        try:
            self.eyeTracker = pylink.EyeLink('100.1.1.1')
        except:
            self.eyeTracker = None
            print "Could not connect to eye tracker"
        
        ''' Layout the layouts '''
        self.mainLayout = mainLayout = FloatLayout()
        with mainLayout.canvas.before:
            Color(.8, .8, .8, 1)
            self.background = Rectangle(size = self.size, pos = self.pos)
        mainLayout.bind(pos = self._updateBackground, size = self._updateBackground)
        
        hgap, vgap = 0.01, 0.01
        self.topLeftLayout      = topLeftLayout     = PartialLayout(size_hint = (.5-hgap/2, 0.4*(1-2*vgap)),
                                                                    pos_hint = {'center_x': 0.25-hgap/4, 'center_y': .804})
        
        self.middleLeftLayout   = middleLeftLayout  = PartialLayout(size_hint = (.5-hgap/2, 0.5*(1-2*vgap)),
                                                                    pos_hint = {'center_x': 0.25-hgap/4, 'center_y': .353})
        
        self.bottomLeftLayout   = bottomLeftLayout  = PartialLayout(size_hint = (.5-hgap/2, 0.1*(1-2*vgap)),
                                                                    pos_hint = {'center_x': 0.25-hgap/4, 'center_y': .049})
        
        self.rightLayout        = rightLayout       = PartialLayout(size_hint = (.5-hgap/2, 1),
                                                                    pos_hint = {'center_x': 0.75+hgap/4, 'center_y': .5})
        
        self.add_widget(mainLayout)
        mainLayout.add_widget(topLeftLayout)
        mainLayout.add_widget(middleLeftLayout)
        mainLayout.add_widget(bottomLeftLayout)
        mainLayout.add_widget(rightLayout)
        
        ''' Top left layout '''
        saveFolderLabel = Label(text = 'Save Folder', size_hint = (0.4, 0.25), pos_hint = {'center_x': 0.2, 'center_y': 0.875})
        folderButton = Button(source = 'Assets/folder.png',
                              size_hint = (None, None),
                              size = (0.05*self.WIN_HEIGHT, 0.05*self.WIN_HEIGHT),
                              pos_hint = {'center_x': 0.45, 'center_y': 0.875})
        self.folderText = TextInput(size_hint = (0.5, 0.125), pos_hint = {'center_x': 0.75, 'center_y': 0.875})
        subjectIDLabel = Label(text = 'Subject ID', size_hint = (0.5, 0.25), pos_hint = {'center_x': 0.25, 'center_y': 0.625})
        self.subjectIDText = TextInput(size_hint = (0.5, 0.125), pos_hint = {'center_x': 0.75, 'center_y': 0.625})
        calibButton = Button(text = 'Calibrate Eye Tracker', size_hint = (1, 0.25), pos_hint = {'center_x': 0.5, 'center_y': 0.375})
        checkCamButton = Button(text = 'Check Camera', size_hint = (1, 0.25), pos_hint = {'center_x': 0.5, 'center_y': 0.125})
        
        folderButton.background_normal = 'Assets/folder_normal.png'
        folderButton.background_down = 'Assets/folder_down.png'
        
        topLeftLayout.add_widget(saveFolderLabel)
        topLeftLayout.add_widget(folderButton)
        topLeftLayout.add_widget(self.folderText)
        topLeftLayout.add_widget(subjectIDLabel)
        topLeftLayout.add_widget(self.subjectIDText)
        topLeftLayout.add_widget(calibButton)
        topLeftLayout.add_widget(checkCamButton)
        
        ''' Middle Left Layout '''
        designerLabel = Label(text = 'Experiment Designer', size_hint = (1, 0.2), pos_hint = {'center_x': 0.5, 'center_y': 0.9})
        self.asd = asd = AntisaccadeDesigner(size_hint = (1, 0.39), pos_hint = {'center_x': 0.5, 'center_y': 0.6})
        self.vsd = vsd = VisualSearchDesigner(size_hint = (1, 0.39), pos_hint = {'center_x': 0.5, 'center_y': 0.2})
        
        middleLeftLayout.add_widget(designerLabel)
        middleLeftLayout.add_widget(asd)
        middleLeftLayout.add_widget(vsd)
        
        ''' Bottom Left Layout '''
        startButton = Button(text = 'Start', size_hint = (0.5, 0.99), pos_hint = {'center_x': 0.5, 'center_y': 0.5})
        bottomLeftLayout.add_widget(startButton)
        
        ''' Right Layout '''
        self.stimGrid = GridLayout(cols = 1, spacing = 10, size_hint_y = None)
        self.stimGrid.bind(minimum_height=self.stimGrid.setter('height'))
        with self.stimGrid.canvas.before:
            Color(0, 0, 0, 1)
            self.gridRect = Rectangle(size = self.stimGrid.size, pos = self.stimGrid.pos)
        self.stimGrid.bind(pos=self._updateGridRect, size=self._updateGridRect)
        
        flowLabel = Label(text = 'Experiment Flow', size_hint = (1, 0.1), pos_hint = {'center_x': 0.5, 'center_y': 0.95})
        scroller = ScrollView(size_hint = (1, 0.7), pos_hint = {'center_x': 0.5, 'center_y': 0.55})
        showButton = Button(text = 'Hide', size_hint = (0.5, 0.1), pos_hint = {'center_x': 0.25, 'center_y': 0.15})
        clearButton = Button(text = 'Clear', size_hint = (0.5, 0.1), pos_hint = {'center_x': 0.75, 'center_y': 0.15})
        randButton = Button(text = 'Randomize', size_hint = (0.5, 0.1), pos_hint = {'center_x': 0.25, 'center_y': 0.05})
        
        scroller.add_widget(self.stimGrid)
        rightLayout.add_widget(flowLabel)
        rightLayout.add_widget(scroller)
        rightLayout.add_widget(showButton)
        rightLayout.add_widget(clearButton)
        rightLayout.add_widget(randButton)
        
        ''' Other widgets '''
        self.isVisible = True
        
        self.coverWidget = FloatLayout(size_hint = (1, 0.7), pos_hint = {'center_x': 0.5, 'center_y': 0.55})
        with self.coverWidget.canvas.before:
            Color(0, 0, 0, 1)
            self.coverRect = Rectangle(size = self.coverWidget.size, pos = self.coverWidget.pos)
        self.coverWidget.bind(pos = self._updateCoverRect, size = self._updateCoverRect)
        self.coverWidget.add_widget(Label(text = 'Experiment flow is\ncurrently hidden.',
                                          size_hint = (1, 1),
                                          pos_hint = {'center_x': 0.5, 'center_y': 0.5}))
        
        self.calibrationWidget = FloatLayout(size_hint = (1, 1), pos_hint = {'center_x': 0.5, 'center_y': 0.5})
        with self.calibrationWidget.canvas.before:
            Color(0, 0, 0, 1)
            self.calibRect = Rectangle(size = self.calibrationWidget.size, pos = self.calibrationWidget.pos)
        self.calibrationWidget.bind(pos = self._updateCalibOverlay, size = self._updateCalibOverlay)
        self.coverWidget.add_widget(Label(text = CALIB_TEXT,
                                          size_hint = (1, 1),
                                          pos_hint = {'center_x': 0.5, 'center_y': 0.5}))
        
        ''' Object Bindings '''
        folderButton.bind(on_release = self.chooseRootFolder)
        checkCamButton.bind(on_release = self.toCheckCam)
        calibButton.bind(on_release = self.calibrateEyelink)
        self.asd.addButton.bind(on_release = self.addAntisaccade)
        self.vsd.addButton.bind(on_release = self.addVisualSearch)
        startButton.bind(on_release = self.startExperiment)
        
        showButton.bind(on_release = self.toggleGUI)
        clearButton.bind(on_release = self.clearExperiment)
        randButton.bind(on_release = self.randomizeOrder)
    
    def chooseRootFolder(self, _):
        pass
    
    def calibrateEyelink(self, _):
        if not self.eyeTracker is None:
            self.eyeTracker.doTrackerSetup()
    
    def toCheckCam(self, _):
        self.parent.transition.direction = 'left'
        self.parent.current = 'check_cam'
    
    def addAntisaccade(self, _):
        stimLabel = StimLabel(text = 'Antisaccade', size_hint_y = None, height = self.WIN_HEIGHT/10)
        self.stimGrid.add_widget(stimLabel)
        
        stimLabel.buttonUp.bind(on_release = self.moveTaskUp)
        stimLabel.buttonDown.bind(on_release = self.moveTaskDown)
        stimLabel.buttonRemove.bind(on_release = self.removeTask)
    
    def addVisualSearch(self, _):
        text = 'Visual Search\nContrast(s): {}, Stimuli: {}'.format(self.vsd.mainContrastButton.text.split(' ')[0],
                                                                    self.vsd.mainConditionButton.text.split(' ')[0])
        stimLabel = StimLabel(text = text, size_hint_y = None, height = self.WIN_HEIGHT/10)
        self.stimGrid.add_widget(stimLabel)
        
        stimLabel.buttonUp.bind(on_release = self.moveTaskUp)
        stimLabel.buttonDown.bind(on_release = self.moveTaskDown)
        stimLabel.buttonRemove.bind(on_release = self.removeTask)
    
    def moveTaskUp(self, obj):
        index = self.stimGrid.children.index(obj.parent.parent)
        if index == len(self.stimGrid.children)-1:
            return
        child = self.stimGrid.children[index]
        self.stimGrid.remove_widget(child)
        self.stimGrid.add_widget(child, index+1)
    
    def moveTaskDown(self, obj):
        index = self.stimGrid.children.index(obj.parent.parent)
        if index == 0:
            return
        child = self.stimGrid.children[index]
        self.stimGrid.remove_widget(child)
        self.stimGrid.add_widget(child, index-1)
    
    def removeTask(self, obj):
        self.stimGrid.remove_widget(obj.parent.parent)
    
    def startExperiment(self, _):
        if len(self.stimGrid.children) == 0:
            return
    
    def toggleGUI(self, _):
        if self.isVisible:
            self.rightLayout.add_widget(self.coverWidget)
        else:
            self.rightLayout.remove_widget(self.coverWidget)
        self.isVisible = not self.isVisible
    
    def clearExperiment(self, _):
        self.stimGrid.clear_widgets()
    
    def randomizeOrder(self, _):
        random.shuffle(self.stimGrid.children)
    
    def _updateBackground(self, instance, _):
        self.background.pos = instance.pos
        self.background.size = instance.size
    
    def _updateGridRect(self, instance, _):
        self.gridRect.pos = instance.pos
        self.gridRect.size = instance.size
    
    def _updateCoverRect(self, instance, _):
        self.coverRect.pos = instance.pos
        self.coverRect.size = instance.size
    
    def _updateCalibOverlay(self, instance, _):
        self.calibrationWidget.pos = instance.pos
        self.calibrationWidget.size = instance.size