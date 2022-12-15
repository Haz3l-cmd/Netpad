import customtkinter
import threading
import sys
import random
import json
import argparse

#Custom module/s
from myutils.callbacks import *


from typing import Callable, Dict
from collections import OrderedDict
from time import sleep
from contextlib import contextmanager
from tkinter import Canvas, messagebox, PhotoImage
from PIL import Image, ImageTk
from queue import Queue

# Path of icons
RECON_PATH = "./recon/recon.json"
ROUTER_PATH ="./assets/images/router.png"
REFRESH_PATH ="./assets/images/refresh.png"
COMP_PATH = "./assets/images/computadora.png"
SERVER_PATH = "./assets/images/server.png"
ANDROID_PATH = "./assets/images/android.png"
MSWIN_PATH = "./assets/images/mswin.png"
MSWIN2_PATH = "./assets/images/mswin2.png"
MSWIN_SERVER_PATH = "./assets/images/mswinserver.png"
LIN_SERVER_PATH = "./assets/images/linuxserver.png"
LIN_COMP_PATH = "./assets/images/linuxcomp.png"
UBUNTU_LOGO_PATH = "./assets/images/ubuntu.png"
UBUNTU_DESKTOP_PATH = "./assets/images/ubuntu2.png"
KALI_PATH = "./assets/images/kali.jpg"
EXIT_MSG = "Are you sure to want to exit?"
DISCLAIMER_MSG = "This project was created solely for learning purposes and not otherwise. I am not responsible for your actions."
HOSTS_FILE = None


class Netpad(customtkinter.CTk):
      """ This class contains  just about everything for the app to run, Note that this is the  windows version of Netpad."""

      # Mapper constants
      TAG_TO_ICON = OrderedDict() # Maps Tags to PhotoImage objects
      
      # Maps "LOGO" key to their respective values, see documentation on https://github.com/Haz3l-cmd/Netpad
      LOGO_MAPPING = {"SERVER": SERVER_PATH,
                      "ANDROID": ANDROID_PATH,
                       "MSWIN": MSWIN_PATH,
                       "LINSERVER": LIN_SERVER_PATH,
                       "LINCOMP": LIN_COMP_PATH,
                       "UBUNTU LOGO": UBUNTU_LOGO_PATH,
                       "UBUNTU DESKTOP": UBUNTU_DESKTOP_PATH,
                       "KALI": KALI_PATH
                         }
      
      #Internal constants for root window
      _WINDOW_DIMENSION = "700x400"
      _WINDOW_TITLE  = "Netpad"
      
      #Internal constants for widgets
      PADDING = 5 


      def __init__(self):
          """This function is responsible for initialising the main window"""
          
          super().__init__()
       
          
         
          self.wm_state('zoomed')  # Ensures that window starts in full mode
          self.title(self._WINDOW_TITLE) # Main window title
          self.protocol("WM_DELETE_WINDOW", self.on_closing) # Warns user before exiting
          self.warning() # Disclaimer window

  
          
          
         
       

      
      def warning(self)->None:
          """Thsi method sets up the disclaimer window, users can decide whether they want to continue beyond this point
             
             :return: None
          """

          # Frame that fills up main window
          self.warning_frame = customtkinter.CTkFrame(master=self)
          self.warning_frame.pack(expand=True, fill="both")
          self.grid_maker(row= 3, column=3, weight=1, widget=self.warning_frame)

          # Label displaying disclaimer message
          self.warning_label = customtkinter.CTkLabel(master=self.warning_frame, text=DISCLAIMER_MSG, font=("",15))
          self.warning_label.grid(row=1, column=1, sticky="nsew")
          
          # Button that allows user to proceed further
          self.warning_button = customtkinter.CTkButton(master=self.warning_frame, text="Continue", command=self.clear_root)
          self.warning_button.grid(row=2, column=1, sticky="n")

     

      def clear_root(self)->None:
          """This method clears up the main window after user reads disclaimer and invokes self.setup() to initialise 
             the actual user interface

             :return: None
          """

          # Loops through every child widget and destroys them, a copy is made to prevent RuntimeError: dictionary changed size during iteration
          for child in self.children.copy().values(): 
              child.destroy()
          
          self.setup() # Sets up actual user interface
      

      def setup(self)->None:
          """This method is one of the core methods as it responsible for setting the actual interface
             
             :return: None
          """
          self.my_canvas = Canvas(master=self,bg="black") # Sets up black canvas, who the f*ck uses light mode anyways
          self.my_canvas.pack(expand=True, fill="both")
          
          # Bindings, Implementation are found withinn this file itself, though that might change in the
          # future to be more organised
          self.my_canvas.bind("<Button-3>", self.scan)
          self.my_canvas.bind("<Button3-Motion>", self.drag)
          self.my_canvas.bind("<Motion>", self.display_coords)
          self.my_label = customtkinter.CTkLabel(master=self.my_canvas, text="X: None Y: None", height=20, width=100)
          self.my_label.pack(padx="10px", pady="10px", anchor="ne")
          self.refresh_map_button = customtkinter.CTkButton(master=self.my_canvas, text="Refresh!", command=self.map_refresh, height=30, width=30)
          self.refresh_map_button.pack(padx=self.PADDING, pady=self.PADDING, anchor="ne")
    
      
      def grid_maker(self, row:int = 2, column:int =2 , weight:int = 1, widget=None)->None:
          """This process automates the process of creating grid and coloumn within a widget

             :param row: Number of rows
             :param coloumn: Number of column
             :param weight: Width of column/row relative to others
             :param widget: the widget or frame with needs to have grid and columns configured

             :return: None
          """
          for row in range(row):
              widget.rowconfigure(row, weight=weight)


          for column in range(column):
              widget.columnconfigure(column, weight=weight)
      
      def on_closing(self)->None:
          """This method implements the messagebox that warns the user about saving data before quiting
             
             :Return: None
          """
          if messagebox.askokcancel("Quit", EXIT_MSG):
             self.destroy() # Destroys main window before exiting program
             sys.exit()    

         
    


      def map_refresh(self)->None:
          """This method is responsible for refreshing the canvas. It is responsible
             for deleting images and reloading them by accordingly removing them from self.TAG_TO_ICON()
             so as to not eat up all your RAM

             :Return: None

             parsed config file looks like this --> {IP:{MAC:MAC,
                                                        is_gateway:bool}}
          """
          try:
            LOGO_PATH = COMP_PATH # This is explicitly written here to make sure it always defaults back to COMP_PATH
            
            # Deletes everything from canvas
            if len(self.my_canvas.find_all()) > 1:
               for child in self.my_canvas.find_all():
                    try:
                       self.my_canvas.delete(child)
                       self.my_canvas.delete(f"{child}-Complement")
                       self.TAG_TO_ICON.pop(child)
                    except KeyError:
                       continue
            
            # Opens config file given through the command line
            with open(HOSTS_FILE, "r") as fp:
                 data = OrderedDict(json.load(fp))
            
            # This cryptic looking code simply parses the config file, assuming the format is correct.(JSON format)
            for key, value in data.items():
                info = [f"IP: {key}"]
                for keys, values in value.items():
                    if keys != "is_gateway" and keys != "LOGO":
                      tmp = f"{keys}: {values}"
                      info.append(tmp)
                    else:
                        pass
                    if keys == "LOGO":
                       if values in self.LOGO_MAPPING.keys():
                          LOGO_PATH = self.LOGO_MAPPING.get(values)
                      
                info = "\n".join(info)
                
                # Generates the icon according to config file
                if value.get("is_gateway") is True:
                    self.generate_icon(ROUTER_PATH, info)
                else:
                    self.generate_icon(LOGO_PATH, info)
                    LOGO_PATH = COMP_PATH

          except Exception as e:
                 sys.stderr.write(f"{e}, please verify the config file\n")
          

      def scan(self, event)->None:
          """This method works together with self.drag() to allow user to move around canvas
             
             :param event: Used to access event atrributes
          """
          self.my_canvas.scan_mark(event.x, event.y)

      def drag(self, event):
          """This method works together with self.scan() to allow user to move around canvas
             
             :param event: Used to access event attributes

             :Return: None
          """
          self.my_canvas.scan_dragto(event.x, event.y, gain=2)

      def display_coords(self, event)->None:
          """This method is responsible for updating the X and Y label

             :param event: Used to access event attributes
          """
          self.my_label.configure(text=f"X: {self.my_canvas.canvasx(event.x)} Y:{self.my_canvas.canvasy(event.y)}")

      def generate_icon(self, path:str = COMP_PATH, text:str = "")->None:
          """This method generates icons/images on the canvas
                  
                  :param path: File path of image/icon
                  :param text: Text to be display below icon/image, this has to be the IP and MAC. Fortunately self.map_refresh() handles all of that for us
  
               :Return: None
          """
          try:
            
            # Resizes logo accordingly
            if path != ROUTER_PATH:
              img = Image.open(path) # Opens image
              if path == SERVER_PATH:
                 resized_image = img.resize((50,100))
              elif path == ANDROID_PATH :
                   resized_image = img.resize((130,100))
              elif path == MSWIN_PATH or path == MSWIN2_PATH:
                   resized_image = img.resize((100,100))
              elif path == LIN_SERVER_PATH:
                   resized_image = img.resize((70,100))
              elif path == UBUNTU_DESKTOP_PATH :
                   resized_image = img.resize((150,100))
              elif path == KALI_PATH:
                   resized_image = img.resize((130,85))
              else:
                   resized_image = img.resize((100,100))
              self.image = ImageTk.PhotoImage(resized_image) # Create PhotoImage object
              self.image = self.image # For persistance
                
              # self.my_image is a tag(an integer in this case) to later modify the image/icon
              # random.randrange() causes the image/icon to appear at differnet location after each refresh
              self.my_image = self.my_canvas.create_image(random.randrange(0, 500-50),random.randrange(0, 700-50), image=self.image)
                
              # A mapping of tags to PhotoImage object,
              # This allows the image to remain in memory and not be overwritten otherwise it would defeat the whole purpose of this project
              self.TAG_TO_ICON.update({self.my_image: self.image })
  
              # (x, y) represents the midpoint of the hosts image/icon, in this case it is found at COMP_PATH, see above
              x = ((self.my_canvas.bbox(self.my_image)[2] - self.my_canvas.bbox(self.my_image)[0])/2)+ self.my_canvas.bbox(self.my_image)[0]
              y  = ((self.my_canvas.bbox(self.my_image)[3] - self.my_canvas.bbox(self.my_image)[1])/2)+ self.my_canvas.bbox(self.my_image)[1]
            
              # (x2, y2) represents the midpoint of the router image/icon, in this case it is found at ROUTER_PATH, see above
              x2  = ((self.my_canvas.bbox("router")[2] - self.my_canvas.bbox("router")[0])/2)+ self.my_canvas.bbox("router")[0]
              y2  = ((self.my_canvas.bbox("router")[3] - self.my_canvas.bbox("router")[1])/2)+ self.my_canvas.bbox("router")[1]
  
              # Draws line between the two midpoints
              self.line_tag = self.my_canvas.create_line(x, y, x2, y2, fill="white")
                
              # (x3, y3) marks the start of the label which display the IP and MAC
              x3 = self.my_canvas.bbox(self.my_image)[0]
              y3 = self.my_canvas.bbox(self.my_image)[3]
  
              # All tags of label which display IP and MAC will have a trailing "-Complement" after the tag of their 
              # respective icon they are representing, e.g and icon having a tag of 4 will have a label with the tag
              # 4-Complement
              self.text_tag = f"{self.my_image}-Complement" # Here we it being implemented
  
              # See implementation of MoveCompIcon() in myutils/callbacks.py
              self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag, self.line_tag ), add="+")
              # self.my_canvas.tag_bind(self.my_image,"<ButtonPress-3>", self.top_level, add="+")
              self.my_canvas.create_text(x3, y3, text=text, fill="white",tags=self.text_tag, anchor="nw", font=("Comic sans", 9))
               
            else:
                canvas_width =self.my_canvas.winfo_width() # width of canvas
                canvas_height = self.my_canvas.winfo_height() # height of canvas
                img = Image.open(ROUTER_PATH) # Opens image
                resized_image = img.resize((100,100)) # Resizez image to appropriate size
                self.image = ImageTk.PhotoImage(resized_image)  # Create PhotoImage object
                self.image = self.image  # For persistance
  
                # self.my_image is a tag(an integer in this case) to later modify the image/icon
                # This canvas item always spawns in the center after a refresh, regardless of canvas dimensions
                self.my_image = self.my_canvas.create_image(canvas_width/2, canvas_height/2, image=self.image, tags="router")
  
                # A mapping of tags to PhotoImage object,
                # This allows the image to remain in memory and not be overwritten otherwise it would defeat the whole purpose of this project            
                self.TAG_TO_ICON.update({self.my_image: self.image })
  
                # Initialy no line is created due to the fact that
                # router image/router is create alone
                self.line_tag = self.my_canvas.create_line(0, 0, 0, 0, fill="white")
  
                # All tags of label which display IP and MAC will have a trailing "-Complement" after the tag of their 
                # respective icon they are representing, e.g and icon having a tag of 4 will have a label with the tag
                # 4-Complement
                self.text_tag = f"{self.my_image}-Complement"
  
                # See implementation of MoveCompIcon() in myutils/callbacks.py
                # self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag), add="+")
                
                # These coordinates are used to align label with router icon/image
                x1, y1, x2, y2 = self.my_canvas.bbox(self.my_image)
                self.my_canvas.create_text(x1, y2-20, text=text, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20)
                self.my_canvas.create_text(x1, y2-20, text=None, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20) #Filler
            
          except  Exception as e:
                  print(e)
      


if __name__ == "__main__":
    """ This portion initialises CLI"""
    
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter, description="This program helps you visualise a network, helpful when enumerating networks", epilog="Usage:\n\tpython3 netpad.py -f hosts.json\n\nReport bugs to https://github.com/Haz3l-cmd/Netpad" )
    parser.add_argument("-f","--file",help="File to parse, in JSON format. Format is {IP:{MAC:MAC, is_gateway:bool}} ",metavar="file.json", required=True, dest="file",type=str)
    parse = parser.parse_args()
    HOSTS_FILE = parse.file
    
    # Starts main loop
    app = Netpad()
    app.mainloop()


