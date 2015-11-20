"""
Panel to set Filteroptions for all Data

""" 
import Tkinter
import ttk

class FieldTypes:
    INACTIVE=1
    ENTRY=2
    MENU=3

class Filter(object):
    
    def __init__(self,name):
        self.name = name
        self.field1 = ""
        self.choices1 = []
        self.type1 = FieldTypes.INACTIVE
        self.operator = ""
        self.operatorChoices = []
        self.field2 = ""
        self.choices2 = []
        self.type2 = FieldTypes.INACTIVE
        self.valid = False
    
    def parseValues(self, field1, operator, field2):
        raise Exception("overwrite this function!")
        
        
    def parseField1(self, field1):
        raise Exception("overwrite this function!")
        
    def parseField2(self, field1):
        raise Exception("overwrite this function!")
        
    def parseOperator(self, operator):
        assert operator in self.operatorChoices
        self.operator = operator
        
    
    def evaluate(self, obj, typ):
        raise Exception("overwrite this function!")
    
    def parseFloatRange(self, string):
        if not "-" in string:
            raise Exception("please provide a range")
        
        sp = string.replace(" ", "").split("-")
        if len(sp) != 2:
            raise Exception("use only one '-'")
        a,b = sp
        try:
            a = float(a)
            b = float(b)
            return a,b
        except:
            raise Exception("cannot convert to number")
            
    def parseFloat(self,string):
        try:
            return float(string)
        except:
            raise Exception("cannot convert to number")    
    
class EmptyFilter(Filter):
    def __init__(self):
        super(EmptyFilter, self).__init__("")
        self.type1 = FieldTypes.INACTIVE
        self.type2 = FieldTypes.INACTIVE
        self.operatorChoices = [""]
        
    def parseField1(self,field1):
        return
        
    def parseField2(self,field2):
        return

    def evaluate(self, obj, typ):
        return True

class GlycopeptideMass_Filter(Filter):
    def __init__(self):
        super(GlycopeptideMass_Filter, self).__init__("Glycopeptidemass")
        self.type1 = FieldTypes.INACTIVE
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = "="
        self.lowValue = 0
        self.highValue = 0
        self.value = 0
        
    def parseField1(self,field1):
        return
        
    def parseField2(self,field2):
        if self.operator == "=":
            a, b = self.parseFloatRange(field2)
            if a < b:
                self.lowValue, self.highValue = a, b
            else:
                 self.lowValue, self.highValue = b, a
            self.field2 = str(self.lowValue) + " - " + str(self.highValue)
        else:
            self.value = self.parseFloat(field2)
            self.field2 = str(self.value)
            self.field2 = str(self.value)

    def evaluate(self, hit, typ):
        if typ != "hit":
            return True
        mass = hit.glycan.mass + hit.peptide.mass
        if self.operator == "<":
            if mass < self.value:
                return True
            else:
                return False
        elif  self.operator == ">":
            if mass > self.value:
                return True
            else:
                return False
        else:
            if self.lowValue <= mass <= self.highValue:
                return True
            else:
                return False


class Fragmentmass_Filter(Filter):
    def __init__(self):
        super(Fragmentmass_Filter, self).__init__("Fragmentmass")
        self.field1 = "0 - 1"
        self.type1 = FieldTypes.ENTRY
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = "="
        self.lowIntensity = 0
        self.highIntensity = 0
        self.intensity = 0
        
        self.lowMass = 0
        self.highMass = 0
        
    def parseField1(self,field1):
        a, b = self.parseFloatRange(field1)
        if a < b:
            self.lowMass, self.highMass = a, b
        else:
             self.lowMass, self.highMass = b, a
        self.field1 = str(self.lowMass) + " - " + str(self.highMass)
        
    def parseField2(self,field2):
        if self.operator == "=":
            a, b = self.parseFloatRange(field2)
            if a < b:
                self.lowIntensity, self.highIntensity = a, b
            else:
                 self.lowIntensity, self.highIntensity = b, a
            self.field2 = str(self.lowIntensity) + " - " + str(self.highIntensity)
        else:
            self.intensity = self.parseFloat(field2)
            self.field2 = str(self.intensity)

    def evaluate(self, feature, typ):

        if typ != "feature":
            return True
        intensity = 0
        for peak in feature.consensus:
            if self.lowMass <= peak.x <= self.highMass:
                intensity += peak.y
                
        if self.operator == "<":
            if intensity < self.intensity:
                return True
            else:
                return False
        elif  self.operator == ">":
            if intensity > self.intensity:
                return True
            else:
                return False
        else:
            if self.lowIntensity <= intensity <= self.highIntensity:
                return True
            else:
                return False
                
                
class Fragmentname_Filter(Filter):
    def __init__(self):
        super(Fragmentname_Filter, self).__init__("Fragmentname")
        self.field1 = "Fragmentname"
        self.type1 = FieldTypes.ENTRY
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.INACTIVE
        self.operatorChoices = ["exists", "exists not"]
        self.operator = "exists"
        
    def parseField1(self,field1):
        self.field1 = field1
        
    def parseField2(self,field2):
        return

    def evaluate(self, hit, typ):

        if typ != "hit":
            return True
                
        if self.operator == "exists":
            if self.field1 in hit.fragments:
                return True
            else:
                return False
        else:
            if self.field1 in hit.fragments:
                return False
            else:
                return True

class FilterEntry(ttk.Frame):
    def __init__(self, master, model, definedFilter=None):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        # | type | <Field1> | Operator | <Field2> |
        
        self.traceChanges = True
        
        button = Tkinter.Button(self, text=" - ", command=self.delete)
        button.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        
        # register new filters here
        self.filters = []
        self.filters.append(EmptyFilter())
        self.filters.append(GlycopeptideMass_Filter())
        self.filters.append(Fragmentmass_Filter())
        self.filters.append(Fragmentname_Filter())

        self.var = Tkinter.StringVar(self)
        
        self.currentFilter = self.filters[0]
        
        self.var.set(self.currentFilter.name)
        self.var.trace("w", self.filterChanged)
        
        self.currentOperator = self.currentFilter.operator

        choices = []
        for f in self.filters:
            choices.append(f.name)
            
        option = Tkinter.OptionMenu(self, self.var, *choices)
        option.grid(row=0, column=1, sticky=("N", "W", "E", "S"))

        self.field1Var = Tkinter.StringVar(self)
        self.field1Var.trace("w", self.valuesChanged)
        self.entry1 = Tkinter.Entry(self, textvariable=self.field1Var)
        self.entry1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
        
        choices = ['', ]
        self.options1 = Tkinter.OptionMenu(self, self.field1Var, *choices)
        self.options1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))

        self.operatorVar = Tkinter.StringVar(self)
        self.operatorVar.trace("w", self.valuesChanged)
        choicesOperator = ['', ]
        self.optionOperator = Tkinter.OptionMenu(self, self.operatorVar, *choicesOperator)
        self.optionOperator.grid(row=0, column=3, sticky=("N", "W", "E", "S"))
        
        self.field2Var = Tkinter.StringVar(self)
        self.field2Var.trace("w", self.valuesChanged)
        self.entry2 = Tkinter.Entry(self, textvariable=self.field2Var)
        self.entry2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        
        choices = ['', ]
        self.options2 = Tkinter.OptionMenu(self, self.field2Var, *choices)
        self.options1.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        
        if definedFilter != None:
            self.currentFilter = definedFilter
        self.traceChanges = False
        self.paintCurrentFilter()
        self.traceChanges = True
        
    def valuesChanged(self, *args):
        if self.traceChanges == False:
            return
        self.currentFilter.valid = True
        try:
            self.currentFilter.parseField1(self.field1Var.get())
            self.entry1.config(bg="grey")
            self.options1.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.entry1.config(bg="red")
            self.options1.config(bg="red")
            
        try:
            self.currentFilter.parseOperator(self.operatorVar.get())
            self.optionOperator.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.optionOperator.config(bg="red")
                     
        try:
            self.currentFilter.parseField2(self.field2Var.get())
            self.entry2.config(bg="grey")
            self.options2.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.entry2.config(bg="red")
            self.options2.config(bg="red")
 
    def filterChanged(self, *args):
        if self.traceChanges == False:
            return
        name = self.var.get()
        if self.currentFilter.name == name:
            return
        # remove currentFilter from model
        if self.currentFilter in self.model.filters["Identification"]:
            self.model.filters["Identification"].remove(self.currentFilter)
        
        self.currentFilter = None
        for f in self.filters:
            if f.name == name:
                self.currentFilter = f
        if self.currentFilter == None:
            raise Exception("Unknown Filter")
                
        self.paintCurrentFilter()

        self.model.filters["Identification"].append(self.currentFilter)

    def paintCurrentFilter(self):
        self.traceChanges = False
        self.var.set(self.currentFilter.name)
        
        if self.currentFilter.type1 == FieldTypes.INACTIVE:
            self.entry1.grid_remove()
            self.options1.grid_remove()
        elif self.currentFilter.type1 == FieldTypes.ENTRY:
            self.entry1.grid()
            self.options1.grid_remove()
            self.field1Var.set(self.currentFilter.field1)
        else:
            self.entry1.grid_remove()
            self.options1.grid()
            self.setMenuChoices(self.options1,self.currentFilter.choices1, self.field1Var)
        
        self.setMenuChoices(self.optionOperator, self.currentFilter.operatorChoices, self.operatorVar)
        self.operatorVar.set(self.currentFilter.operator)
            
        if self.currentFilter.type2 == FieldTypes.INACTIVE:
            self.entry2.grid_remove()
            self.options2.grid_remove()
        elif self.currentFilter.type2 == FieldTypes.ENTRY:
            self.entry2.grid()
            self.options2.grid_remove()
            self.field2Var.set(self.currentFilter.field2)
            
        else:
            self.entry2.grid_remove()
            self.options2.grid()
            self.setMenuChoices(self.options2,self.currentFilter.choices2, self.field2Var)
        self.traceChanges = True
        self.valuesChanged()
        
        
    def setMenuChoices(self, menu, choices, var):
        self.traceChanges = False
        menu['menu'].delete(0, 'end')
        if len(choices) == 0:
            var.set("")
            return
        var.set(choices[0])
        for choice in choices:
            menu['menu'].add_command(label=choice, command=Tkinter._setit(var, choice))
        self.traceChanges = True

    def delete(self):
        self.grid_forget()
        if self.currentFilter in self.model.filters["Identification"]:
            self.model.filters["Identification"].remove(self.currentFilter)
        return

class FilterPanel(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.model = model
        self.title("Filter Options")
        
        
        button = Tkinter.Button(self, text="add Filter", command=self.addFilter)
        button.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        
        self.N = 0
        self.filters = []
        self.filterFrame = ttk.Frame(self, width=100, height=30)
        self.filterFrame.grid(row=1, column=0, sticky=("N", "W", "E", "S"))
        
        # add predefined filters
        for f in self.model.filters["Identification"]:
            print f.field1, f.operator, f.field2
            self.addFilter(f)
        
    def addFilter(self, definedFilter=None):
        f = FilterEntry(self.filterFrame, self.model, definedFilter=definedFilter)
        f.grid(row=self.N, column=0, sticky=("N", "W", "E", "S"))
        self.N += 1
        
