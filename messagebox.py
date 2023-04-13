from tkinter.messagebox import showinfo

def showinformation(title: str,message: str ) -> None:
    """
          function checks after user confirmation if all paths selected in user interface
          :param title: string representing top text of window
          :param message:  string of final information to be presented
          :return: None
        """
    showinfo(title=title, message=message)
