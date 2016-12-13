import ttk
import Tkinter
import math
import os
import tkFileDialog

class Observe(Tkinter.Button):
    
    def __init__(self,master, text):
        Tkinter.Button.__init__(self, master=master, text=text)
        
    def pack(self, *arg):
        print "pack called"
        Tkinter.Button.pack(self, arg)

class ToggleButton(Tkinter.Button):
    
    def __init__(self, master, toolbar, image, groupname, name, cursor = ""):
        Tkinter.Button.__init__(self, master,image=image, command=self.toggle)
        self.toolbar = toolbar
        self.master = master
        self.name = name
        self.groupname = groupname
        self.cursor = cursor
        self.config(relief="raised")
        self.active = Tkinter.BooleanVar()
        self.active.set(False)
        
        if groupname not in self.toolbar.groups:
            self.toolbar.groups[groupname] = []
        self.toolbar.groups.get(groupname).append(self)

    def setOn(self):
        self.config(relief="sunken")
        self.active.set(True)
        
    def setOff(self):
        self.config(relief="raised")
        self.active.set(False)
        
    def toggle(self):
        if self.config('relief')[-1] == 'sunken':
            self.setOff()
        else:
            # disable all other
            for button in self.toolbar.groups.get(self.groupname):
                if button == self:
                    continue
                else:
                    button.setOff()
            self.setOn()
        self.toolbar.collectActiveButtons()

class Toolbar(Tkinter.Frame):
    def __init__(self, master, model, canvas, sidepanel):
        Tkinter.Frame.__init__(self, master=master)
        self.model = model
        self.canvas = canvas
        self.sidepanel = sidepanel
        self.groups = {}
        self.panels = {}
        self.active = {}
        
    def addPanel(self, panelname, panel=None, side="left"):
        assert panelname not in self.panels
        if panel == None:
            panel = Tkinter.Frame(self)
        panel.pack(side=side)        
        self.panels[panelname] = panel
        return panel

    def addButton(self, imagepath, groupname, panelname, cursor="", side="left"):
        # get panel
        button = ToggleButton(self.panels[panelname], self,
                              self.model.resources[imagepath], 
                              groupname, imagepath, cursor=cursor)
        button.pack(side=side)
        return button
        

    def collectActiveButtons(self):
        self.active = {}
        for groupname in self.groups:
            for button in self.groups[groupname]:
                if button.active.get() == True:
                    self.active[groupname] = button.name
                    self.canvas.config(cursor=button.cursor)
        self.sidepanel.activatePanels(self.active.values())
        self.master.toolboxButtonPressed()
                    
    def deactivateGroup(self, groupname):
        for button in self.groups[groupname]:
            button.setOff()

            
class SidePanel(Tkinter.Frame, object):
    def __init__(self, master):
        Tkinter.Frame.__init__(self, master=master)
        self.master = master
        self.panels = {}

        # add spacer frame to force pack updates
        nullframe = Tkinter.Frame(self, bd=0)
        nullframe.pack()
        
    def addContextPanel(self, buttonname, panel):
        self.panels[buttonname] = panel

    def activatePanels(self,buttonnames):
        for name in self.panels:
            if name in buttonnames:
                if not self.panels[name].winfo_ismapped():
                    # activate panel
                    self.panels[name].pack(side="bottom", anchor="n")
                    self.panels[name].update()
            elif self.panels[name].winfo_ismapped():
                # deactivate panel
                self.panels[name].pack_forget()

class FramePlot(Tkinter.Frame, object):

    def __init__(self, master, model, xTitle="", yTitle=""):
        Tkinter.Frame.__init__(self, master=master)
        self.model = model
        self.master = master
        self.action = None
        self.zoomHistory = []
        self.allowZoom = False

        self.xTitle = xTitle
        self.yTitle = yTitle

        self.NrXScales = 5.0
        self.NrYScales = 5.0
        
        self.xTypeTime = False

        # add canvas
        self.aMax = -1
        self.bMax = -1
        self.aMin = 0
        self.bMin = 0

        self.viewXMin = 0
        self.viewXMax = 1
        self.viewYMin = 0
        self.viewYMax = 1

        self.slopeA = 1
        self.slopeB = 1
        
        # currentMousePositions in plot coordinates
        self.currentX = 0
        self.currentY = 0

        self.height = 0
        self.width = 0

        self.borderLeft = 100
        self.borderRight = 50
        self.borderTop = 50
        self.borderBottom = 50

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=0)
        self.columnconfigure(2,weight=0)
        self.rowconfigure(0,weight=0, minsize=38)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=0)
        

        #self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height) # check screen resolution
        self.canvas = Tkinter.Canvas(self) # check screen resolution
        self.canvas.config(bg="white")
        self.canvas.config(highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="NSEW")
        
        self.hbar = Tkinter.Scrollbar(self,orient="horizontal",command=self.scrollX)
        self.hbar.grid(row=2, column=0, sticky="NSEW")
        
        self.vbar=Tkinter.Scrollbar(self,orient="vertical",command=self.scrollY)
        self.vbar.grid(row=1, column=1, sticky="NSEW")
        
        self.sidepanel = SidePanel(self)
        self.sidepanel.grid(row=1, column=2, sticky="NEW")
        
        

        self.keepZoom = Tkinter.IntVar()
        #c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        #c.grid(row=5, column=0, sticky="NS")

        self.canvas.bind("<Button-1>", self.eventButton1, "+")
        self.canvas.bind("<Motion>", self.eventMouseMotion, "+")
        self.canvas.bind("<B1-Motion>", self.eventMouseMotionB1, "+")
        #self.canvas.bind("<Control-Button-1>", self.eventStartZoom, "+")
        self.canvas.bind("<ButtonRelease-1>", self.eventButtonRelease, "+")
        self.canvas.bind("<BackSpace>", self.zoomBack, "+")
        self.canvas.bind("<Control-Left>", self.keyLeft, "+")
        self.canvas.bind("<Control-Right>", self.keyRight, "+")
        self.canvas.bind("<Control-BackSpace>", self.resetZoom, "+")
        self.canvas.bind("<Configure>", self.on_resize, "+")
        self.canvas.bind("<Control-s>", self.savePlot, "+")
        self.canvas.bind("<4>", self.eventMousewheel, "+")
        self.canvas.bind("<5>", self.eventMousewheel, "+")
        # setup toolbar
        self.toolbar = Toolbar(self, model, self.canvas, self.sidepanel)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="NSEW")

        
        # add toolbar buttons for zoom
        panelZoom = self.toolbar.addPanel("default", side="left")
        self.toolbar.addButton("drag","toggle", "default", cursor="hand2")
        self.toolbar.addButton("zoom_in","toggle", "default", cursor="")
        self.toolbar.addButton("zoom_out","single", "default", cursor="")
        self.toolbar.addButton("zoom_auto","single", "default", cursor="")
        
        # Add coords and Canvasname to panel
        panelCoords = self.toolbar.addPanel("coords", side="right")
        #panelCoords.config(bg=self.toolbar.cget("bg"))
        labelName = Tkinter.Label(panelCoords, text=self.identifier())
        #labelName.config(bg=panelCoords.cget("bg"))
        labelName.grid(row=0, column=0, sticky="NE")
        
        self.coord = Tkinter.StringVar()
        l = Tkinter.Label(panelCoords, textvariable=self.coord)
        l.grid(row=1, column=0, sticky="NE")
        
        #saveButton = ttk.Button(self, text="Save Plot", command=self.savePlot)
        #saveButton.grid(row=5, column=1, sticky="NS")

        self.calcScales()
        self._paintAxis()

        
    def toggle(self):
        print "foo"
        
    def scrollX(self, *args):
        if args[0] == '-1':
            self.keyLeft(None)
        elif args[0] == '1':
            self.keyRight(None)
        elif args[0] == 'scroll':
            if args[1] == '-1':
                self.keyLeft(None)
            if args[1] == '1':
                self.keyRight(None)
        elif args[0] == 'moveto':
            moveto = float(args[1])
            barsize = self.hbar.get()[1]-self.hbar.get()[0]
            if moveto < 0:
                moveto = 0
            elif (moveto + barsize) > 1:
                moveto = 1 - barsize
            self.viewXMin = moveto * float(self.aMax-self.aMin)
            self.viewXMax = (moveto + barsize) * float(self.aMax-self.aMin)
            self._paintCanvas(addToHistory=False)
    
    def scrollY(self, *args):
        if args[0] == '-1':
            self.keyUp(None)
        elif args[0] == '1':
            self.keyDown(None)
        elif args[0] == 'scroll':
            if args[1] == '-1':
                self.keyUp(None)
            if args[1] == '1':
                self.keyDown(None)
        elif args[0] == 'moveto':
            moveto = float(args[1])
            barsize = self.vbar.get()[1]-self.vbar.get()[0]
            if moveto < 0:
                moveto = 0
            elif (moveto + barsize) > 1:
                moveto = 1 - barsize
            self.viewYMax = self.bMax-moveto * float(self.bMax-self.bMin)
            self.viewYMin = self.bMax-(moveto + barsize) * float(self.bMax-self.bMin)
            self._paintCanvas(addToHistory=False)

    def savePlot(self, event):
        if self.model.currentAnalysis == None:
            return
        options = {}
        options['filetypes'] = [('post script', '.eps'), ]
        workingdir = os.path.dirname(self.model.currentAnalysis.path)
        options['initialdir'] = workingdir
        options['parent'] = self
        filename = tkFileDialog.asksaveasfilename(**options)
        if filename == "":
            return
        self.canvas.postscript(file=filename, height=self.height, width=self.width)
        
    def on_resize(self,event):
        self.width = event.width
        self.height = event.height
        self._paintCanvas(False)

    def keyUp(self,event):
        if self.allowZoom == False:
            return
        windowsize = self.viewYMax-self.viewYMin
        add = abs(windowsize)*0.1
        if self.viewYMax+add >= self.bMax:
            self.viewYMin = self.bMax - windowsize
            self.viewYMax = self.bMax
        else:
            self.viewYMin = self.viewYMin+add
            self.viewYMax = self.viewYMax+add
        self._paintCanvas(addToHistory=False)
        
    def keyDown(self,event):
        if self.allowZoom == False:
            return
        windowsize = self.viewYMax-self.viewYMin
        add = abs(windowsize)*0.1
        if self.viewYMin-add <= self.bMin:
            self.viewYMin = self.bMin 
            self.viewYMax = self.bMin + windowsize
        else:
            self.viewYMin = self.viewYMin-add
            self.viewYMax = self.viewYMax-add
        self._paintCanvas(addToHistory=False)

    def keyLeft(self, event):
        if self.allowZoom == False:
            return
        windowsize = self.viewXMax-self.viewXMin
        add = abs(windowsize)*0.1
        if self.viewXMin-add <= self.aMin:
            self.viewXMin = self.aMin
            self.viewXMax = self.aMin + windowsize
        else:
            self.viewXMin = self.viewXMin-add
            self.viewXMax = self.viewXMax-add
        self._paintCanvas(addToHistory=False)

    def keyRight(self, event):
        if self.allowZoom == False:
            return
        windowsize = self.viewXMax-self.viewXMin
        add = abs(windowsize)*0.1
        if self.viewXMax+add >= self.aMax:
            self.viewXMin = self.aMax - windowsize
            self.viewXMax = self.aMax
        else:
            self.viewXMin = self.viewXMin+add
            self.viewXMax = self.viewXMax+add
        self._paintCanvas(addToHistory=False)
        
    def eventMousewheel(self, event):
        
        def calcScroll(self, value, sign, viewMin, viewMax):         
            add = abs(viewMax-viewMin)*0.1*sign
            a1 = value - viewMin
            b1 = viewMax - value
            if a1 > b1:
                a2 = a1 - add
                b2 = a2 * b1 / float(a1)
            else:
                b2 = b1 - add
                a2 = a1 *b2 / float(b1)
            return value - a2, value + b2
        
        x = self.convXtoA(event.x)
        y = self.convYtoB(event.y)
        if event.num == 4:
            sign = 1
        elif event.num == 5:
            sign = -1
        else:
            return
        if x > 0 and y > 0:
            self.viewXMin,self.viewXMax = calcScroll(self,x, sign,self.viewXMin,self.viewXMax)
            self.viewYMin,self.viewYMax = calcScroll(self,y, sign,self.viewYMin,self.viewYMax)
        elif x > 0:
            self.viewXMin,self.viewXMax = calcScroll(self,x, sign,self.viewXMin,self.viewXMax)
        elif y > 0:
            self.viewYMin,self.viewYMax = calcScroll(self,y, sign,self.viewYMin,self.viewYMax)
        else:
            return

        self._paintCanvas(addToHistory=False)

    def identifier(self):
        return "Frameplot"

    def setMaxValues(self):
        raise Exception("Replace function!")

    def paintObject(self):
        raise Exception("Replace function!")
        
    def toolboxButtonPressed(self):
        if self.toolbar.active.get("single", "") == "zoom_auto":
            self.toolbar.deactivateGroup("single")
            self.viewXMin = self.aMin
            self.viewXMax = self.aMax
            self.viewYMin = self.bMin
            self.viewYMax = self.bMax
            self._paintCanvas(addToHistory=False)
        elif self.toolbar.active.get("single", "") == "zoom_out":
            addX = abs(self.viewXMax-self.viewXMin)*0.1
            self.viewXMin -= addX
            self.viewXMax += addX
            if self.viewXMin < self.aMin:
                self.viewXMin = self.aMin
            if self.viewXMax > self.aMin:
                self.viewXMax = self.aMax
                
            addY = abs(self.viewYMax-self.viewYMin)*0.1
            self.viewYMin -= addY
            self.viewYMax += addY
            if self.viewYMin < self.bMin:
                self.viewYMin = self.bMin
            if self.viewYMax > self.bMin:
                self.viewYMax = self.bMax
            self.toolbar.deactivateGroup("single")
            self._paintCanvas(addToHistory=False)
                
    def eventButton1(self, event):
        self.canvas.focus_set()
        # get current toolbar
        if self.toolbar.active.get("toggle", "") == "zoom_in":
            x = event.x
            y = event.y
            self.action = {"name":"zoomin", "x":x, "y":y}
            rectangle = self.canvas.create_rectangle(x, y, x, y)
            self.action["rectangle"] = rectangle
        elif self.toolbar.active.get("toggle", "") == "drag":
            self.action = {"name":"drag", "startx":self.convXtoA(event.x), "starty":self.convYtoB(event.y)}


    def eventMouseMotion(self, event):
        x = self.convXtoA(event.x)
        if self.xTypeTime == True and self.model.timescale == "minutes":
            x = x/60.0
        y = self.convYtoB(event.y)
        self.currentX = x
        self.currentY = y
        xstring = str(round(x, 4))
        xstring += "0"*(4-len(xstring.split(".")[1])) # pad number
        ystring = str(round(y, 4))
        ystring += "0"*(4-len(ystring.split(".")[1])) # pad number
        
        self.coord.set(xstring+"/"+ystring)

    def eventMouseMotionB1(self, event):
        if self.action == None:
            return

        if self.action.get("name","") == "drag":
            x = self.convXtoA(event.x)
            y = self.convYtoB(event.y)

            startx = self.action.get("startx")
            starty = self.action.get("starty")
            dragx = startx - x
            dragy = starty - y

            if dragx < 0 and self.viewXMin == self.aMin:
                dragx = 0
            elif dragx > 0 and self.viewXMax == self.aMax:
                dragx = 0
                
            if dragy < 0 and self.viewYMin == self.bMin:
                dragy = 0
            elif dragy > 0 and self.viewYMax == self.bMax:
                dragy = 0

            self.viewXMin += dragx
            self.viewXMax += dragx
            self.viewYMin += dragy
            self.viewYMax += dragy
            self._paintCanvas(addToHistory=False)
            return
        elif self.action.get("name","") == "zoomin":
            self.canvas.coords(self.action["rectangle"], 
                               (self.action["x"], self.action["y"], 
                               event.x, event.y))

    def eventButtonRelease(self, event):
        if self.action == None:
            return
        if self.action.get("name","") == "zoomin":
            x1, y1, x2, y2 = self.canvas.coords(self.action ["rectangle"])
            self.canvas.delete(self.action ["rectangle"])
            self.zoom(x1, y1, x2, y2)
            self.action = None

    def calcScales(self):
        if self.viewXMin == -1 or self.viewXMin < self.aMin:
            self.viewXMin = self.aMin
        if self.viewYMin == -1 or self.viewYMin < self.bMin:
            self.viewYMin = self.bMin

        if self.viewXMax == -1 or self.viewXMax > self.aMax:
            self.viewXMax = self.aMax
        if self.viewYMax == -1 or self.viewYMax > self.bMax:
            self.viewYMax = self.bMax

        # calc slopes
        baseX = float(self.viewXMax-self.viewXMin)
        if baseX == 0.0:
            baseY = 1.0
            self.viewXMax = self.viewXMin+1
        baseY = float(self.viewYMax-self.viewYMin)
        if baseY == 0.0:
            baseY = 1.0
            self.viewYMax = self.viewYMin+1
        self.slopeA = (self.width-self.borderLeft-self.borderRight)/baseX
        self.slopeB = (self.height-self.borderTop-self.borderBottom)/baseY
        
        self.slopeA = self.slopeA
        
        # calculate scrollbar dimensions
        width = float(self.aMax-self.aMin)
        if width > 0:
            lowX = self.viewXMin/width
            highX = self.viewXMax/width
        else:
            lowX = 0.0
            highX = 1.0
        self.hbar.set(lowX, highX)
        
        height = float(self.bMax-self.bMin)
        if height > 0:
            highY = 1.0 - self.viewYMin / height
            lowY = 1.0 - self.viewYMax / height
        else:
            lowY = 0.0
            highY = 1.0
        self.vbar.set(lowY, highY)

    def convAtoX(self, A):
        return self.borderLeft+self.slopeA*(A-self.viewXMin)
            
    def timeConversion(self):
        if self.xTypeTime == True and self.model.timescale == "minutes":
            return 60.0
        else:
            return 1.0

    def convBtoY(self, B):
        return self.height-self.borderBottom-self.slopeB*(B-self.viewYMin)

    def convXtoA(self, X):
        if self.allowZoom == False:
            return X
        return (X-self.borderLeft)/self.slopeA+self.viewXMin

    def convYtoB(self, Y):
        if self.allowZoom == False:
            return Y
        return (self.height-self.borderBottom-Y)/self.slopeB+self.viewYMin

    def initCanvas(self, keepZoom=False):
        self.setMaxValues()
        if self.keepZoom.get() == 0 and keepZoom == False:
            self.viewXMin = -1
            self.viewXMax = -1
            self.viewYMin = -1
            self.viewYMax = -1
            self.zoomHistory = []
        self._paintCanvas()

    def _paintCanvas(self, addToHistory=True):
        if addToHistory == True:
            self.zoomHistory.append((self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax))

        self.calcScales()
        self.canvas.delete(Tkinter.ALL)

        self.paintObject()
        self._paintAxis()

    def _paintAxis(self):

        # overpaint possible overflows
        self.canvas.create_rectangle(0, 0,
                                     self.borderLeft, self.height,
                                     fill=self.canvas["background"],
                                     outline=self.canvas["background"],
                                     width=0)
        self.canvas.create_rectangle(self.width-self.borderRight,
                                     0, self.width, self.height,
                                     fill=self.canvas["background"],
                                     outline=self.canvas["background"],
                                     width=0)
        self.canvas.create_rectangle(0, 0,
                                     self.width, self.borderTop,
                                     fill=self.canvas["background"],
                                     outline=self.canvas["background"],
                                     width=0)
        self.canvas.create_rectangle(0, self.height-self.borderBottom,
                                     self.width, self.height+1,
                                     fill=self.canvas["background"],
                                     outline=self.canvas["background"],
                                     width=0)

        # create axis
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMax)+10,
                                self.convBtoY(self.viewYMin),
                                tags=("axis", ), arrow="last")
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMax)-10,
                                tags=("axis", ), arrow="last")

        # search scale X
        start, end, diff, exp = findScale(self.viewXMin, self.viewXMax,
                                          self.NrXScales)
        while start < end:
            if start > self.viewXMin and start < self.viewXMax:
                x = self.convAtoX(start)
                y = self.convBtoY(self.viewYMin)
                if self.xTypeTime == True and self.model.timescale == "minutes":
                    self.canvas.create_text((x, y+5),
                                            text=shortNr(start/60.0, exp-2),
                                            anchor="n")
                else:
                    self.canvas.create_text((x, y+5),
                                            text=shortNr(start, exp),
                                            anchor="n")
                self.canvas.create_line(x, y, x, y+4)
            start += diff

        # search scale Y
        start, end, diff, exp = findScale(self.viewYMin, self.viewYMax,
                                          self.NrYScales)
        while start < end:
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convAtoX(self.viewXMin)
                y = self.convBtoY(start)
                self.canvas.create_text((x-5, y),
                                        text=shortNr(start, exp),
                                        anchor="e")
                self.canvas.create_line(x-4, y, x, y)
            start += diff

        # write axis description
        
        xText = self.xTitle
        if self.xTypeTime == True:
            if self.model.timescale == "minutes":
                xText = "rt [min]"
            else:
                xText = "rt [s]"
        item = self.canvas.create_text(self.convAtoX((self.viewXMin+self.viewXMax)/2.0),
                                       self.height-self.borderBottom/3.0,
                                       text=xText)

        item = self.canvas.create_text(self.borderLeft,
                                       self.borderTop/2.0,
                                       text=self.yTitle)


    def resetZoom(self, event):
        if self.allowZoom == False:
            return
        self.viewXMin = -1
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self._paintCanvas()

    def zoom(self, x1, y1, x2, y2):
        """ Zoom to pixelrange"""
        if self.allowZoom == False:
            return
        if x1 == x2 or y1 == y2:
            return
        xa = self.convXtoA(x1)
        xb = self.convXtoA(x2)
        # check if zoom is outside of canvas
        def testBorder(x, xmin, xmax):
            if x < xmin:
                x = xmin
            if x > xmax:
                x = xmax
            return x
        xa = testBorder(xa, self.viewXMin, self.viewXMax)
        xb = testBorder(xb, self.viewXMin, self.viewXMax)
        if xa == xb:
            return

        if xa < xb:
            self.viewXMin = xa
            self.viewXMax = xb
        else:
            self.viewXMin = xb
            self.viewXMax = xa

        ya = self.convYtoB(y1)
        yb = self.convYtoB(y2)

        ya = testBorder(ya, self.viewYMin, self.viewYMax)
        yb = testBorder(yb, self.viewYMin, self.viewYMax)
        if ya == yb:
            return

        if ya < yb:
            self.viewYMin = ya
            self.viewYMax = yb
        else:
            self.viewYMin = yb
            self.viewYMax = ya

        # check maximal parameters
        if self.viewXMax > self.aMax:
            self.viewXMax = self.aMax
        if self.viewXMin < self.aMin:
            self.viewXMin = self.aMin
        if self.viewYMax > self.bMax:
            self.viewYMax = self.bMax
        if self.viewYMin < self.bMin:
            self.viewYMin = self.bMin

        self._paintCanvas()
        
    def zoomToCoordinates(self, x1, y1, x2, y2):
        """ Zoom to datavalue range"""
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self.viewXMin = x1
        self.viewXMax = x2
        self.viewYMin = y1
        self.viewYMax = y2
        self._paintCanvas()

    def zoomBack(self, event):
        if len(self.zoomHistory) == 0:
            print "no history"
            return
        a, b, c, d = self.zoomHistory.pop(-1)
        if (a, b, c, d) == (self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax):
            self.zoomBack(event)
            return
        self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax = a, b, c, d
        self._paintCanvas()

def shortNr(nr, exp):
    # shorten nr if precision is necessary
    if exp <= 0:
        return round(nr, int(-exp+1))
    if exp > 4:
        e = int(math.floor(math.log(nr)/math.log(10)))
        b = round(nr/float(10**e), 4)
        return str(b)+"E"+str(e)
    return int(nr)

def findScale(start, end, NrScales):
    diff = abs(end-start)/NrScales
    exp = math.floor(math.log(diff)/math.log(10))
    base = 10**exp
    nr = diff/base
    if nr < 0 or nr >= 10:
        raise Exception("error in scaling")
    # choose nearest scale of [1, 2, 2.5, 5]
    scales = [1, 2, 2.5, 5]
    sortNr = [(abs(s-nr), s) for s in scales]
    sortNr.sort()
    diff = sortNr[0][1]*base

    startAxis = math.floor(start/diff)*diff
    endAxis = math.ceil(end/diff)*diff
    return startAxis, endAxis, diff, exp
