import tkinter
import os
import time

VERSION = "V1.00"

###############################################  READ ME  ###########################################################
# This script is intended to view and control the DO and DI pins on MIC series boards.
# The script is separated into three main parts in order of appearance.
# 1) Defining the class whose sole purpose is to interact and store valuable information pertaining to the MIC device
# 2) Determines what MIC model the device is automatically
# 3) Making the GUI
# Rarely, the terminal will say "I/O Error" multiple times. Ignore it. Nothing is wrong and the program works perfect.
#####################################################################################################################


#Defining the GPIO lines for each MIC model
MIC_710AI_INPUT = [200,38,62,194]
MIC_710AI_OUTPUT = [63,149,66,168]

MIC_730AI_INPUT = [232,233,234,235,236,237,238,239]
MIC_730AI_OUTPUT = [224,225,226,227,228,229,230,231]

MIC_710AIX_INPUT = [422,393,419,268]
MIC_710AIX_OUTPUT = [266,421,264,424]
#710IVA shares the same gpio lines as 710AIX

MIC_730IVA_INPUT = [240,241,242,243]
MIC_730IVA_OUTPUT = [232,233,234,235]

# All interactions to the GPIO are defined in this class: MIC
class MIC:
    # Refreshes Input and Output state lists (lists = python arrays)
    def refresh(self):
        for i in range(len(self.Output_pins)): # Loop for the total amount of output pins
            # Ask computer what the state of the GPIO pin is, save computer's answer/output as string
            temp=os.popen("cat /sys/class/gpio/gpio"+str(self.Output_pins[i])+"/value")
            t=temp.read()
            self.Output_state[i] = (int(t)+1)%2 # Compensation for the inverse logic inherent in the output pins
        for i in range(len(self.Input_pins)): # Same as above, but now for input pins
            temp = os.popen("cat /sys/class/gpio/gpio"+str(self.Input_pins[i])+"/value")
            self.Input_state[i] = temp.read()
        return

    # Changes the state of a GPIO line defined by the parameter 'pin'
    def change(self,pin):
        os.system("echo "+str(self.Output_state[pin])+" > /sys/class/gpio/gpio"+str(self.Output_pins[pin])+"/value")
        return

    # Enables GPIO pins to be changeable, defines GPIO pins as inputs or outputs, and records the current state of pins
    def export(self):
        for i in range(len(self.Output_pins)): # Loop for each output pin
            os.system("echo "+str(self.Output_pins[i])+" > /sys/class/gpio/export") # Sets GPIO pin to read/write
            os.system("echo out > /sys/class/gpio/gpio"+str(self.Output_pins[i])+"/direction") # Sets GPIO pin as output
            temp=os.popen("cat /sys/class/gpio/gpio"+str(self.Output_pins[i])+"/value") # Reads state of GPIO pin
            self.Output_state.append((int(temp.read())+1)%2) # Saves state of GPIO pin to member list
        for i in range(len(self.Input_pins)): # Same as above, but with input pins
            os.system("echo "+str(self.Input_pins[i])+" > /sys/class/gpio/export")
            os.system("echo in > /sys/class/gpio/gpio"+str(self.Input_pins[i])+"/direction")
            temp = os.popen("cat /sys/class/gpio/gpio"+str(self.Input_pins[i])+"/value")
            self.Input_state.append(temp.read())
        return

    # Disables GPIO pins to be changeable. Function for the very end of the program to clean-up loose ends
    def unexport(self):
        for i in range(len(self.Output_pins)):
            os.system("echo "+str(self.Output_pins[i])+" > /sys/class/gpio/unexport")
        for i in range(len(self.Input_pins)):
            os.system("echo "+str(self.Input_pins[i])+" > /sys/class/gpio/unexport")
        return

    # Constructor (startup function for object)
    def __init__(self,model):
        self.model = model # Member variable that identifies the model of the device
        self.Output_state=[] # Member list to store each output pin's state
        self.Input_state=[] # Member list to store each input pin's state
        # Nested IFs to determine GPIO lines based on the device model
        # In the end, the object will have two member lists that store the GPIO lines for the output and input pins
        # by copying two of the lists at the very top of the code
        if model == "MIC-710AI":
            self.Output_pins = MIC_710AI_OUTPUT.copy()
            self.Input_pins = MIC_710AI_INPUT.copy()
        elif model == "MIC-730AI":
            self.Output_pins = MIC_730AI_OUTPUT.copy()
            self.Input_pins = MIC_730AI_INPUT.copy()
        elif model == "MIC-710AIX":
            self.Output_pins = MIC_710AIX_OUTPUT.copy()
            self.Input_pins = MIC_710AIX_INPUT.copy()
        elif model == "MIC-710IVA": #710IVA shares the same gpio lines as 710AIX
            self.Output_pins = MIC_710AIX_OUTPUT.copy()
            self.Input_pins = MIC_710AIX_INPUT.copy()
        elif model == "MIC-730IVA":
            self.Output_pins = MIC_730IVA_OUTPUT.copy()
            self.Input_pins = MIC_730IVA_INPUT.copy()
        else:
            print("I don't have I/O definitions for model: " + model )
            exit()
        self.export() # Set-up GPIO pins to read/write


# Use to find the model of the device
MIC_model_path = "/opt/version" # Read-only file that is made when the BSP is installed in each MIC. Has MIC model there
if os.path.isfile(MIC_model_path): # Checking to make sure the file is real/there
    opened_file = open(MIC_model_path,"r") # Pointer to file in read mode
    text_in_file = opened_file.read() # Take all lines of file as one string
    MIC_model = text_in_file.split("_") # Split the string into a list of strings that are cut where ever an underscore
                                        # is (ex "true_false" -> "true","false")
    MIC_bsp = text_in_file.split(",")
else:
    print(f"File failed to open")
    exit
Device = MIC(MIC_model[0]) # First item in the string list is the MIC model name.

# Refreshes GPIO states on the window every 50ms
def window_refresh():
  button_refresh()
  root.after(50,window_refresh) # 50 is time in ms, window_refresh is the function that is run after x ms in the root window
  return

# Updates the state list for the display based on the device's state list member variable
def button_refresh():
    Device.refresh()
    for i in range(len(Device.Output_state)):
        display_outstates[i].config(text=Device.Output_state[i])
    for i in range(len(Device.Input_state)):
        display_instates[i].config(text=Device.Input_state[i])
    return

# Changes pin state and refreshes window with new state
def button_change(pin):
    Device.change(pin)
    button_refresh()
    return


# Extra window that appears after its button is pressed to show information of the GPIO pins
def popup():
    pop = tkinter.Toplevel(root) # Window call pop that appears over the root window
    pop.title("GPIO Information") # Side-bar icon name
    pop_header = tkinter.Label(pop, text = "GPIO Mappings", font = ("times",15,"bold")) # Defining tkinter "strings"
    pop_in = tkinter.Label(pop, text = "Inputs: "+str(len(Device.Input_pins)), font=("times",12,"bold"))
    pop_out = tkinter.Label(pop, text = "Outputs: "+str(len(Device.Output_pins)), font=("times",12,"bold"))
    pop_display_in = [] # List to contain GPIO input lines
    pop_display_out = [] # List to contain GPIO output lines
    for j in range(len(Device.Output_pins)): # Inserts GPIO lines to correlated list and display the out GPIO text.
        pop_display_out.append(tkinter.Label(pop,text = "Pin "+str(j)+":   "+str(Device.Output_pins[j]),font = ("times",12)))
        pop_display_in.append(tkinter.Label(pop,text = "Pin "+str(j)+":   "+str(Device.Input_pins[j]),font = ("times",12)))
        pop_display_out[j].place(x=100,y=60+(j*30))
    pos_temp = 130+(j*30)
    for k in range(len(pop_display_out)): # Displays the in GPIO text
        pop_display_in[k].place(x=100,y=pos_temp+(k*30))
    pop_header.place(x=100,y=0)
    pop_in.place(x=100, y=100+(j*30))
    pop_out.place(x=100, y=30)
    pop.geometry("300x"+str(pos_temp+50+(k*30))) # Defines the space any text or images can use


root = tkinter.Tk() # Main window that the program functions around
root.title(MIC_model[0]+" GPIO TEST " + VERSION ) # Side-bar icon name
header = tkinter.Label(root, text=MIC_model[0]+" GPIO TEST " + VERSION,font=("times",20,"bold")) # Defining tkinter "strings"
mini_header = tkinter.Label(root, text="BSP: "+MIC_bsp[0],font=("times",10))
out_mess = tkinter.Message(root,text="Output State:")
in_mess = tkinter.Message(root,text="Input State:")
# Button to open the popup window. Don't add () in the command argument or the function will run once at the start
GPIO_button = tkinter.Button(root,width=8,height=1,text="GPIO Info",font=("times",10),command= popup)
pin_num = [] # List of pin numbers (ex 1, 2, 3 ...)
display_outstates = [] # List of output states whose use is for only displaying
display_instates = [] # List of input states whose use is for only displaying
pin_button = [] # List of buttons to change each GPIO pin
for i in range(len(Device.Output_state)):
    pin_num.append(tkinter.Label(root, text="PIN "+str(i),font=(5)))
    pin_num[i].place(x=150+(125*i),y=100)
    display_outstates.append(tkinter.Label(root, text=Device.Output_state[i]))
    display_outstates[i].place(x=150+(125*i),y=150)
    pin_button.append(tkinter.Button(root,width=10,height=3,text="Change Pin "+str(i),command=lambda i=i:button_change(i)))
    pin_button[i].place(x=150+(125*i),y=325)
for i in range(len(Device.Input_state)):
    display_instates.append(tkinter.Label(root, text=Device.Input_state[i]))
    display_instates[i].place(x=150+(125*i),y=250)
root.geometry(str(300+(125*i))+"x400") # Defines the space any text or images can use

GPIO_button.place(x=450,y=35)
out_mess.place(x=50, y=150)
in_mess.place(x=50, y=250)
mini_header.place(x=200, y=35)
header.place(x=200,y=0)

# Opens window and keeps it open
root.mainloop() # Opens main window. Code execution stops here until the root window is closed. '.after' is an exception
root.after(50, window_refresh) # Starts display refresh cycle
time.sleep(1)
Device.unexport() # Wraps up loose ends