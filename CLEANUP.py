



#### oh boy oh boy


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
import datetime

today = datetime.date.today()
currentdate = today.strftime("%m/%d/%y").replace("/","-") ### change from / to hyphen for file name purposes
starttime = str(datetime.datetime.now().time())[:8].replace(":","-") ### truncate to seconds
print(f"\nThe date is: {currentdate}")
print(f"This program was started at: {starttime} \n")

LARGE_FONT = ("Verdana", 12)
TClocations = ['Reservoir','Reservoir Output','Elbow','LFV','VCR Swage','Dump Input' ############# MUST MATCH LENGTH OF PINS VARIABLE
      ,'1','2','3','4','5','6','7','8'#,'9','10','11','12','13','14','15','16','17','18','19','20'
      ]
numberOfRows = len(TClocations)

# print("Current Working Directory " , os.getcwd()) 
############################## INPUT WHERE YOU WANT DATA FILES TO BE SAVED #################################################
# os.chdir("\andrew\CPMI\TCsaves")
savefile = open(f"time-{starttime}-date-{currentdate}","w")
savefile.write(f"The date is: {currentdate}\n")
savefile.write(f"This program was started at: {starttime} \n timestamp ") ### timepadding

for location in TClocations:
    padding = int(15 - len(location)/2)
    paddedstring = " " *padding + location + " " *padding
    savefile.write(paddedstring) ### centered text with 10 padding, same format to be used with the actual data
savefile.close()

serial=360018184
serial2=360015878
# pins= [13,12,11,10,9,8]  # This is the AIN 0-13 that is read
pins = [0,1,2,3,4,5,6,7,8,9,10,11,12,13] ############################################ MUST MATCH LENGTH OF TClocations VARIABLE

dacpins = [1,1,0,0] ### labjack output for chip to run
PWMpins = [13,12,11,8]
timerpins = [0,1,2,3] ### labjack output of frequency for duty cycle
dutycycles = [36,50,9,6]
maxpwm = [2*i/120*100 for i in dutycycles]


num_timers=len(timerpins)
color = ['red','blue','green','magenta','purple','brown','black','orange','pink','gray'
         ,'red','red','red','red','red','red','red','red','red','red','red','red','red','red','red','red','red','red','red','red'
         ] ### add more

maxlen = 1E3 # Time in seconds that the graph runs for

times = np.linspace(0, maxlen, int(maxlen + 1))
timestep = 0 # running variable represending time, use to index data array. Should not exceed window_width
window_width = 10  # width of the scrolling window in sec

data=np.empty((len(pins),window_width)) ### empty array in which we store all data
data = np.transpose(data) ### makes rows timestep and columns pins
data[:] = np.NaN # make array of len(pins) x 180 all NaNs for graphing purposes

data2=[] # ??
linewidth = 2.    # thickness of the graph line


fig = plt.figure()
a=fig.add_subplot(111) ### for later use in a.plot() in plot_data
idx=np.zeros(len(PWMpins))

for ii,i in enumerate(PWMpins):
    idx[ii]=pins.index(i)



##### PID PARAMETERS #####
kp  = 20
ki  = .5
kd  = 0

pid=[PID.PID(kp,ki,kd),PID.PID(kp,ki,kd),PID.PID(kp,ki,kd),PID.PID(kp,ki,kd)]
for i in pid:
    i.setSampleTime(.5)
################ TEMPERATURE STORING and PLOTTING ########################

storetime = 1

def StoreData(data,temp1,timestep,storevar,storetime): ### this function stores temp1 into both "data" and a chosen save file

    ### store into "data" variable    

    global inc
    if timestep >= window_width: ### timestep is index, window width is length. When timestep = window length, it's already exceeded data array.
        data = np.delete(data,0,0) ### delete initial row of data array, making data 179 long, and timestep = 179 index won't work. must append:
        data = np.vstack((data,temp1)) ### append. Hopefully just adds row.
        inc += 1 ### keeps counting for when graph is turned off
    else: ### if timestep has not reached 180, we can use data[timestep] to fill in data.
        data[timestep] = temp1
        timestep += 1
    
    ### store into file
    
    savefile = open(f"time-{starttime}-date-{currentdate}","a") ### create folder per run, folder contains multiple files.
    
    
    ######################################### careful of boundaries
    
    
    
    
    
    
    
    filesize = savefile.tell()
    print(filesize)
    
    if storetime == -1: ### storetime = -1 is our stopping condition for the file storage portion. This makes it so 
    ### that this part will stop running if we exceed file size, decreasing runtime
        1==1
        print("stopped")
    
    else: ### if file size not exceeded, run!
    
        if filesize < 1E8: ######## limit file size
            timepadding = int(6 - len(str(storetime))/2) ### 6 ... pixels? this was manually set to match length of string "timestamp"
            timestamp = " "*timepadding + str(storetime) + " "*timepadding
            savefile.write("\n"+timestamp) ### start a new line for each point in time and write in padded time
            for index,temperature in enumerate(temp1):
                
                if storevar[index].get(): ### if we want to store
                    temperature = "%.2f"%temperature ### format to 2 decimal places
                    padding = int(15 - len(temperature)/2)
                    paddedstring = " "*padding + temperature + " "*padding
                    savefile.write(paddedstring)
                    
                else:
                    savefile.write(" "*30)
                    
            savefile.close()
            storetime += 1 ### for timestamp
        else: ### run once when file size is exceeded. 
            enddate = today.strftime("%m/%d/%y").replace("/","-") ### change from / to hyphen for file name purposes
            endtime = str(datetime.datetime.now().time())[:8] ### truncate to seconds
            savefile.write(f"\n\nThis file closed at {endtime} on {enddate}")
            savefile.close()
            storetime = -1
            
    return data,timestep,storetime

##################################################################################### STORE NANS WHEN PLOT TURNED OFF INSTEAD OF STOPPING THE PLOT.
##################################################################################### WE WANT STUFF TO STAY THERE BUT JUST NOT PLOT ANYMORE.

##################################################################################### ADD CHECKBOX FOR WHETHER OR NOT WE WANT TO STORE DATA (PREVIOUS NOT DELETED)
##################################################################################### DATA WILL BE LIVE WRITTEN INTO A FILE (probably)
##################################################################################### LIMIT FILE SIZE
##################################################################################### FILE NAME CORRESPONDS TO TIME AND DATE (find module with that)

global inc
inc=window_width # sets inc into 60

def plot_data(data,timer,plotvar,color,name,timestep):
    global inc ### inc starts at window_width, represents time past window_width
    data_length=timestep ### returns number of rows, should be equal to window_width (columns of data are pins indices)
    if data_length > window_width-1: ### if window_width > window_width-1, so only this branch runs!!!
        if plotvar.get(): ### idk
            if (inc-timer)<window_width:
                # times[timer:inc] hashes from timer to inc, but
                a.plot(times[timer:inc], data[-(inc-timer):], linewidth = linewidth,color='%s'%color,label='%s'%TClocations) ### plt.plot

            else:
                a.plot(times[inc-window_width:inc], data[-window_width:], linewidth = linewidth,color='%s'%color,label='%s'%TClocations,)

        else:
            timer=inc ### timer = 60 + time past 60
    else: 
        if plotvar.get():
            a.plot(times[timer:data_length],data[timer:data_length], linewidth = linewidth,color='%s'%color,label='%s'%name)

        else:
            timer=data_length
    if data_length > window_width:
        plt.xlim(inc-window_width-1,inc-2)
    return timer

# def plot_data(data,timer,plotvar,color,name,timestep):
#     global inc ### inc starts at window_width, represents time past window_width
#     data_length=timestep ### returns number of rows, should be equal to window_width (columns of data are pins indices)
    
#     if data_length > window_width-1: ### if window_width > window_width-1, so only this branch runs!!!
    
#     ### plot_data is called every second for each pin (run in a loop, in j,jj enumerate(pins)). 
#     ### inc starts at window_width (60), represents time past window_width.
#     ### times is linspace [0,1,2,...,maxlen] (keep small for testing, might try another method)
#     ### don't worry about color and name
#     ### plotvar is array that stores plot or not 
#     ### timestep is running variable, increases by 1 every time store_data is called, until 180 (basically pre-inc)
#     ### timer is just an array of ones, which gets called per index. it starts as 1
    
#         if plotvar.get(): ### IF WE TELL IT TO PLOT
        
#             if (inc-timer)<window_width: ### within graph
#             ### x from 
#                 a.plot(times[timer:inc], data[-(inc-timer):], linewidth = linewidth,color='%s'%color,label='%s'%name) ### plt.plot

#             else: ### exceeds graph, so we plot 
#                 a.plot(times[inc-window_width:inc], data[-window_width:], linewidth = linewidth,color='%s'%color,label='%s'%name,)

#         else: ### IF PLOT CHECKMARK NOT SELECTED, DO THE SAME THING EXCEPT PLOT NANS
#         ### to do this, we need to still keep plotting all the other data. 
#         ### So we make a new array of just that data 
        
#             # if (inc-timer)<window_width:
#             #     a.plot(times[timer:inc], data[-(inc-timer):], linewidth = linewidth,color='%s'%color,label='%s'%name) ### plt.plot

#             # else:
#             #     a.plot(times[inc-window_width:inc], data[-window_width:], linewidth = linewidth,color='%s'%color,label='%s'%name,)
#             1==1
#         timer=inc ### timer = 180 + time past 180
            
#     if data_length > window_width:
#         plt.xlim(inc-window_width-1,inc-2)
#     return timer


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

''' DCcorrect
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

        ### BACKGROUND FOR ALL OPTIONS, COL 1
        BackFrame=tk.Frame(self,height=400)
        #Frame2.config(height=100)
        BackFrame.grid(row=0,column=1)
        
        TitleFrame = tk.Frame(BackFrame)
        TitleFrame.grid(row=0)
        
        titles = ["TC Locations","Temperature oC","Setpoint","Plot Y/N","Store Data Y/N"]
        columns = len(titles)
        labels1 = [tk.Label() for j in range(0,columns)]
        for j in range(0,columns):
            labels1[j] = tk.Label(TitleFrame, relief="solid", font=LARGE_FONT,text = str(titles[j]))
            labels1[j].grid(row=0,column=j,pady=10,padx=10,sticky="news")
        
        ### Frames can scroll, canvases can't. To have a frame, you need to put it on a canvas. 
        ### You can't put a canvas without a frame. First frame has root as master. 
        ScrollFrame = tk.Frame(BackFrame)
        ScrollFrame.grid(row=1,column=0,sticky="news")
        ScrollFrame.grid_rowconfigure(0,weight=1)
        ScrollFrame.grid_columnconfigure(0,weight=1)
        ScrollFrame.grid_propagate(False)
        
        ScrollCanvas = tk.Canvas(ScrollFrame)
        ScrollCanvas.grid(row=0,column=0,sticky="news")
        
        scrollbary = tk.Scrollbar(ScrollFrame, orient="vertical", command=ScrollCanvas.yview)
        scrollbary.grid(row=0,column=1,sticky="ns")
        ScrollCanvas.configure(yscrollcommand=scrollbary.set)
        
        OptionsFrame = tk.Frame(ScrollCanvas)
        ScrollCanvas.create_window((0,0),window = OptionsFrame, anchor = "center")
        

        ###### generalized ###########
        
        tclocations = [tk.Label() for i in range(0,numberOfRows)]
        self.currenttemp = [tk.Label() for i in range(0,numberOfRows)]
        self.setpoints = [tk.Entry() for i in range(0,numberOfRows)]
        
        self.plotvar = [tk.IntVar(self) for i in range(0,numberOfRows)]
        plotornot = [tk.Checkbutton() for i in range(0,numberOfRows)]
        self.storevar = [tk.IntVar(self) for i in range(0,numberOfRows)]
        storeornot = [tk.Checkbutton() for i in range(0,numberOfRows)]
        
        for i in range(0,numberOfRows): ### must have sufficient length of: name, color, plotvar (which depends on pins)
        
            ##### THERMOCOUPLE LOCATIONS ###########
            tclocations[i] = tk.Label(OptionsFrame, relief="solid", font=LARGE_FONT, text='%s'%TClocations[i],fg='%s'%color[i])
            tclocations[i].grid(row=i,pady=10,padx=10)
            ###### ACTUAL TEMPERATURE ############
            self.currenttemp[i] = tk.Label(OptionsFrame, relief="solid", font=LARGE_FONT, text="start")
            self.currenttemp[i].grid(row=i,column=1,pady=10,padx=10)
            ####### SET POINTS #################
            self.setpoints[i] = tk.Entry(OptionsFrame)
            self.setpoints[i].grid(row=i,column=2,pady=10,padx=10)
            ########## PLOTTING Y/N CHECK ##################
            plotornot[i] = tk.Checkbutton(OptionsFrame,text='', variable = self.plotvar[i])
            plotornot[i].grid(row=i,column=3,pady=10,padx=40)
            ####### STORE DATA Y/N CHECK ###################
            storeornot[i] = tk.Checkbutton(OptionsFrame,text='', variable = self.storevar[i])
            storeornot[i].grid(row=i,column=4,pady=10,padx=40)
            
        OptionsFrame.update_idletasks()
        
        width = 400
        height = 400
        ScrollFrame.config(width=width + scrollbary.winfo_width(),height=height)
        
        ScrollCanvas.config(scrollregion = ScrollCanvas.bbox('all'))

    def f(self,TC1):
        for i in range(0,numberOfRows):
            self.currenttemp[i].configure(text='%.2f'%(TC1[i]))
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
        data,timestep,storetime = StoreData(data,temp1,timestep,gui.storevar,storetime) #store data. TIMESTEP IS RUNNING VARIABLE FOR TIME
        a.clear()  #clear plot on gui
    
        for j,jj in enumerate(pins): #since pins values are its indices
            # print(jj,gui.plotvar[j].get())
            t[j] = plot_data(data[:,j],t[j],gui.plotvar[j],color[j],TClocations[j],timestep) ### updates t (timer)
    
        ##### END OF LOOP ########
    
        plt.grid(b=True, axis='y')
        plt.title('Temperature')
        plt.xlabel('Time (sec)')
        plt.ylabel('Temperature ($^o$C)')
        fig.canvas.draw()
    
        # create new list with the gui.en.gets()s, which we can loop over to read setpoint, which we then get to labjack output via pid.update
        # for loop for each pins
        
        updatedsetpoints = np.zeros(numberOfRows)
        for k in range(0,numberOfRows):
            try:
                updatedsetpoints[k] = int(gui.setpoints[k].get())
            except:
                pass

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
    while True:
        temp1 = np.random.randint(0,high=10,size=len(pins))
        #### LOOP FOR EACH INPUT 0-13
        data,timestep,storetime = StoreData(data,temp1,timestep,gui.storevar,storetime) #store data
        a.clear()  #clear plot on gui
    
        for j,jj in enumerate(pins): #since pins values are its indices
            # print(jj,gui.plotvar[j].get())
            t[j] = plot_data(data[:,j],t[j],gui.plotvar[j],color[j],TClocations[j],timestep) ### original t[j] is "timer" in plot_data function
    
        ##### END OF LOOP ########
    
        plt.grid(b=True, axis='y')
        plt.title('Temperature')
        plt.xlabel('Time (sec)')
        plt.ylabel('Temperature ($^o$C)')
        fig.canvas.draw()
    
        # create new list with the gui.en.gets()s, which we can loop over to read setpoint, which we then get to labjack output via pid.update
        # for loop for each pins
        
        updatedsetpoints = np.zeros(numberOfRows)
        for k in range(0,numberOfRows):
            try:
                updatedsetpoints[k] = int(gui.setpoints[k].get())
            except:
                pass
            
        gui.after(1000,gui.f(temp1))
    

gui.mainloop()
sys.exit()







