import ttk 
from Tkinter import * 
import math
import FramePlot
import glyxsuite

        
class HistogramView(FramePlot.FramePlot,glyxsuite.lib.Histogram):
    
    def __init__(self,master,model,height=300,width=800):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width,xTitle= "Glyco Score",yTitle="Counts")
        glyxsuite.lib.Histogram.__init__(self,0.2)
        
        self.master = master
        self.logScore = 0.0
        self.NrXScales = 5.0

        self.coord = StringVar()
        l = Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky=N+S)
        
        self.keepZoom = IntVar()
        c = Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky=N+S)
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        #self.model.funcScoringMSSpectrum = self.initSpectrum

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        height = {}
        for label in self.bins.keys():
            for b in self.bins[label]:
                va = b*self.binwidth
                if self.aMax == -1 or va > self.aMax:
                    self.aMax = va
                vb = self.bins[label][b]
                if not b in height:
                    height[b] = 0
                height[b] += vb
        for b in height:
            if self.bMax == -1 or height[b] > self.bMax:
                self.bMax = height[b]

    def paintObject(self):
        bottomStart = {}
        for label in self.bins.keys():
            bottom = []
            height = []
            left = []
            if not label in self.bins:
                continue
            for b in self.bins[label]:
                if not b in bottomStart:
                    bottomStart[b] = 0
                item = self.canvas.create_rectangle(
                        self.convAtoX(b*self.binwidth),
                        self.convBtoY(bottomStart[b]),
                        self.convAtoX(b*self.binwidth+self.binwidth),
                        self.convBtoY(bottomStart[b]+self.bins[label][b]),
                        fill=self.colors[label])
                bottomStart[b] += self.bins[label][b]

        # plot logScore line
        intZero = self.convBtoY(0)
        intMax = self.convBtoY(self.viewYMax)
        if self.logScore != 0:
            item = self.canvas.create_line(
                self.convAtoX(self.logScore),
                intZero,
                self.convAtoX(self.logScore),
                intMax,
                fill='red', width=4)
                    

        self.allowZoom = True
            
    def initHistogram(self,logScore):
        self.logScore = logScore
        self.initCanvas(keepZoom = True)
        
    def identifier(self):
        return "HistogramView"
        
