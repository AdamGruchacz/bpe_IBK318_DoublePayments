"""
Paid items
IBK:318+560
Developed by: Adam Gruchacz, PAT
Process Expert: Piotr Kolanowski
11/10/2022
Module for GUI creation
"""
from pathlib import Path
from tkinter import Button, OptionMenu, StringVar, Tk, filedialog as fd, ttk

import main


class GUI:
    """
    class for GUI creation
    """
    CCC: str
    AUTOMATION_TITLE: str = 'AX/PS Double Payments'
    SELECT_FILE_STR: str = 'Select to be paid file'
    EMPTY_PATH_COLOR: str = '#F0F0F0'
    FILLED_PATH_COLOR: str = '#69BE28'
    FOCUS_COLOR: str = '#D2785A'
    RUN_BUTTON_COLOR: str = '#DBD99A'

    # Automation geometry
    MULTIPLIER: int = 20
    X_1: int = MULTIPLIER
    Y_1: int = MULTIPLIER
    SEPARATOR_1: int = MULTIPLIER * 2
    Y_2: int = SEPARATOR_1 + MULTIPLIER
    Y_3: int = SEPARATOR_1 + MULTIPLIER * 3
    SEPARATOR_2: int = SEPARATOR_1 + MULTIPLIER * 5
    Y_4: int = SEPARATOR_1 + MULTIPLIER * 6
    Y_5: int = SEPARATOR_1 + MULTIPLIER * 8
    Y_6: int = SEPARATOR_1 + MULTIPLIER * 10
    Y_7: int = SEPARATOR_1 + MULTIPLIER * 12
    SHORT_WIDTH: int = int(0.6 * MULTIPLIER)
    LONG_WIDTH: int = int(1.6 * MULTIPLIER)
    LONG_HEIGHT: int = int(MULTIPLIER / 10)
    SHORT_HEIGHT: int = int(MULTIPLIER / 20)
    WINDOW_SIZE: str = f'{MULTIPLIER * 15}x{MULTIPLIER * 17}'
    OPTION_MENU_WIDTH_2: int = int(MULTIPLIER * 1.0)
    ERP: list[str] = ['Dynamics', 'PeopleSoft']

    # OptionMenu initial values
    ERP_SELECT: str = 'Select ERP system'

    def __init__(self,
                 master: Tk,
                 init_path: Path = Path(),
                 output_path: Path = Path(),
                 final_path: Path = Path()) -> None:

        self.master = master
        self.report_path = init_path
        self.template_path = final_path
        self.output_folder = output_path
        self.filez = list()
        master.title(GUI.AUTOMATION_TITLE)

        self.rep_path_button: Button = Button(master,
                                              text="Load 'Paid items' input file(s)",
                                              command=self.select_report_path,
                                              height=GUI.SHORT_HEIGHT,
                                              width=GUI.LONG_WIDTH)
        self.rep_path_button.place(x=GUI.X_1,
                                   y=GUI.Y_1)

        self.templ_path_button: Button = Button(master,
                                                text="Load 'To pay' input file",
                                                command=self.select_templ_path,
                                                height=GUI.SHORT_HEIGHT,
                                                width=GUI.LONG_WIDTH)
        self.templ_path_button.place(x=GUI.X_1,
                                     y=GUI.Y_2)
        self.output_path_button: Button = Button(master,
                                                 text="Load 'output' directory",
                                                 command=self.select_output_directory,
                                                 height=GUI.SHORT_HEIGHT,
                                                 width=GUI.LONG_WIDTH)
        self.output_path_button.place(x=GUI.X_1,
                                      y=GUI.Y_3)
        self.erp = StringVar(master)
        self.erp.set(GUI.ERP_SELECT)
        self.erp_option = OptionMenu(
            master,
            self.erp,
            *GUI.ERP,
            command=lambda _: self.change_option_states())
        self.erp_option.config(width=GUI.LONG_WIDTH)
        self.erp_option.pack()
        self.erp_option.place(x=GUI.X_1,
                              y=GUI.Y_4)

        self.run_automation_button: Button = Button(master,
                                                    text="Run Automation",
                                                    command=self.run,
                                                    height=GUI.SHORT_HEIGHT,
                                                    width=GUI.LONG_WIDTH,
                                                    bg=GUI.RUN_BUTTON_COLOR)
        self.run_automation_button.place(x=GUI.X_1,
                                         y=GUI.Y_5)

        self.separator_first = ttk.Separator(master,
                                             orient='horizontal')
        self.separator_first.place(x=0,
                                   y=GUI.SEPARATOR_2,
                                   relwidth=GUI.SHORT_HEIGHT)
        self.label_text = StringVar()
        '''self.label_text.set('Status: not running')
        self.label = Label(master, textvariable=self.label_text)
        self.label.place(x=17, y=GUI.Y_6)'''
        self.clear_button: Button = Button(master,
                                           text="Clear all selections",
                                           command=self.clear_all,
                                           height=GUI.SHORT_HEIGHT,
                                           width=GUI.LONG_WIDTH)
        self.clear_button.place(x=GUI.X_1,
                                y=GUI.Y_7)
        self.selected_erp = ""

    def change_option_states(self) -> None:
        """
        function gets selected erp value and change button color
        :return:
        """
        self.selected_erp = self.erp.get()
        if self.selected_erp != "":
            self.erp_option.configure(bg=GUI.FILLED_PATH_COLOR)
        else:
            pass  # linia z else i pass nie jest potrzebna

    def test(self) -> None:
        """
        function gets selected erp value and change button color
        :return:
        """
        self.selected_erp = self.erp.get()
        if self.selected_erp != "":
            self.erp_option.configure(bg=GUI.FILLED_PATH_COLOR)
        else:
            pass  # linia z else i pass nie jest potrzebna

    def clear_all(self) -> None:
        """
        function gets back the automation to initial state
        :return: None
        """
        self.report_path = Path()
        self.rep_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.template_path = Path()
        self.templ_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.output_folder = Path()
        self.output_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.erp.set(GUI.ERP_SELECT)
        self.erp_option.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.run_automation_button['state'] = 'normal'

    def select_report_path(self) -> Path:
        """
        function loads paid reports paths
        :return: path to file
        """
        self.rep_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.filez = fd.askopenfilenames(parent=root, title='Choose a paid file(s)')
        if len(self.filez) != 0:
            self.rep_path_button.configure(bg=GUI.FILLED_PATH_COLOR)
        else:
            self.rep_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        return self.report_path

    def select_templ_path(self) -> Path:
        """
        function loads TobePaid path
        :return: path to file
        """
        self.templ_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.template_path = Path(fd.askopenfilename(
            title=GUI.SELECT_FILE_STR))
        if self.template_path != Path():
            self.templ_path_button.configure(bg=GUI.FILLED_PATH_COLOR)
        else:
            self.templ_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        return self.template_path

    def select_output_directory(self) -> Path:
        """
        function loads directory of folder where output file will saved
        :return: path to file
        """
        self.output_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        self.output_folder = fd.askdirectory(parent=root, title='Choose a folder')
        '''self.filez = fd.askdirectory(parent=root, title='Choose a file')'''
        '''if self.report_path != Path():'''
        if len(self.output_folder) != 0:
            self.output_path_button.configure(bg=GUI.FILLED_PATH_COLOR)
        else:
            self.output_path_button.configure(bg=GUI.EMPTY_PATH_COLOR)
        return self.report_path

    def run(self) -> None:
        """
        function runs the automation
        :return: None
        """

        '''self.run_automation_button.configure(bg=GUI.FILLED_PATH_COLOR)'''
        self.run_automation_button['state'] = 'disabled'
        try:
            main.mainprocess(str(self.template_path), self.filez, str(self.output_folder), self.selected_erp)
        except Exception:
            pass
        exit()


if __name__ == "__main__":
    root = Tk()
    my_gui = GUI(root)
    root.geometry(my_gui.WINDOW_SIZE)
    root.attributes('-topmost', True)
    root.mainloop()
