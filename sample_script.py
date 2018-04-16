"""
Created on 2018-03-26
@author Alexandre Drouin-Picaro
"""

import csv
import cv2
import numpy as np
import random
import threading
import time
import Tkinter

try:
    import pylink
except:
    print "No pylink library could be found"

from os.path import join, isdir, isfile
from os import makedirs

''' Index of the camera to use. If there is only one camera, index is 0 '''
WEBCAM_INDEX = 1
SAVE_DIR = 'C:\\python_experiment'

''' Color constants for drawing in openCV. Images are in BGR format'''
BLACK   = (0,0,0)
RED     = (0,0,255)

class Experiment:
    
    def __init__(self):
        self.eyeTracker = None
        
        """ Get screen resolution and physical dimensions """
        root = Tkinter.Tk()
        self.WIN_WIDTH, self.WIN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()
        self.MIL_WIDTH, self.MIL_HEIGHT = root.winfo_screenmmwidth(), root.winfo_screenmmheight()
        self.SCREEN_INFO = (self.WIN_WIDTH, self.WIN_HEIGHT, self.MIL_WIDTH, self.MIL_HEIGHT)
        
        ''' Initiate webcam image capture and set image resolution to screen resolution. This can be changed. '''
        self.capture = cv2.VideoCapture(WEBCAM_INDEX)
        self.capture.set(3, self.WIN_WIDTH)
        self.capture.set(4, self.WIN_HEIGHT)       
        
        ''' Boolean trigger to stop the camera capture thread '''
        self.captureFlag = False
        
        ''' Check that the save folder exists. If not, create it. '''
        if not isdir(SAVE_DIR):
            makedirs(SAVE_DIR)
        
        ''' Variables to record metadata on the experiment '''
        self.experiment = 'N/A'
        self.metaDataRow = ['N/A', 'N/A', 'N/A', self.WIN_WIDTH, self.WIN_HEIGHT, self.MIL_WIDTH, self.MIL_HEIGHT]
        
        '''
        Check if the metadata file exists and, if it doesn't, create it and write the
        column headers. This file will be used for synchronization between the captured
        camera frames and the recorded eye tracker data.
        '''
        if not isfile(join(SAVE_DIR, 'metadata.csv')):
            with open(join(SAVE_DIR, 'metadata.csv'), 'wb') as f:
                writer = csv.writer(f, delimiter = ',')
                writer.writerow(['Experiment',
                                 'Timestamp',
                                 'Image name',
                                 'Screen Resolution X (pixels)',
                                 'Screen Resolution Y (pixels)',
                                 'Screen Width (mm)',
                                 'Screen Height (mm)',
                                 'Stim Info (Multicolumn)'])
    
    def runExperiment(self):
        ''' Connect to the eye tracker and do calibration'''
        try:
            self.eyeTracker = pylink.EyeLink('100.1.1.1')
            self.eyeTracker.doTrackerSetup()
        except:
            print "Could not connect to eye tracker"
        
        ''' Start recording thread '''
        self.captureFlag = True
        recordingThread = threading.Thread(target = self.recordingThread)
        recordingThread.start()
        
        ''' Run experiments '''
        self.runAntisaccades()
        
        ''' Cleanup '''
        self.captureFlag = False
        if not self.eyeTracker is None:
            self.eyeTracker.close()
            self.eyeTracker = None
    
    def recordingThread(self):
        '''
        Iterating as fast as possible:
        - Capture a frame from the webcam
        - If the frame was captured:
            - Update the metadata with the timestamp and image name
            - Save metadata to disk
            - Save image to disk
        '''
        imageIndex = 0
        if not self.capture.isOpened():
            self.capture.open(WEBCAM_INDEX)
        
        while self.captureFlag:
            timestamp = time.time()
            ret, image = self.capture.read()
            if ret:
                imageName = '%05d.jpg' % imageIndex
                self.metaDataRow[1] = timestamp
                self.metaDataRow[2] = imageName
                with open(join(SAVE_DIR, 'metadata.csv'), 'ab') as f:
                    writer = csv.writer(f, delimiter = ',')
                    writer.writerow(self.metaDataRow)
                
                cv2.imwrite(join(SAVE_DIR, imageName), image)
                imageIndex += 1
    
    def runAntisaccades(self):
        '''
        Antisaccade task.
        In this paradigm, the subject is shown a white screen containing a black dot at the center
        of the screen, and red dots to the left and right of the black dot. The red dots are centered
        vertically, and are positioned horizontally at 20% of the screen width from the edge of the
        screen edge towards the center.
        
        At a two-second interval, one of the red dots, chosen at random, will disappear for 0.5 second.
        When this happens, the subject is to look in the direction of the dot that just disappeared.
        '''
        
        if not self.eyeTracker is None:
            self.eyeTracker.openDataFile('ANTISACCADES.EDF')
            self.eyeTracker.startRecording(1,1,1,1)
            
        self.metaDataRow[0] = 'Antisaccades'
        self.metaDataRow.append(['N/A'])
        
        '''
        Initialize drawing variables:
            - x-axis centers of the left, middle and right dots
            - radius of the dots
        '''
        xl, xc, xr = int(0.2*self.WIN_WIDTH), int(0.5*self.WIN_WIDTH), int(0.8*self.WIN_WIDTH)
        r = int(min(0.02*self.WIN_HEIGHT, 0.02*self.WIN_WIDTH))
        
        '''
        Generate the list of stimuli. It consists of 12 antisaccades to the left, 12
        antisaccades to the right and 6 neutral stimuli where both left and right dots are shown,
        and no antisaccade should be performed. These stimuli are shown in a random order.
        
        A new "stimulus" is shown every 2 seconds. That is, the screen returns to neutral and,
        after 1.5 seconds, the direction of the antisaccade is shown for 0.5 second.
        '''
        stims = ['None']*6 + ['Left']*12 + ['Right']*12
        random.shuffle(stims)
        
        ''' Open a fullscreen borderless window in which the stimuli will be drawn '''
        cv2.namedWindow('Antisaccades', cv2.WND_PROP_FULLSCREEN)          
        cv2.setWindowProperty('Antisaccades', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        '''
        Start iterating through the stimuli.
        When the screen returns to normal and when a stimulus is shown,
        the event is recorded is the eye tracker data file and in the metadata
        synchronization file.
        '''
        for stim in stims:
            if not self.eyeTracker is None:
                self.eyeTracker.sendMessage('TO_NEUTRAL')
            self.metaDataRow[-1] = 'Neutral'
            cv2.imshow('Antisaccades', self.makeAntisaccadeSlides('None', xl, xc, xr, r))
            cv2.waitKey(1500)
            
            if not self.eyeTracker is None:
                self.eyeTracker.sendMessage('STIMULUS_{}').format(stim)
            self.metaDataRow[-1] = stim
            cv2.imshow('Antisaccades', self.makeAntisaccadeSlides(stim, xl, xc, xr, r))
            cv2.waitKey(500)
        
        if not self.eyeTracker is None:
            self.eyeTracker.sendMessage('TO_NEUTRAL')
        self.metaDataRow[-1] = 'Neutral'
        cv2.imshow('Antisaccades', self.makeAntisaccadeSlides('None', xl, xc, xr, r))
        cv2.waitKey(1500)
        
        ''' Cleanup '''
        cv2.destroyAllWindows()
        self.metaDataRow = self.metaDataRow[:-1]
        self.metaDataRow[:3] = ['N/A', 'N/A', 'N/A']
        
        if not self.eyeTracker is None:
            self.eyeTracker.stopRecording()
            self.eyeTracker.closeDataFile()
            self.eyeTracker.receiveDataFile('ANTISACCADES.EDF', join(SAVE_DIR, 'ANTISACCADES.EDF'))
    
    def makeAntisaccadeSlides(self, stimSide, xl, xc, xr, r):
        slide = np.ones((self.WIN_HEIGHT, self.WIN_WIDTH, 3), np.uint8)*(255)
        cv2.circle(slide, (xc, self.WIN_HEIGHT/2), r, BLACK, -1)
        if stimSide == 'Right':
            cv2.circle(slide, (xr, self.WIN_HEIGHT/2), r, RED, -1)
        elif stimSide == 'Left':
            cv2.circle(slide, (xl, self.WIN_HEIGHT/2), r, RED, -1)
        else:
            cv2.circle(slide, (xr, self.WIN_HEIGHT/2), r, RED, -1)
            cv2.circle(slide, (xl, self.WIN_HEIGHT/2), r, RED, -1)
        
        return slide

if __name__ == '__main__':
    experiment = Experiment()
    experiment.runExperiment()
    #experiment.runAntisaccades()