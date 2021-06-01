





import math
import tkinter as tk
import sys
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import u6
import time
from labjackTC import *
import os
import PID

LARGE_FONT= ("Verdana", 12)


#color=['red','blue']
name=['Reservoir','Reservoir Output','Elbow','LFV','VCR Swage','Dump Input']
serial=360018184
serial2=360015878
pins= [13,12,11,10,9,8]  # This is the AIN 0-13 that is read

dacpins = [1,1,0,0] ### labjack output for chip to run
PWMpins=[13,12,11,8]
timerpins = [0,1,2,3] ### labjack output of frequency for duty cycle
R=[36,50,9,6]
maxpwm=[2*i/120*100 for i in R]


num_timers=len(timerpins)
color = ['red','blue','green','magenta','purple','brown','black','orange','pink','gray'] ### add more

maxlen = 1E7 # Time in seconds that the graph runs for

times = np.linspace(0, maxlen, int(maxlen + 1))
timestep = 0 # running variable represending time, use to index data array. Should not exceed 179 (179th index is 180tb value)
window_width = 60  # width of the scrolling window in sec

data=np.empty((len(pins),window_width)) ### empty array in which we store all data
data = np.transpose(data) ### makes rows timestep and columns pins
data[:] = np.NaN # make array of len(pins) x 180 all NaNs for graphing purposes

data2=[] # ??
linewidth = 2.    # thickness of the graph line


fig = plt.figure()
a=fig.add_subplot(111)
idx=np.zeros(len(PWMpins))

for ii,i in enumerate(PWMpins):
    idx[ii]=pins.index(i)




zz=0

global inc
inc=window_width # sets inc into 180

##### PID PARAMETERS #####
kp  = 20
ki  = .5
kd  = 0

pid=[PID.PID(kp,ki,kd),PID.PID(kp,ki,kd),PID.PID(kp,ki,kd),PID.PID(kp,ki,kd)]
for i in pid:
    i.setSampleTime(.5)
################ TEMPERATURE STORING and PLOTTING ########################
def StoreData(data,temp1,timestep):
    global inc
    if timestep >= window_width: ### timestep is index, window width is length. When timestep = window length, it's already exceeded data array.
        data = np.delete(data,0,0) ### delete initial row of data array, making data 179 long, and timestep = 179 index won't work. must append:
        data = np.vstack((data,temp1)) ### append. Hopefully just adds row.
        inc += 1 ### keeps counting for when graph is turned off
    else: ### if timestep has not reached 180, we can use data[timestep] to fill in data.
        data[timestep] = temp1
        timestep += 1

    return data,timestep


def plot_data(data,timer,var,color,name,timestep):
    global inc ### inc starts at window_width, represents time past window_width
    data_length=timestep ### returns number of rows, should be equal to window_width (columns of data are pins indices)
    if data_length > window_width-1: ### if window_width > window_width-1, so only this branch runs!!!
        if var.get(): ### idk
            if (inc-timer)<window_width:
                # times[timer:inc] hashes from timer to inc, but
                a.plot(times[timer:inc], data[-(inc-timer):], linewidth = linewidth,color='%s'%color,label='%s'%name) ### plt.plot

            else:
                a.plot(times[inc-window_width:inc], data[-window_width:], linewidth = linewidth,color='%s'%color,label='%s'%name,)

        else:
            timer=inc ### timer = 180 + time past 180
    else: ### never runs.
        if var.get():
            a.plot(times[timer:data_length],data[timer:data_length], linewidth = linewidth,color='%s'%color,label='%s'%name)

        else:
            timer=data_length
    if data_length > window_width:
        plt.xlim(inc-window_width-1,inc-2)
    return timer

## these are just if check mark is selected or not... but how does IntVar distinguish between buttons?
var = list(np.zeros(len(pins)))
for i in range(0,len(pins)):
    var[i] = tk.IntVar()

def set(var):
    if var.get()==0:
        var.set(1)
    else:
        var.set(0)


############## PWM CONTROL #######################
def LabjackSetup(serial,num_timers):
    U6=u6.U6(autoOpen=False)
    U6.open(firstFound=False,serial=serial)
    U6.configIO(NumberTimersEnabled=num_timers)
    #self.LJ.configTimerClock(TimerClockBase=3, TimerClockDivisor=2)
    U6.configTimerClock(TimerClockBase=3, TimerClockDivisor=1)
    U6.getCalibrationData() ###
    return U6

def PWM(LJ,dutycycle,dacnumber,pinnumber):
    DAC0_VALUE = LJ.voltageToDACBits(5.0, dacNumber = dacnumber, is16Bits=False) ### pin on labjack that outputs 5 or 0 volts (high/low),
    LJ.getFeedback(u6.DAC8(dacnumber,DAC0_VALUE)) ### getfeedback tells labjack to output something from labjack pins (physical output)
    base=int(65336-(float(dutycycle)*65335/100)) ### converts dutycycle to something labjack can read

    ### 0,1,2,3 timers on labjack
    LJ.getFeedback(u6.TimerConfig(pinnumber,1,Value=base)) ### run timer 0 in mode 1 (8 bit PWM), value being set as duty cycle in labjackanese

def stopPWM(LJ,dacnumber):
    DAC0_VALUE = LJ.voltageToDACBits(0.0, dacNumber = dacnumber, is16Bits=False) ### set voltage to 0 for chip
    LJ.getFeedback(u6.DAC8(dacnumber,DAC0_VALUE))

try:
    U6=LabjackSetup(serial,num_timers)
except:
    print("devMode")
#U6Pro=LabjackSetup(serial2,1)

'''
def DCcorrect(setpoint,T1,DC):
    if DC<=50:
        #print(T1,setpoint)
        #print('%f'%(abs(T1-setpoint)/setpoint))
        if abs(T1-setpoint)/setpoint>.05:
            print(DC)
            print((T1-setpoint)/setpoint*DC)
            DC-=(T1-setpoint)/setpoint*DC
            print(DC)
    else:
        DC=50
    return DC
'''


#### GUI OBJECT  ####

class GUI(tk.Tk):
    def __init__(self,U6):
        tk.Tk.__init__(self)
        self.title('temp1 Readout')
        Frame1=tk.Frame(self,height=5000)
        Frame1.grid()
        Frame1.config(height=5000)
        canvas1 = FigureCanvasTkAgg(fig, Frame1)
        canvas1.draw()
        canvas1.get_tk_widget().grid()

        Frame2=tk.Frame(self,height=400)
        #Frame2.config(height=100)
        Frame2.grid(row=0,column=1)


        ###### THERMOCOUPLE LOCATIONS - FRAME 5 ############
        label11=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='TC Locations')
        label11.grid(row=0,pady=10,padx=10)
        label12=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[0],fg='%s'%color[0])
        label12.grid(row=1,pady=10,padx=10)
        label13=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[1],fg='%s'%color[1])
        label13.grid(row=2,pady=10,padx=10)
        label14=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[2],fg='%s'%color[2])
        label14.grid(row=3,pady=10,padx=10)
        label15=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[3],fg='%s'%color[3])
        label15.grid(row=4,pady=10,padx=10)
        label16=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[4],fg='%s'%color[4])
        label16.grid(row=5,pady=10,padx=10)
        label17=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='%s'%name[5],fg='%s'%color[5])
        label17.grid(row=6,pady=10,padx=10)

        ########## ACTUAL TEMPERATURE ###############
        self.label21=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='Temperature oC')
        self.label21.grid(row=0,column=1,pady=10,padx=10)
        self.label22=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label22.grid(row=1,column=1,pady=10,padx=10)
        self.label23=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label23.grid(row=2,column=1,pady=10,padx=10)
        self.label24=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label24.grid(row=3,column=1,pady=10,padx=10)
        self.label25=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label25.grid(row=4,column=1,pady=10,padx=10)
        self.label26=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label26.grid(row=5,column=1,pady=10,padx=10)
        self.label27=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='start')
        self.label27.grid(row=6,column=1,pady=10,padx=10)


        ######## SET_POINTS #######
        label41=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='Setpoint')
        label41.grid(row=0,column=2,pady=10,padx=10)
        self.e1=tk.Entry(Frame2)
        self.e1.grid(row=1,column=2,pady=10,padx=10)
        self.e2=tk.Entry(Frame2)
        self.e2.grid(row=2,column=2,pady=10,padx=10)
        self.e3=tk.Entry(Frame2)
        self.e3.grid(row=3,column=2,pady=10,padx=10)
        self.e4=tk.Entry(Frame2)
        self.e4.grid(row=6,column=2,pady=10,padx=10)

        ####### PLOTTTING Y/N #################
        label31=tk.Label(Frame2,relief='solid',font=LARGE_FONT,text='Plot Y/N')
        label31.grid(row=0,column=3,pady=10,padx=10)
        c1=tk.Checkbutton(Frame2,text='',command= lambda : set(var[0]) )
        c1.grid(row=1,column=3,pady=10,padx=10)
        c2=tk.Checkbutton(Frame2,text='',command= lambda : set(var[1]) )
        c2.grid(row=2,column=3,pady=10,padx=10)
        c3=tk.Checkbutton(Frame2,text='',command= lambda : set(var[2]) )
        c3.grid(row=3,column=3,pady=10,padx=10)
        c4=tk.Checkbutton(Frame2,text='',command= lambda : set(var[3]) )
        c4.grid(row=4,column=3,pady=10,padx=10)
        c5=tk.Checkbutton(Frame2,text='',command= lambda : set(var[4]) )
        c5.grid(row=5,column=3,pady=10,padx=10)
        c6=tk.Checkbutton(Frame2,text='',command= lambda : set(var[5]) )
        c6.grid(row=6,column=3,pady=10,padx=10)


    def f(self,TC1):
        self.label22.configure(text='%.2f'%(TC1[0]))
        self.label23.configure(text='%.2f'%(TC1[1]))
        self.label24.configure(text='%.2f'%(TC1[2]))
        self.label25.configure(text='%.2f'%(TC1[3]))
        self.label26.configure(text='%.2f'%(TC1[4]))
        self.label27.configure(text='%.2f'%(TC1[5]))
        self.update()

### we also need the pins corresponding to these timer/dac pins...
### so like maybe AIN pin 4 gives us TC data to convert to an output for timer 2

try:
    gui=GUI(U6)
except:
    gui=GUI(1)
t1=0
t2=0
dutycycle=25


t= np.ones(len(pins),dtype=int)### is this just a random array of size len(pins)
try:
    while True:
        ### temp1 is list of 13
        temp1=TCvalue(U6,pins)
    
        #### LOOP FOR EACH INPUT 0-13
        data,timestep=StoreData(data,temp1,timestep) #store data
        a.clear()  #clear plot on gui
    
        for i,ii in enumerate(pins): #since pins values are its indices
            t[i]=plot_data(data[:,i],t[i],var[i],color[i],name[i],timestep)
    
        ##### END OF LOOP ########
    
        plt.grid(b=True, axis='y')
        plt.title('Temperature')
        plt.xlabel('Time (sec)')
        plt.ylabel('Temperature ($^o$C)')
        fig.canvas.draw()
    
        # create new list with the gui.en.gets()s, which we can loop over to read setpoint, which we then get to labjack output via pid.update
        # for loop for each pins
        setpoint = [gui.e1.get(),gui.e2.get(),gui.e3.get(),gui.e4.get()] ### in loop to constantly check input from GUI
    
        for index,value in enumerate(PWMpins):
            index1=int(idx[index])
    
            if setpoint[index]=='': ### if there is no input in the GUI
                stopPWM(U6,dacpins[index])
            else:
                 ### convert to float
                pid[index].SetPoint=float(setpoint[index]) ### desired temp fed into PWM
                pid[index].update(temp1[index1]) ### update with current reading from AIN pin corresponding to timerpin[index]
                targetpwm=pid[index].output ### pid.output tells us duty cycle we want to run at
                targetpwm=max(min(int(targetpwm),maxpwm[index]),10) ### won't work at <10% duty cycle, 50 is upper bound to prevent overdraw of current
                PWM(U6,targetpwm,dacpins[index],timerpins[index]) ### given input from AIN pin i, output to DAC pin j
                print(targetpwm)
    
        gui.after(1000,gui.f(temp1))
except:
    1==1



gui.mainloop()
sys.exit()