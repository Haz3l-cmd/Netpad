import customtkinter
import os
import json

from abc import ABC, abstractmethod
from time import sleep, strftime
from tkinter import messagebox
from sys import stderr

ROUTER_PATH ="./assets/images/router.png"
RECON_PATH = "./recon/recon.json"

class Callback(ABC):
      """This abstract method represents the blueprint for following sub classes. Instances
         if this class are callables, this allows us to circumvent the limitation of not being able 
         to pass arguemnts to callbacks, e.g if we want to  invoke the callback with the arguement text="hello" 
         to customTkinter.CTkButton(master=self), instead of customTkinter.CTkButton(master=self, command=close),
         we would do customTkinter.CTkButton(master=self, command=CloseClass(text="hello")), in this case the callback will be like this :
         CloseClass(text="hello")(), i.e CloseClass(text="hello").__call__(self). As you can see, this gives us much more control and flexibility.
      """
      
      @abstractmethod
      def __init__(self, *args, **kwargs):
      	 """Pass additional arguements"""
      
      @abstractmethod
      def __call__(self, event):
      	 """Calls handler function, additionaly parameters may be supplied to handler function"""
      
      @abstractmethod
      def handler(self, *args, **kwargs):
      	  """Implement here"""


class MoveCompIcons(Callback):
      """ This subclass is sole;y responsible for moving the icons(and labels) on the screen """
      
      def __init__(self, *args, **kwargs):
         """ The arguememts are specific to the class and is not  the for all classes, here the arguement are as follows
             :param args[0]: root frame, self in this case.See netpad.py
             :param args[1]: Tag of the icon/image(The PhotoImage instance)
             :param args[2]: Tag of the label/text
             :param args[3]: Tag of the line that connects the icons to the default gateway
         """
         self.args = args 
         self.kwargs = kwargs

      def __call__(self, event):
          """ The instance of this class is what gets called, hence the __call__ dunder method
              
              :param event: The value of the event, e.g x and y coordinates of cursor
          """
          self.handler(event, self.args[0], self.args[1], self.args[2], self.args[3]) # The method that actually handles everything

      def handler(self, event, root, img_tag, text_tag, line_tag):
          """This method is actually responsible for changing the coordinates of the icons and text
              
             :param event: The value of the event, e.g x and y coordinates of cursor
             :param root: root frame, self in this case.See netpad.py
             :param img_tag: Tag of the icon/image(The PhotoImage instance)
             :param text_tag: Tag of the label/text
             :param line_tag: Tag of the line that connects the icons to the default gate
          """

          root.my_canvas.moveto(img_tag, root.my_canvas.canvasx(event.x-50), root.my_canvas.canvasy(event.y-50)) # Moves icons with respect to cursor position on canvas
          root.my_canvas.moveto(text_tag, root.my_canvas.canvasx(event.x-50), root.my_canvas.canvasy(event.y+50)) # Moves text/label with respect to cursor position on canvas
          
          # Gets midpooint of icon 
          x = ((root.my_canvas.bbox(img_tag)[2] - root.my_canvas.bbox(img_tag)[0])/2)+ root.my_canvas.bbox(img_tag)[0] 
          y = ((root.my_canvas.bbox(img_tag)[3] - root.my_canvas.bbox(img_tag)[1])/2)+ root.my_canvas.bbox(img_tag)[1]

          # Gets midpoint of router
          x2 = ((root.my_canvas.bbox("router")[2] - root.my_canvas.bbox("router")[0])/2)+ root.my_canvas.bbox("router")[0]
          y2 = ((root.my_canvas.bbox("router")[3] - root.my_canvas.bbox("router")[1])/2)+ root.my_canvas.bbox("router")[1]

          root.my_canvas.coords(line_tag, x, y, x2, y2) # Adjusts the connecting line accordingly






           