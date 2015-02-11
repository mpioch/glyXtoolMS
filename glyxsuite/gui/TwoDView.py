import ttk 
from Tkinter import * 
import math
import FramePlot
import DataModel

        
class TwoDView(FramePlot.FramePlot):
    
    def __init__(self,master,model,height=300,width=300):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width,xTitle= "rt [s]",yTitle="mz [Th]")
        
        self.master = master

        self.coord = StringVar()
        l = Label(self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky=N+S)
        
        self.keepZoom = IntVar()
        c = Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky=N+S)
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcFeatureTwoDView = self.init
        
        # Events
        #self.canvas.bind("<Left>", self.setButtonValue)
        #self.canvas.bind("<Right>", self.setButtonValue)
        #self.canvas.bind("<Button-1>", self.setSpectrumPointer)
        
        optionsFrame = ttk.Labelframe(self,text="Plot Options")
        optionsFrame.grid(row=0, column=1, sticky=N+S)
        
        self.ov1 = IntVar()
        oc1 = Checkbutton(optionsFrame,
                            text="In Feature and\nRight Charge",
                            variable=self.ov1,
                            command=lambda:self.setButtonValue(1))
        oc1.grid(row=3,column=0,sticky="WS")
        
        self.ov2 = IntVar() # Switch all Features and Wrong Charge
        oc2 = Checkbutton(optionsFrame,
                            text="In Feature and\nWrong Charge",
                            variable = self.ov2,
                            command=lambda:self.setButtonValue(2))
        oc2.grid(row=4,column=0,sticky="WS")
        
        self.ov3 = IntVar() # Switch all Outside Features
        oc3 = Checkbutton(optionsFrame,text="Outside Feature",
                            variable = self.ov3,
                            command=lambda:self.setButtonValue(3))
        oc3.grid(row=6,column=0,sticky="WS")
        
        self.ov4 = IntVar() # Switch all Glycopeptide
        ol4 = Label(optionsFrame,text="Glycopeptide")
        ol4.grid(row=0,column=2,sticky="S")
        oc4 = Checkbutton(optionsFrame,
                            variable = self.ov4,
                            command=lambda:self.setButtonValue(4))
        oc4.grid(row=1,column=2,sticky="S") 
        
        self.ov5 = IntVar() # Switch all No Glycopeptide
        ol5 = Label(optionsFrame,text="No Glycopeptide")
        ol5.grid(row=0,column=4,sticky="S")
        oc5 = Checkbutton(optionsFrame,
                            variable = self.ov5,
                            command=lambda:self.setButtonValue(5)) 
        oc5.grid(row=1,column=4,sticky="S")
        
        self.ov6 = IntVar() # In Feature / Glyco / Right Charge
        oc6 = Checkbutton(optionsFrame,
                            variable = self.ov6,
                            command=lambda:self.setButtonValue(6))
        oc6.grid(row=3,column=2,sticky="NS")
        
        self.ov7 = IntVar() # In Feature / Glyco / Wrong Charge
        oc7 = Checkbutton(optionsFrame,
                            variable = self.ov7,
                            command=lambda:self.setButtonValue(7))
        oc7.grid(row=4,column=2,sticky="NS")
        
        self.ov8 = IntVar() # In Feature / No Glyco / Right Charge
        oc8 = Checkbutton(optionsFrame,
                            variable = self.ov8,
                            command=lambda:self.setButtonValue(8))
        oc8.grid(row=3,column=4,sticky="NS")
        
        self.ov9 = IntVar() # In Feature / No Glyco / Wrong Charge
        oc9 = Checkbutton(optionsFrame,
                            variable = self.ov9,
                            command=lambda:self.setButtonValue(9))
        oc9.grid(row=4,column=4,sticky="NS")
        
        self.ov10 = IntVar() # Glyco / Outside feature
        oc10 = Checkbutton(optionsFrame,
                            variable = self.ov10,
                            command=lambda:self.setButtonValue(10))
        oc10.grid(row=6,column=2,sticky="NS")
        
        self.ov11 = IntVar() # No Glyco / Outside feature
        oc11 = Checkbutton(optionsFrame,
                            variable = self.ov11,
                            command=lambda:self.setButtonValue(11))
        oc11.grid(row=6,column=4,sticky="NS")
        
        s1 = ttk.Separator(optionsFrame)
        s1.grid(row=2,column=0,columnspan=5,sticky="NSEW")
        s2 = ttk.Separator(optionsFrame)
        s2.grid(row=5,column=0,columnspan=5,sticky="NSEW")
        
        s3 = ttk.Separator(optionsFrame,orient="vertical")
        s3.grid(row=0,column=1,rowspan=7,sticky="NSEW")
        s4 = ttk.Separator(optionsFrame,orient="vertical")
        s4.grid(row=0,column=3,rowspan=7,sticky="NSEW")
        
        # set default states
        self.ov1.set(0)
        self.ov2.set(0)
        self.ov3.set(0)
        self.ov4.set(0)
        self.ov5.set(0)
        self.ov6.set(1)
        self.ov7.set(1)
        self.ov8.set(1)
        self.ov9.set(1)
        self.ov10.set(1)
        self.ov11.set(0)
        

    def setButtonValue(self,i):
        state = getattr(self,"ov"+str(i)).get()
        if i == 1:
            self.ov6.set(state)
            self.ov8.set(state)
        elif i == 2:
            self.ov7.set(state)
            self.ov9.set(state)
        elif i == 3:
            self.ov10.set(state)
            self.ov11.set(state)
        elif i == 4:
            self.ov6.set(state)
            self.ov7.set(state)
            self.ov10.set(state)
        elif i == 5:
            self.ov8.set(state)
            self.ov9.set(state)
            self.ov11.set(state)
        # plot feature
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        self.init(keepZoom=True)
        
    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        for feature in self.model.currentAnalysis.analysis.features:
            rt = feature.getRT()
            mz = feature.getMZ()
            if self.aMax < rt:
                self.aMax = rt
            if self.bMax < mz:
                self.bMax = mz

    def paintFeatures(self):
        for feature in self.model.currentAnalysis.analysis.features:
            rt1,rt2,mz1,mz2 = feature.getBoundingBox()
            rt1 = self.convAtoX(rt1)
            rt2 = self.convAtoX(rt2)
            mz1 = self.convBtoY(mz1)
            mz2 = self.convBtoY(mz2)

            linewidth = 2
            #if chrom.selected == True:
            #    linewidth = 2
            xy = []
            xy += [rt1,mz1]
            xy += [rt2,mz1]
            xy += [rt2,mz2]
            xy += [rt1,mz2]
            xy += [rt1,mz1]
            if self.model.currentAnalysis.currentFeature == feature:
                color = "red"
                colorSpec = "green"
            else:
                color = "black"
                colorSpec = "white"
            item = self.canvas.create_line(xy,fill=color, width = linewidth)
    
    def paintSpectra(self):
        # calculate circle diameter
        #diam = int(min(self.slopeA,self.slopeB)*2)
        diam = int(min(self.slopeA,self.slopeB)*2)+1.5
        # plot msms spectra
        for specId in self.model.currentAnalysis.spectraInFeatures:
            
            features = self.model.currentAnalysis.spectraInFeatures[specId]
            spectrum = self.model.currentAnalysis.spectraIds[specId]

            # get charge state
            hasCharge = False
            for featureId in features:
                feature = self.model.currentAnalysis.featureIds[featureId] 
                if feature.charge == spectrum.precursorCharge:
                    hasCharge = True
                    break

            nr = 1
            if spectrum.isGlycopeptide:
                nr *= 1
            else:
                nr *= 2
            
            if len(features) == 0:
                nr *= 3
            elif hasCharge == True:
                nr *= 5
            else:
                nr *= 7
            
            if nr == 5:
                if self.ov6.get() == 0:
                    continue
                color = "green"
            elif nr == 7:
                if self.ov7.get() == 0:
                    continue
                color = "green"
            elif nr == 3:
                if self.ov10.get() == 0:
                    continue
                color = "green"
            elif nr == 10:
                if self.ov8.get() == 0:
                    continue
                color = "red"
            elif nr == 14:
                if self.ov9.get() == 0:
                    continue
                color = "red"
            else:
                if self.ov11.get() == 0:
                    continue
                color = "red"
                
            x = self.convAtoX(spectrum.rt)
            y = self.convBtoY(spectrum.precursorMass)
            item = self.canvas.create_oval(x-diam, y-diam, x+diam, y+diam, fill=color)        

    def paintObject(self):
        self.allowZoom = False
        
        self.paintFeatures()
        self.paintSpectra()
        
        
        self.allowZoom = True
    
    def init(self,keepZoom = False):
        self.initCanvas(keepZoom = keepZoom)

    def identifier(self):
        return "2DView"

        
    