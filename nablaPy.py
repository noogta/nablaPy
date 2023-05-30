from configparser import Interpolation
from matplotlib import projections
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import struct
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.filedialog import askopenfile
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from copy import deepcopy
import pickle

font_size = {"small": 9, "normal": 10, "large": 11, "Large": 12}
text_color = "#000000"
background_color = "#FFFFFF"

def label_frame(parent, label):
    font_style = tkFont.Font(family = font_family, size = font_size["normal"], weight = "normal")
    labelframe=LabelFrame(parent, text=label, bg=background_color, fg = text_color, font = font_style, relief = "raised")
    return labelframe

def frame(parent):
    frame = Frame(parent, bg = background_color, relief = "raised")
    return frame

def combobox(parent, options):
    font_style = tkFont.Font(family = font_family, size = font_size["large"], weight = "normal")
    combobox = ttk.Combobox(parent, value = options, font = font_style,state = "readonly")
    return combobox

def entry(parent):
    font_style = tkFont.Font(family = font_family, size = font_size["normal"], weight = "normal")
    return Entry(parent, bg = background_color, fg = text_color, font = font_style)

def label(parent, label):
    font_style = tkFont.Font(family = font_family, size = font_size["normal"], weight = "normal")
    return Label(parent, text=label ,bg = background_color, fg = text_color, font = font_style)


class Projet:
    def __init__(self, path_folder, name):
        self.path_folder=path_folder
        self.path_list=self.set_file()
        self.mesure_list=self.set_mesure_path()
        self.name_list=self.set_name()
        self.name=name
        self.config=Config_slice()
        
    def set_file(self):
        L=[]
        for root, dirs, files in os.walk(self.path_folder):
            for file in files:
                L.append(os.path.join(root,file))
        return sorted(L)

    def set_mesure_path(self):
        L=[]
        for path in self.path_list:
            if path.endswith('_1.rad'):
                L.append(Mesure(path))
        return L

    def set_mesure_param(self, path):
        L=[]
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.nablapy'):
                    final_directory = os.path.join(path, file)
                    param=pickle.load(open( final_directory, "rb" ) )
                    L.append(param)
        for k in range(len(self.mesure_list)):
            self.mesure_list[k].param.update(L[k])
    
        
        
    
    def set_name(self):
        L=[]
        for path in self.path_list:
            if path.endswith('_1.rad'):
                L.append(os.path.splitext(os.path.basename(path))[0])
        return L

class Mesure:
    def __init__(self, path):
        self.path=path
        self.name=os.path.splitext(os.path.basename(self.path))[0]
        self.param=Parametres()
        self.radar=Radar(self.path, self.param)
        self.traitement=Traitement(self.radar, self.param)
        self.param.tc_end=self.radar.getSamples()
        self.param.path=self.path
        
        
    def path_data(self):
        return self.radar.path_rd3()
    def nbSamples(self):
        return self.radar.getSamples()
    def nbTraces(self):
        return self.radar.getTraces()
    def Dt(self):
        return self.radar.getDt()

class Radar:
    def __init__(self, path, param):
        self.path=path[:-6]
        self.param=param

    def path_rad(self):
        return self.bi_freq()[0]

    def path_rd3(self):
        return self.bi_freq()[1]  

    def bi_freq(self):
        if affichage.freq=="High":
            return self.path+"_1.rad",self.path+"_1.rd3"
        if affichage.freq=="Low":
            return self.path+"_2.rad",self.path+"_2.rd3"

    def get_info(self):
        rad=open(self.path_rad(),"r")
        rad_info=rad.readlines()
        rad.close()
        info={}
        for line in rad_info:
            line=line.strip('\n')
            line=line.split(':')
            info[str(line[0])]=line[1]
        return info

    def getTraces(self):
        return int(self.get_info()["LAST TRACE"])
    def getSamples(self):
        return int(self.get_info()["SAMPLES"]) 
    def getTimewindow(self):
        return float(self.get_info()["TIMEWINDOW"]) 
    def getDx(self):
        return float(self.get_info()["DISTANCE INTERVAL"])
    def getDt(self):
        return self.getTimewindow()/self.getSamples()
    def listsamples(self):
        return [i for i in range(self.getSamples())]
    def getDx(self):
        if self.param.dx_edit==False:
            return float(self.get_info()["DISTANCE INTERVAL"])
        else:
            return self.param.dx_edit_val
class Parametres:
    path=""
    name=""
    c_gain=1
    a_exp=1
    b_exp=0
    a_line=1
    b_line=0
    g_cst=False
    g_exp=False
    g_line=False
    epsilon=8
    c=299792458
    tc_start=0
    tc_end=0
    scope=0
    sub_mean=False
    mean=0
    invert=False
    trace_reduction=False
    reduction=100
    dewow=False
    dx_edit=False
    dx_edit_val=0

    def update(self,newdata):
        for key,value in newdata.items():
            setattr(self,key,value)
            
class Affichage:
    y_unit="Temps (ns)"
    x_unit="Traces"
    color="Greys"
    freq="High"
    interpolation="nearest"
    grid=None
    nbTick=20
    plot_scale=25000

class Config_slice:
    z_unit="Samples"
    interline=50
    slice_color="tab20c"
    nbTick=20
    max_auto=False
    start=10
    end=50
    grid=False
    inv=False
    slice_cut_start=0
    slice_cut_end=0
    flip=False

class Slice:
    def __init__(self, mesure_list, config):
        self.mesure_list=mesure_list
        self.config=config
        self.data_list=[]
        for mesure in self.mesure_list:
            self.data_list.append(mesure.traitement.get_rd3())

    def plot(self, slice):
        Slicing(self.mesure_list, self.config).plot(slice)
  
    def get_slice(self, n):
        slice=[]
        for k in range(len(self.data_list)):
            a=list(self.data_list[k][n])
            slice.append(a)
        return self.filler(slice)

    def filler(self, slice):
        maxlen=self.find_max_list(slice)
        for line in slice:
            m=maxlen-len(line)
            for k in range(m):
                line.insert(0,0)
        return slice

    def find_max_list(self, list):
        list_len = [len(i) for i in list]
        return max(list_len)

    def meaner(self):
        start=self.mesure_list[0].traitement.conversion(self.config.start, "Temps (ns)", "Samples")
        end=self.mesure_list[0].traitement.conversion(self.config.end, "Temps (ns)", "Samples")
        if self.config.slice_cut==True:
            return self.slice_cut(np.mean( np.array([np.absolute(self.get_slice(k)) for k in range(start, end)]), axis=0 ))

        else:
            return np.mean( np.array([np.absolute(self.get_slice(k)) for k in range(start, end)]), axis=0 )

    def invert_trace(self):
        for k in range(0, len(self.data_list), 2):
            self.data_list[k]=np.fliplr(self.data_list[k])
    
    def flip_slice(self):
        for k in range(0, len(self.data_list)):
            self.data_list[k]=np.fliplr(self.data_list[k])

    def slice_cut(self, slice_mean):
        start=self.mesure_list[0].traitement.conversion(self.config.slice_cut_start, "Distance (m)", "Traces")
        end=self.mesure_list[0].traitement.conversion(self.config.slice_cut_end, "Distance (m)", "Traces")
        m=len(slice_mean[0])-end
        L=[k for k in range(start)]+[k for k in range(m, len(slice_mean[0]))]
        slice_mean=np.delete(slice_mean, L, axis=1)
        return slice_mean


    def save(self, name):
        pass

    def gainstatique(self, c):
        for rd3 in self.data_list:
            rd3=np.multiply(rd3, float(c))

    def gainlin(self, a, t0):
        t0=self.mesure_list[0].traitement.conversion(t0, affichage.y_unit, "Samples")
        for rd3 in self.data_list:
            samples, Traces=rd3.shape
            L=[k for k in range(samples)]
            fgain=np.ones(samples)
            fgain[t0:]=[a*(x-t0)+1 for x in L[t0:]]
            for trace in range(Traces):
                rd3[:, trace] = rd3[:, trace] * np.array(fgain).astype(dtype=rd3.dtype)

    def gainexp(self, a, t0):
        t0=self.mesure_list[0].traitement.conversion(t0, affichage.y_unit, "Samples")
        for rd3 in self.data_list:
            b=np.log(1/a)/t0
            samples, Traces=rd3.shape
            fgain=np.ones(samples)
            L=[k for k in range(samples)]
            fgain=[(a*(np.exp(b*(x)) - 1) + 1) for x in L]
            for trace in range(Traces):
                rd3[:, trace] = rd3[:, trace] * np.array(fgain).astype(dtype=rd3.dtype)

    def apply(self):
        if self.config.flip==True:
            self.flip_slice()
        if self.config.inv==True:
            self.invert_trace()
        if self.mesure_list[0].param.g_line==True:
            self.gainlin(self.mesure_list[0].param.a_line,self.mesure_list[0].param.b_line)
        if self.mesure_list[0].param.g_exp==True:
            self.gainexp(self.mesure_list[0].param.a_exp,self.mesure_list[0].param.b_exp)
        if self.mesure_list[0].param.g_cst==True:
            self.gainstatique(self.mesure_list[0].param.c_gain)
        slice=self.meaner()
        self.plot(slice)
        return slice




class Traitement:
    def __init__(self, radar, param):
        self.radar=radar
        self.param=param
        self.listsamples=radar.listsamples()
        
    
    def get_rd3(self):
        with open(self.radar.path_rd3(), mode='rb') as rd3data:
            rd3data=rd3data.read()
        rd3=struct.unpack("h"*((len(rd3data))//2), rd3data)
        rd3=np.reshape(rd3,(self.radar.getTraces(),self.radar.getSamples()))
        rd3=np.transpose(rd3)
        return rd3

    def invert(self):
        self.data_mod=np.fliplr(self.data_mod)

    def conversion(self, u: float, unit_1, unit_2):
        if u==0:
            return 0
        if u==None:
            return None
        if unit_1==unit_2:
            return u
        if unit_1=="Samples" and unit_2=="Temps (ns)":
            return round(u*self.radar.getDt())
        elif unit_1=="Temps (ns)" and unit_2=="Samples":
            return round(u/self.radar.getDt())
        elif unit_1=="Temps (ns)" and unit_2=="Distance (m)":
            return round((u*1e-9*self.param.c)/(2*(self.param.epsilon**0.5)), 2)
        elif unit_1=="Samples" and unit_2=="Distance (m)":
            return round((u*self.radar.getDt()*1e-9*self.param.c)/(2*(self.param.epsilon**0.5)), 2)
        elif unit_1=="Distance (m)" and unit_2=="Temps (ns)":
            return round((u*2*(self.param.epsilon**0.5))/(1e-9*self.param.c))
        elif unit_1=="Distance (m)" and unit_2=="Samples":
            return round((u*2*(self.param.epsilon**0.5))/(self.radar.getDt()*1e-9*self.param.c))
        elif unit_1=="Traces" and unit_2=="Distance (m)":
            return u*self.radar.getDx()
        elif unit_1=="Distance (m)" and unit_2=="Traces":
            return round(u/self.radar.getDx())

    def time_cut(self):
        self.listsamples_mod=self.radar.listsamples()[self.param.tc_start:self.param.tc_end]
        self.data_mod=self.data_mod[self.param.tc_start:self.param.tc_end]

    def gainlin(self, a, t0):
        samples, Traces=self.data_mod.shape
        fgain=np.ones(samples)
        fgain[t0:]=[a*(x-t0)+1 for x in self.radar.listsamples()[t0:]]
        for trace in range(Traces):
            self.data_mod[:, trace] = self.data_mod[:, trace] * np.array(fgain).astype(dtype=self.data_mod.dtype)

    def gainstatique(self, c):
        self.data_mod=np.multiply(self.data_mod, float(c))

    def gainexp(self, a, t0):
        b=np.log(1/a)/t0
        samples, Traces=self.data_mod.shape
        fgain=np.ones(samples)
        fgain=[(a*(np.exp(b*(x)) - 1) + 1) for x in self.radar.listsamples()]
        for trace in range(Traces):
            self.data_mod[:, trace] = self.data_mod[:, trace] * np.array(fgain).astype(dtype=self.data_mod.dtype)
    
    def sub_mean(self, k):
        if k==0:
            mean_tr = np.mean(self.data_mod, axis=1)
            ns, ntr = self.data_mod.shape
            for n in range(ntr):
                self.data_mod[:,n] = self.data_mod[:,n] - mean_tr
        else:
            start=k
            end=self.radar.getTraces()-k
            ls=np.arange(start, end, 1)
            for n in ls:
                mean_tr = np.mean(self.data_mod[:, int(n-k):int(n+k)], axis=1)
                self.data_mod[:,int(n)] = self.data_mod[:,int(n)] - mean_tr
            mean_l = np.mean(self.data_mod[:, 0:int(start)], axis=1)
            mean_r = np.mean(self.data_mod[:, int(end):int(self.radar.getTraces())], axis=1)
            for n in np.arange(0, start, 1):
                self.data_mod[:,int(n)] = self.data_mod[:,int(n)] - mean_l
            for n in np.arange(end, self.radar.getTraces(), 1):
                self.data_mod[:,int(n)] = self.data_mod[:,int(n)] - mean_r
        
    def trace_reduction(self, n):
        if n<100:
            p=round((n*self.radar.getTraces())/100)
            L=np.linspace(0,self.radar.getTraces()-1, p, dtype = int)
            self.data_mod=np.delete(self.data_mod,L,1)

    def dewow(self):
        mean_s = np.mean(self.data_mod, axis=0)
        self.data_mod=self.data_mod-mean_s

    def save_png(self, name, png, projet, mesure):
        path_folder = os.path.join(os.path.dirname(__file__), name)
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
        if png=="1 seul":
            Radargramme(mesure).save(path_folder)
        else:
            for k in range(len(projet.mesure_list)):
                Radargramme(projet.mesure_list[k]).save(path_folder)



    def apply(self):
        self.data_mod=self.get_rd3()
        self.listsamples_mod=self.listsamples.copy()
        if self.param.trace_reduction==True:
            self.trace_reduction(self.param.reduction)
        if self.param.dewow==True:
            self.dewow()
        if self.param.invert==True:
            self.invert()
        if self.param.sub_mean==True:
            self.sub_mean(self.param.mean)
        if self.param.g_line==True:
            self.gainlin(self.param.a_line, self.param.b_line)
        if self.param.g_exp==True:
            self.gainexp(self.param.a_exp, self.param.b_exp)
        if self.param.g_cst==True:
            self.gainstatique(self.param.c_gain)
        self.time_cut()
        return self.data_mod, self.listsamples_mod

class Radargramme:
    def __init__(self, mesure):
        self.mesure=mesure
        self.rd3=mesure.traitement.apply()[0]
        self.listsamples=mesure.traitement.apply()[1]

    def Y_list(self):
        if affichage.y_unit == "Temps (ns)":
            return np.multiply(self.listsamples,self.mesure.radar.getDt())
        if affichage.y_unit == "Samples":
            return self.listsamples
        if affichage.y_unit=="Distance (m)":
            return np.multiply(self.listsamples, (self.mesure.radar.getDt()*1e-9*self.mesure.param.c)/(2*(self.mesure.param.epsilon**0.5)))

    def X_list(self):
        if affichage.x_unit=="Distance (m)":
            dx=self.mesure.radar.getDx()
            return np.multiply(np.arange(0, self.mesure.radar.getTraces(), 1), dx)
        if affichage.x_unit=="Traces":
            return np.arange(0, self.mesure.radar.getTraces(), 1)

    def plot(self):
        figu=plt.figure(figsize=(9,9))
        radargramme=figu.add_subplot(1,1,1)
        figu.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.06)
        img=radargramme.imshow(self.rd3, interpolation=affichage.interpolation, cmap=affichage.color, aspect='auto', extent=[0,self.X_list()[-1],self.Y_list()[-1],0])
        img.set_clim(-affichage.plot_scale,affichage.plot_scale)
        radargramme.xaxis.set_ticks_position("top")
        if affichage.grid==True:
            plt.grid(axis=Y, linewidth = 0.3, color="black", linestyle='-')
        plt.axvline(self.mesure.traitement.conversion(self.mesure.param.scope, "Traces", affichage.x_unit), color='r', linewidth=0.8)
        plt.xticks(fontsize= 8)
        plt.yticks(fontsize= 8)
        plt.locator_params(axis='y', nbins=affichage.nbTick)
        plt.locator_params(axis='x', nbins=affichage.nbTick)
        plt.title(str(self.mesure.name), fontsize=7, y=-0.01)
        canvas = FigureCanvasTkAgg(figu, master=Dframe.plot_frame)
        canvas.get_tk_widget().grid(row=0,column=0)
        canvas.draw()
        plt.close(figu)

    def save(self, path_folder):
        figu=plt.figure(figsize=(6,3))
        radargramme=figu.add_subplot(1,1,1)
        radargramme.xaxis.set_ticks_position("top")
        radargramme.xaxis.set_label_position('top')
        plt.xticks(fontsize= 5)
        plt.yticks(fontsize= 5)
        plt.locator_params(axis='y', nbins=affichage.nbTick)
        plt.locator_params(axis='x', nbins=affichage.nbTick)
        img=radargramme.imshow(self.rd3, cmap=affichage.color, interpolation=affichage.interpolation, aspect='auto', extent=[0,self.X_list()[-1],self.Y_list()[-1],0])
        plt.ylabel(affichage.y_unit, fontsize=6)
        plt.xlabel(affichage.x_unit, fontsize=6)
        img.set_clim(-affichage.plot_scale,affichage.plot_scale)
        figu.savefig(os.path.join(path_folder,self.mesure.name+'.png'), dpi=1000, format='png', bbox_inches='tight')
        plt.close(figu)

class Slicing:
    def __init__(self, mesure_list, config):
        self.mesure_list=mesure_list
        self.config=config
        self.figu=plt.figure(figsize=(7,7))
        self.slice=self.figu.add_subplot(1,1,1)
        self.figu.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.06)
        self.slice.xaxis.set_ticks_position("top")
        plt.xticks(fontsize= 8)
        plt.yticks(fontsize= 8)

    def X_list(self, slice):
        nbTraces=len(slice[0])
        dx=self.mesure_list[0].radar.getDx()
        return np.multiply(np.arange(0, nbTraces, 1),dx)

    def Y_list(self, slice):
        dy=self.config.interline/100
        n=len(slice)
        return np.arange(0,n*dy, dy)

    def plot(self, slice):
        img=self.slice.imshow(slice ,origin='lower', interpolation='gaussian', cmap=self.config.slice_color, aspect='auto', extent=[0, self.X_list(slice)[-1], self.Y_list(slice)[-1],0 ])
        plt.locator_params(axis='x', nbins=self.config.nbTick)
        plt.locator_params(axis='y', nbins=self.config.nbTick)
        if self.config.max_auto==True:
            self.figu.colorbar(img, orientation="horizontal",aspect=50)
            max=slice.max()
            img.set_clim(0,max)
        else:
            self.figu.colorbar(img, orientation="horizontal",aspect=50)
            img.set_clim(0,25000)
        if self.config.grid==True:
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        canvas = FigureCanvasTkAgg(self.figu, master=Dframe.slice_frame)
        canvas.get_tk_widget().grid(row=0, column=0)
        canvas.draw()
        plt.close(self.figu)

    def save(self, slice, name):
        slice_mean=slice
        figu=plt.figure(figsize=(4,4))
        slice=figu.add_subplot(1,1,1)
        plt.xticks(fontsize= 7)
        plt.yticks(fontsize= 7)
        plt.locator_params(axis='x', nbins=self.config.nbTick)
        plt.locator_params(axis='y', nbins=self.config.nbTick)
        img=slice.imshow(slice_mean ,origin='lower', interpolation='gaussian', cmap=self.config.slice_color, aspect='auto', extent=[0, self.X_list(slice_mean)[-1], self.Y_list(slice_mean)[-1],0 ])
        figu.colorbar(img, orientation="horizontal",aspect=50)
        if self.config.max_auto==True:
            max=slice_mean.max()
            img.set_clim(0,max)
        else:
            img.set_clim(0,25000)
        if self.config.grid==True:
            plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
        figu.savefig(os.path.join(os.path.dirname(__file__),name+'.png'), dpi=1000, format='png', bbox_inches='tight')
        plt.close(figu)
    
class Scope:
    def __init__(self, mesure):
        self.mesure=mesure
        self.rd3=mesure.traitement.apply()[0]
        self.listsamples=mesure.traitement.apply()[1]

    def Y_list(self):
        if affichage.y_unit == "Temps (ns)":
            return np.multiply(self.listsamples,self.mesure.radar.getDt())
        if affichage.y_unit == "Samples":
            self.Y_label="Samples"
            return self.listsamples
        if affichage.y_unit=="Distance (m)":
            return np.multiply(self.listsamples, self.mesure.radar.getDt()*1e-9*self.mesure.param.c/(2*(self.mesure.param.epsilon**0.5)))

    def plot(self, n):
        figu=plt.figure(figsize=(1.5,9))
        scope=figu.add_subplot(1,1,1)
        scope.plot([line[n] for line in self.rd3], self.Y_list(), color='black', linewidth=0.3)
        scope.invert_yaxis()
        scope.axes.get_xaxis().set_visible(False)
        scope.axes.get_yaxis().set_visible(False)
        figu.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.06)
        plt.margins(0)
        plt.axvline(x=0, color="g", linewidth=0.3)
        canvas = FigureCanvasTkAgg(figu, master=Dframe.plot_frame)
        canvas.get_tk_widget().grid(row=0,column=1)
        canvas.draw()
        plt.close(figu)

class Tool:
    def __init__(self, parent):
        self.tool_frame_label(parent)
        self.work=False
    
    def tool_frame_label(self, parent):
        tool_frame = label_frame(parent, "Parametres")
        tool_frame.configure(width=300)
        tool_frame.pack(side=LEFT,fill=Y, expand=0, padx=5, pady=5)
        tool_frame.grid_propagate(0)
        tool_frame.pack_propagate(0)
        self.fill_tool_frame(tool_frame)

    def fill_tool_frame(self, parent):
        project_frame=Frame(parent)
        project_frame.pack(side="top", fill = BOTH)
        self.fill_project_frame(project_frame)

        self.unit_frame=Frame(parent)
        self.unit_frame.pack(side="top", fill = BOTH)

        self.scope_frame=Frame(parent)
        self.scope_frame.pack(side="top", fill = BOTH)
        
        self.edit_frame=Frame(parent)
        self.edit_frame.pack(side="top", fill = BOTH)

        self.apply=Button(parent, text="Appliquer", command=lambda: [self.update()])
        self.apply.pack(side="bottom", fill="both")
        

    def fill_project_frame(self, parent):
        new=Button(parent, text="Ouvrir un dossier", command=lambda: self.new_project("projet"))
        new.grid(row=0, columnspan=2, sticky=W+E)
        self.name_box=Listbox(parent,selectmode=SINGLE, width=30)
        self.name_box.grid(row=1, columnspan=2, sticky=W+E)
        self.name_box.bind('<<ListboxSelect>>', self.select)

    def new_project(self, label):
        path=filedialog.askdirectory(title="Selectionner un dossier")
        if path:
            if self.work==True:
                self.tabControl.destroy()
                self.projet=Projet(path, label)          
                self.name_box.delete(0,END)
                for name in self.projet.name_list:
                    self.name_box.insert(END, name)
                self.fill_unit_frame(self.unit_frame)
                self.fill_edit_frame(self.edit_frame)
                Dframe.fill_tab_slice(Dframe.tabSlice, self.projet)
                self.work=True
                print("ok")
            else:
                self.projet=Projet(path, label)          
                self.name_box.delete(0,END)
                for name in self.projet.name_list:
                    self.name_box.insert(END, name)
                self.fill_unit_frame(self.unit_frame)
                self.fill_edit_frame(self.edit_frame)
                Dframe.fill_tab_slice(Dframe.tabSlice, self.projet)
                self.work=True
            
    
    def select(self, evt):
        w = evt.widget
        self.index = int(w.curselection()[0])+1
        if self.index:
            name = w.get(self.index)
            self.mesure=self.projet.mesure_list[self.index-1]
            self.reset_frame()
            self.set_frame()
            self.init()
            self.plot()

    def set_frame(self):
        self.fill_tab_gains(self.tabGains)
        self.fill_tab_filtres(self.tabFiltres)
        self.fill_tab_info(self.tabInfo)
        self.fill_tab_save(self.tabSave)
        self.fill_unit_frame(self.unit_frame)
        self.fill_scope_scale(self.scope_frame)
        

    def reset_frame(self):
        for tab in [self.tabGains, self.tabFiltres, self.tabInfo, self.scope_frame, self.tabSave]:
            for widget in tab.winfo_children():
                widget.destroy()

    def init(self):
        self.start_tc.set(self.mesure.traitement.conversion(self.mesure.param.tc_start, "Samples", affichage.y_unit))
        self.end_tc.set(self.mesure.traitement.conversion(self.mesure.param.tc_end, "Samples", affichage.y_unit))
        if self.mesure.param.g_exp==True:
            self.g_exp.set(1)
        else: self.g_exp.set(0)
        if self.mesure.param.g_cst==True:
            self.g_cst.set(1)
        else: self.g_cst.set(0)
        if self.mesure.param.g_line==True:
            self.g_line.set(1)
        else: self.g_line.set(0)
        if self.mesure.param.sub_mean==True:
            self.sub_mean.set(1)
        else: self.sub_mean.set(0)
        if self.mesure.param.trace_reduction==True:
            self.trace_reduction.set(1)
        else: self.trace_reduction.set(0)
        if self.mesure.param.invert==True:
            self.invert.set(1)
        else: self.invert.set(0)
        if self.mesure.param.dewow==True:
            self.dewow.set(1)
        else: self.dewow.set(0)
        if affichage.grid==True:
            self.grid.set(1)
        else: self.grid.set(0)
        self.gain_exp_t0.insert(END, str(self.mesure.traitement.conversion(self.mesure.param.b_exp, "Samples", affichage.y_unit)))
        self.gain_exp_a.insert(END, str(self.mesure.param.a_exp))
        self.gain_line_a.insert(END, str(self.mesure.param.a_line))
        self.gain_line_t0.insert(END, str(self.mesure.traitement.conversion(self.mesure.param.b_line, "Samples", affichage.y_unit)))
        self.eps.insert(END, str(self.mesure.param.epsilon))
        self.scope_scale.set(self.mesure.param.scope)
        self.tick.set(affichage.nbTick)
        self.interpolation.set(affichage.interpolation)
        self.move_avg.set(self.mesure.param.mean)
        self.traces.set(self.mesure.param.reduction)
        self.gain_c.insert(END, str(self.mesure.param.c_gain))


    def plot(self):
        Radargramme(self.mesure).plot()
        Scope(self.mesure).plot(self.mesure.param.scope)

    def fill_edit_frame(self, parent):
        self.tabControl=ttk.Notebook(parent)
        self.tabGains=Frame(self.tabControl)
        self.tabFiltres=Frame(self.tabControl)
        self.tabInfo=Frame(self.tabControl)
        self.tabSave=Frame(self.tabControl)
        self.tabControl.add(self.tabGains, text="Gains")
        self.tabControl.add(self.tabFiltres, text="Filtres")
        self.tabControl.add(self.tabInfo, text="Info")
        self.tabControl.add(self.tabSave, text="Save")
        self.tabControl.pack(side="top")
        

    def fill_unit_frame(self, parent):
        Label(parent, text="Couleur").grid(row=0, column=0, sticky=W+E)
        self.colorbox=combobox(parent, ["seismic","Greys", "jet"])
        self.colorbox.set(affichage.color)
        self.colorbox.grid(row=0, column=1, sticky=W)

        Label(parent, text="Unité ordonée").grid(row=1, column=0, sticky=W+E)
        self.y_unit=combobox(parent, ["Temps (ns)","Samples","Distance (m)"])
        self.y_unit.set(affichage.y_unit)
        self.y_unit.grid(row=1, column=1, sticky=W)

        Label(parent, text="Unité abscisse").grid(row=2, column=0, sticky=W+E)
        self.x_unit=combobox(parent, ["Traces","Distance (m)"])
        self.x_unit.set(affichage.x_unit)
        self.x_unit.grid(row=2, column=1, sticky=W)

        Label(parent, text="Fréquence").grid(row=3, column=0, sticky=W+E)
        self.freq=combobox(parent, ["Low","High"])
        self.freq.set(affichage.freq)
        self.freq.grid(row=3, column=1, sticky=W)

    def fill_scope_scale(self, parent):
        Label(parent, text="Scope numéro").grid(row=0, column=0, sticky=W+E)
        self.scope_scale=Scale(parent, from_=0, to=self.mesure.radar.getTraces(), orient=HORIZONTAL)
        self.scope_scale.grid(row=0, column=1, sticky=W+E)
        self.scope_scale.set(self.mesure.param.scope)
    
    def fill_tab_gains(self, parent):
        if affichage.y_unit=="Distance (m)":
            res=0.01
        else: res=1
        Label(parent, text="Découpage").grid(row=0, columnspan=2, sticky=W+E)

        Label(parent, text="Début "+str(affichage.y_unit)).grid(row=1, column=0, sticky=W+E)
        self.start_tc=Scale(parent, from_=0, to=self.mesure.traitement.conversion(self.mesure.radar.getSamples(), "Samples", affichage.y_unit), orient=HORIZONTAL, resolution=res)
        self.start_tc.grid(row=1, column=1, sticky=W+E)
        self.start_tc.set(self.mesure.traitement.conversion(self.mesure.param.tc_start, "Samples", affichage.y_unit))

        Label(parent, text="Fin "+str(affichage.y_unit)).grid(row=2, column=0, sticky=W+E)
        self.end_tc=Scale(parent, from_=0, to=self.mesure.traitement.conversion(self.mesure.radar.getSamples(), "Samples", affichage.y_unit), orient=HORIZONTAL, resolution=res)
        self.end_tc.grid(row=2, column=1, sticky=W+E)
        self.end_tc.set(self.mesure.traitement.conversion(self.mesure.param.tc_end, "Samples", affichage.y_unit))


        ttk.Separator(parent).grid(row=3, columnspan=2, sticky=W+E, pady=5)
 
        Label(parent, text="Gain constant").grid(row=4, column=0, sticky=W+E)
        self.g_cst=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.g_cst).grid(row=4, column=1, stick=W+E)
        Label(parent, text="c").grid(row=5, column=0, sticky=W+E)
        self.gain_c=entry(parent)
        self.gain_c.grid(row=5, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=6, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Gain Exp").grid(row=7, column=0, sticky=W+E)
        self.g_exp=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.g_exp).grid(row=7, column=1, stick=W+E)
        Label(parent, text="a").grid(row=8, column=0, sticky=W+E)
        self.gain_exp_a=entry(parent)
        self.gain_exp_a.grid(row=8, column=1, sticky=W+E)
        Label(parent, text="t0 "+str(affichage.y_unit)).grid(row=9, column=0, sticky=W+E)
        self.gain_exp_t0=entry(parent)
        self.gain_exp_t0.grid(row=9, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=10, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Gain Linéaire").grid(row=11, column=0, sticky=W+E)
        self.g_line=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.g_line).grid(row=11, column=1, stick=W+E)
        Label(parent, text="a").grid(row=12, column=0, sticky=W+E)
        self.gain_line_a=entry(parent)
        self.gain_line_a.grid(row=12, column=1, sticky=W+E)
        Label(parent, text="t0 "+str(affichage.y_unit)).grid(row=13, column=0, sticky=W+E)
        self.gain_line_t0=entry(parent)
        self.gain_line_t0.grid(row=13, column=1, sticky=W+E)

    def fill_tab_filtres(self, parent):
        Label(parent, text="Substract mean").grid(row=0, column=0, sticky=W+E)
        self.sub_mean=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.sub_mean).grid(row=0, column=1, stick=W+E)
        Label(parent, text="Moyenne glissante").grid(row=1, column=0, sticky=W+E)
        self.move_avg=Scale(parent, from_=0, to=self.mesure.radar.getTraces(), orient=HORIZONTAL)
        self.move_avg.grid(row=1, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=2, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Inverser").grid(row=3, column=0, sticky=W+E)
        self.invert=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.invert).grid(row=3, column=1, stick=W+E)

        ttk.Separator(parent).grid(row=4, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Trace reduction").grid(row=5, column=0, sticky=W+E)
        self.trace_reduction=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.trace_reduction).grid(row=5, column=1, stick=W+E)
        Label(parent, text="Traces (%)").grid(row=6, column=0, sticky=W+E)
        self.traces=Scale(parent, from_=0, to=100, orient=HORIZONTAL)
        self.traces.grid(row=6, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=7, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Dewow").grid(row=8, column=0, sticky=W+E)
        self.dewow=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.dewow).grid(row=8, column=1, stick=W+E)

        ttk.Separator(parent).grid(row=9, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Inverser 1/2").grid(row=10, column=0, sticky=W+E)
        batch_inv=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=batch_inv).grid(row=10, column=1, stick=W+E)

        Label(parent, text="Même taille").grid(row=11, column=0, sticky=W+E)
        batch_size=IntVar()
        d=entry(parent)
        d.grid(row=12, columnspan=2, sticky=W+E)
        Checkbutton(parent, onvalue=1, offvalue=0, variable=batch_size).grid(row=11, column=1, stick=W+E)

        batch_button=Button(parent, text="Traitement par lot", command=lambda: self.batch_treatment(batch_size.get(), batch_inv.get(), d.get()))
        batch_button.grid(row=13, columnspan=2, sticky=W+E, pady=5)

    def fill_tab_info(self, parent):
        Label(parent, text="Grille").grid(row=0, column=0, sticky=W+E)
        self.grid=IntVar()
        Checkbutton(parent, onvalue=1, offvalue=0, variable=self.grid).grid(row=0, column=1, stick=W+E)

        ttk.Separator(parent).grid(row=1, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Interpolation").grid(row=2, column=0, sticky=W+E)
        self.interpolation=combobox(parent,["nearest","gaussian","none","bilinear"])
        self.interpolation.grid(row=2, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=3, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Nombre de tick").grid(row=4, column=0, sticky=W+E)
        self.tick=Scale(parent, from_=0, to=50, orient=HORIZONTAL)
        self.tick.grid(row=4, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=5, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Distance = ").grid(row=6, column=0, sticky=W+E)
        Label(parent, text=str(round(self.mesure.radar.getDx()*self.mesure.radar.getTraces(),2))).grid(row=6, column=1, sticky=W+E)

        ttk.Separator(parent).grid(row=7, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="epsilon").grid(row=8, column=0, sticky=W+E)
        self.eps=entry(parent)
        self.eps.grid(row=8, column=1, sticky=W+E)

    def fill_tab_save(self, parent):
        Label(parent, text="Sauvegarde PNG").grid(row=0, columnspan=2, sticky=W+E)
        exp_name=entry(parent)
        exp_name.grid(row=1, columnspan=2, sticky=W+E)
        pngbox=combobox(parent, ["1 seul","Tout"])
        pngbox.current(0)
        pngbox.grid(row=2, columnspan=2, sticky=W+E)
        Button(parent, text="Enregistrer", command=lambda: self.mesure.traitement.save_png(exp_name.get(), pngbox.get(), self.projet, self.mesure)).grid(row=3, columnspan=2, sticky=W+E)

        ttk.Separator(parent).grid(row=4, columnspan=2, sticky=W+E, pady=5)

        Label(parent, text="Sauvegarde parametres").grid(row=5, columnspan=2, sticky=W+E)
        self.param_name=entry(parent)
        self.param_name.grid(row=6, columnspan=2, sticky=W+E)
        Button(parent, text="Enregistrer", command=lambda: self.save_param(self.param_name.get())).grid(row=7, columnspan=2, sticky=W+E)

        ttk.Separator(parent).grid(row=8, columnspan=2, sticky=W+E, pady=5)

        Button(parent, text="Charger parametres", command=lambda: self.load_param()).grid(row=9, columnspan=2, sticky=W+E)


    def save_param(self, label):
        final_directory = os.path.join(os.path.dirname(__file__), label)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        for mes in self.projet.mesure_list:
            name=os.path.join(final_directory,mes.name+".nablapy")
            pickle.dump(vars(mes.param), open(name, "wb"))

    def load_param(self):
        path=filedialog.askdirectory(title="Selectionner un dossier")
        if path:
            self.projet.set_mesure_param(path)
           

    def update(self):
        self.get_freq()
        self.get_start_tc()
        self.get_end_tc()
        self.get_color()
        self.get_interpolation()
        self.get_gain()
        self.get_a_exp()
        self.get_t0_exp()
        self.get_a_line()
        self.get_t0_line()
        self.get_x_unit()
        self.get_y_unit()     
        self.get_c_cst()
        self.get_scope()
        self.get_eps()
        self.get_tick()
        self.get_traces()
        self.get_move_avg()
        self.reset_frame()
        self.set_frame()
        self.init()
        self.plot()

    def get_start_tc(self):
        self.mesure.param.tc_start=self.mesure.traitement.conversion(self.start_tc.get(), affichage.y_unit, "Samples") 
    def get_end_tc(self):
        self.mesure.param.tc_end=self.mesure.traitement.conversion(self.end_tc.get(), affichage.y_unit, "Samples")
    def get_scope(self):
        self.mesure.param.scope=int(self.scope_scale.get())
    def get_move_avg(self):
        self.mesure.param.mean=int(self.move_avg.get())
    def get_tick(self):
        affichage.nbTick=int(self.tick.get())
    def get_traces(self):
        self.mesure.param.reduction=int(self.traces.get())
    def get_color(self):
        affichage.color=self.colorbox.get()
    def get_interpolation(self):
        affichage.interpolation=self.interpolation.get()
    def get_freq(self):
        affichage.freq=self.freq.get()
    def get_x_unit(self):
        affichage.x_unit=self.x_unit.get()
    def get_y_unit(self):
        affichage.y_unit=self.y_unit.get()
    def get_gain(self):
        if self.g_exp.get()==1:
            self.mesure.param.g_exp=True
        else: self.mesure.param.g_exp=False
        if self.g_cst.get()==1:
            self.mesure.param.g_cst=True
        else: self.mesure.param.g_cst=False
        if self.g_line.get()==1:
            self.mesure.param.g_line=True
        else: self.mesure.param.g_line=False
        if self.sub_mean.get()==1:
            self.mesure.param.sub_mean=True
        else: self.mesure.param.sub_mean=False
        if self.invert.get()==1:
            self.mesure.param.invert=True
        else: self.mesure.param.invert=False
        if self.trace_reduction.get()==1:
            self.mesure.param.trace_reduction=True
        else: self.mesure.param.trace_reduction=False
        if self.dewow.get()==1:
            self.mesure.param.dewow=True
        else: self.mesure.param.dewow=False
        if self.grid.get()==1:
            affichage.grid=True
        else: affichage.grid=False
    def get_a_exp(self):
        if self.isfloat(self.gain_exp_a.get()):
            self.mesure.param.a_exp=float(self.replacedecimal(self.gain_exp_a.get()))
        else:
            self.mesure.param.a_exp=1
    def get_t0_exp(self):
        if self.isfloat(self.gain_exp_t0.get()):
            self.mesure.param.b_exp=int(self.mesure.traitement.conversion(float(self.replacedecimal(self.gain_exp_t0.get())), affichage.y_unit, "Samples"))
        else:
            self.mesure.param.b_exp=0
    def get_a_line(self):
        if self.isfloat(self.gain_line_a.get()):
            self.mesure.param.a_line=float(self.replacedecimal(self.gain_line_a.get()))
        else:
            self.mesure.param.a_line=1
    def get_t0_line(self):
        if self.isfloat(self.gain_line_t0.get()):
            self.mesure.param.b_line=int(self.mesure.traitement.conversion(float(self.replacedecimal(self.gain_line_t0.get())), affichage.y_unit, "Samples"))
        else:
            self.mesure.param.b_line=0
    def get_c_cst(self):
        if self.isfloat(self.gain_c.get()):
            self.mesure.param.c_gain=float(self.replacedecimal(self.gain_c.get()))
        else:
            self.mesure.param.c_gain=1
    def get_eps(self):
        if self.isfloat(self.eps.get()):
            self.mesure.param.epsilon=float(self.eps.get())
        else:
            self.mesure.param.epsilon=8

    def isfloat(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def replacedecimal(self, s):
        if "," in s:
            return s.replace(",",".")
        else: return s

    def batch_treatment(self, batch_size, batch_inv, d):
        i=0
        d=self.replacedecimal(d)
        if d=="":
            D=self.mesure.radar.getDx()*self.mesure.radar.getTraces()
        else:
            D=float(d)
        param_batch=vars(self.mesure.param)  
        for mes in self.projet.mesure_list:
            mes.param.update(param_batch)
            if i%2!=0 and batch_inv==1:
                mes.param.invert=True
            i+=1

            if batch_size==1:
                mes.param.dx_edit_val=round(D/(mes.radar.getTraces()-1), 5)
                mes.param.dx_edit=True
            
        self.reset_frame()
        self.set_frame()
        self.init()
        self.plot()
            

class Data:
    def __init__(self, parent):
        self.data_frame_label(parent)

    def data_frame_label(self, parent):
        data_frame=label_frame(parent, "Visualisation")
        data_frame.pack(side=RIGHT, fill="both", expand=1, padx=5, pady=5)
        data_frame.grid_propagate(0)
        data_frame.pack_propagate(0)

        tabControl=ttk.Notebook(data_frame)
        tabRadar=Frame(tabControl)
        self.tabSlice=Frame(tabControl)   
        tabControl.add(tabRadar, text="Radargramme")
        tabControl.add(self.tabSlice, text="Slice")
        tabControl.pack(side="top")
        self.fill_tab_radar(tabRadar)

    def fill_tab_radar(self, parent):
        self.plot_frame=Frame(parent)
        self.plot_frame.pack(side=LEFT, fill=BOTH)

    def init(self):
        self.colorbox.set(self.projet.config.slice_color)
        self.start_scale.set(self.projet.config.start)
        self.end_scale.set(self.projet.config.end)

    def fill_tab_slice(self, parent, projet):
        self.projet=projet
        self.slice_frame=Frame(parent)
        self.slice_frame.pack(side=LEFT, fill=BOTH)
        self.slice_menu=Frame(parent)
        self.slice_menu.pack(side=RIGHT, fill = BOTH)

        Label(self.slice_menu, text="Couleur").grid(row=0, column=0, sticky=W+E)
        self.colorbox=combobox(self.slice_menu, ["seismic","Greys","jet","rainbow","tab20c"])
        self.colorbox.grid(row=0, column=1, sticky=W+E)

        ttk.Separator(self.slice_menu).grid(row=1, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="PNG").grid(row=4, columnspan=2)
        name=entry(self.slice_menu)
        name.grid(row=4, column=0, sticky=W+E)
        save=Button(self.slice_menu, text="sauvegarder", command=lambda: Slicing(self.projet.mesure_list, self.projet.config).save(Slice(self.projet.mesure_list, self.projet.config).apply(),name.get()))
        save.grid(row=4, column=1, sticky=W+E)

        ttk.Separator(self.slice_menu).grid(row=5, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Tranche moyenne").grid(row=6, column=0, sticky=W+E)
        self.start_scale=self.scroll_bar(self.slice_menu, "Début (ns) ", self.projet.config.start, 7)
        self.end_scale=self.scroll_bar(self.slice_menu, "Fin (ns) ", self.projet.config.end, 8)

        ttk.Separator(self.slice_menu).grid(row=9, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Inter-ligne (cm)").grid(row=10, column=0, sticky=W+E)
        self.interline=entry(self.slice_menu)
        self.interline.grid(row=10, column=1, sticky=W+E)
        self.interline.insert(END, str(self.projet.config.interline))

        ttk.Separator(self.slice_menu).grid(row=11, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Max Auto").grid(row=12, column=0, sticky=W+E)
        self.max_auto=IntVar()
        Checkbutton(self.slice_menu, onvalue=1, offvalue=0, variable=self.max_auto).grid(row=12, column=1, stick=W+E)

        ttk.Separator(self.slice_menu).grid(row=13, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Grille").grid(row=14, column=0, sticky=W+E)
        self.grid=IntVar()
        Checkbutton(self.slice_menu, onvalue=1, offvalue=0, variable=self.grid).grid(row=14, column=1, stick=W+E)

        ttk.Separator(self.slice_menu).grid(row=15, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Inverser 1/2").grid(row=16, column=0, sticky=W+E)
        self.slice_inv=IntVar()
        Checkbutton(self.slice_menu, onvalue=1, offvalue=0, variable=self.slice_inv).grid(row=16, column=1, stick=W+E)

        ttk.Separator(self.slice_menu).grid(row=17, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Découpage").grid(row=18, column=0, sticky=W+E)
        self.slice_cut=IntVar()
        Checkbutton(self.slice_menu ,onvalue=1, offvalue=0, variable=self.slice_cut).grid(row=18, column=1, sticky=W+E)
        Label(self.slice_menu, text="Début (m)").grid(row=19, column=0)
        self.slice_cut_start=entry(self.slice_menu)
        self.slice_cut_start.insert(END, str(self.projet.config.slice_cut_start))
        self.slice_cut_start.grid(row=19, column=1)
        Label(self.slice_menu, text="Fin (m)").grid(row=20, column=0)
        self.slice_cut_end=entry(self.slice_menu)
        self.slice_cut_end.insert(END, str(self.projet.config.slice_cut_end))
        self.slice_cut_end.grid(row=20, column=1)

        ttk.Separator(self.slice_menu).grid(row=21, columnspan=2, sticky=W+E, pady=5)

        Label(self.slice_menu, text="Flip gauche/droite").grid(row=22, column=0, sticky=W+E)
        self.flip=IntVar()
        Checkbutton(self.slice_menu ,onvalue=1, offvalue=0, variable=self.flip).grid(row=22, column=1, sticky=W+E)

        ttk.Separator(self.slice_menu).grid(row=21, columnspan=2, sticky=W+E, pady=5)

        apply=Button(self.slice_menu, text="Tracer", command=lambda: [self.apply() ,Slice(self.projet.mesure_list, self.projet.config).apply()])
        apply.grid(row=25, columnspan=2, sticky=W+E)
        self.init()

    def scroll_bar(self, parent, lab, parame, r):
        start=1
        end=150
        Label(parent, text=str(lab)+"("+str(round(self.projet.mesure_list[0].traitement.conversion(parame, "Temps (ns)", "Distance (m)"), 2))+"m)").grid(row=r, column=0, sticky=W+E)
        self.scope_scale=Scale(parent, from_=start, to=end, orient=HORIZONTAL)
        self.scope_scale.grid(row=r, column=1, sticky=W+E)
        self.scope_scale.set(parame)
        return self.scope_scale


    def apply(self):
        self.get_cmap()
        self.get_cut()
        self.get_interline()
        self.get_max_auto()
        self.get_grid()
        self.get_inv()
        self.get_slice_cut()
        self.get_slice_cut_start()
        self.get_slice_cut_end()
        self.start_scale.destroy()
        self.end_scale.destroy()
        self.start_scale=self.scroll_bar(self.slice_menu, "Début (ns) ", self.projet.config.start, 7)
        self.end_scale=self.scroll_bar(self.slice_menu, "Fin (ns) ", self.projet.config.end, 8)


    def get_cut(self):
        self.projet.config.start=int(self.start_scale.get())
        self.projet.config.end=int(self.end_scale.get())
        
    def get_cmap(self):
        self.projet.config.slice_color=self.colorbox.get()

    def get_interline(self):
        if Tframe.isfloat(self.interline.get()):
            self.projet.config.interline=float(Tframe.replacedecimal(self.interline.get()))
        else: self.projet.config.interline=50
    
    def get_max_auto(self):
        if self.max_auto.get()==1:
            self.projet.config.max_auto=True
        else: self.projet.config.max_auto=False

    def get_grid(self):
        if self.grid.get()==1:
            self.projet.config.grid=True
        else: self.projet.config.grid=False

    def get_inv(self):
        if self.slice_inv.get()==1:
            self.projet.config.inv=True
        else: self.projet.config.inv=False

    def get_slice_cut(self):
        if self.slice_cut.get()==1:
            self.projet.config.slice_cut=True
        else: self.projet.config.slice_cut=False
        if self.flip.get()==1:
            self.projet.config.flip=True
        else: self.projet.config.flip=False

    def get_slice_cut_start(self):
        if Tframe.isfloat(self.slice_cut_start.get()):
            self.projet.config.slice_cut_start=float(Tframe.replacedecimal(self.slice_cut_start.get()))
        else: self.projet.config.slice_cut_start=0

    def get_slice_cut_end(self):
        if Tframe.isfloat(self.slice_cut_end.get()):
            self.projet.config.slice_cut_end=float(Tframe.replacedecimal(self.slice_cut_end.get()))
        else: self.projet.config.slice_cut_end=0
    



main=Tk()
main.geometry('1500x900')
main.title('NablaPy')
affichage=Affichage()
Tframe=Tool(main)
Dframe=Data(main)

main.mainloop()