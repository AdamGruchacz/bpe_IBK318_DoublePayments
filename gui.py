#!/usr/bin/python3
"""
IPE Reports Check
IBK 337
PAT: Adam Gruchacz & Michał Gurtowski
# developed using as start point template of feedback_solution.py by Barron Stone
# based on file from Python GUI Development with Tkinter on lynda.com
SME: Augustyna Radomyska & Małgorzata Redzinska
01/Oct/2024

Module for GUI creation
"""
from tkinter import *
from tkinter import ttk, filedialog, messagebox, IntVar

import config
import invoice_reader
import os


class IbkCombineInvoices:

    def __init__(self, master):
        master.title(config.IBK_NUMBER + " " + config.IBK_TITLE + " - User Form")
        master.resizable(False, False)
        master.configure(background='#C0D4CB')

        self.style = ttk.Style()
        self.style.configure('TFrame', background='#C0D4CB')
        self.style.configure('TButton', background='#538184')
        self.style.configure('TLabel', background='#C0D4CB', font=('Arial', 8))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        self.frame_header = ttk.Frame(master)
        self.frame_header.pack()
        ttk.Label(self.frame_header, text=config.IBK_TITLE, style='Header.TLabel').grid(row=0, column=0, sticky="sw")
        ttk.Label(self.frame_header, wraplength=300,
                  text="developed by Process Automation Team").grid(row=1, column=0, sticky='sw')
        self.frame_content = ttk.Frame(master)
        self.frame_content.pack()

        # lambda -  it won't execute right away, instead waiting until the button is clicked.
        ttk.Button(self.frame_content, text='Press to browse first invoice in pdf format)',
                   command=lambda: self.get_first_pdf()).grid(row=0, column=0, padx=5, pady=5, sticky='sw')
        ttk.Button(self.frame_content, text='Press to browse second invoice in pdf format',
                   command=lambda: self.get_second_pdf()).grid(row=2, column=0, padx=5, pady=5, sticky='sw')
        ttk.Button(self.frame_content, text='Press to browse folder in which output file will be saved',
                   command=lambda: self.get_first_folder()).grid(row=4, column=0, padx=5, pady=5, sticky='sw')
        ttk.Button(self.frame_content, text='Press to browse cbre logo',
                   command=lambda: self.get_logo()).grid(row=6, column=0, padx=5, pady=5, sticky='sw')
        '''ttk.Button(self.frame_content, text='TODO 2',
                   command=lambda: self.get_embedding_macro_path()).grid(row=8, column=0, padx=5, pady=5, sticky='sw')
        '''
        ttk.Label(self.frame_content, text='Manual / invoices format expectations:', width=70,
                  font=('Arial', 10)).grid(row=11, column=0, padx=5, sticky='sw')
        ttk.Label(self.frame_content, text='1. Expected invoice format: YYYY-6digits-4digits', width=70,
                  font=('Arial', 8)).grid(row=12, column=0, padx=5, sticky='sw')
        ttk.Label(self.frame_content, text='2. Deal ID equals invoice without last 4 characters', width=70,
                  font=('Arial', 8)).grid(row=13, column=0, padx=5, sticky='sw')
        ttk.Label(self.frame_content, text='3. Reference information equals invoice number', width=70,
                  font=('Arial', 8)).grid(row=14, column=0, padx=5, sticky='sw')
        ttk.Label(self.frame_content, text='4. Producer includes small letters to be recognized correctly', width=70,
                  font=('Arial', 8)).grid(row=15, column=0, padx=5, sticky='sw')
        self.entry_first_pdf = ttk.Entry(self.frame_content, width=85, font=('Arial', 8))
        self.entry_second_pdf = ttk.Entry(self.frame_content, width=85, font=('Arial', 8))
        self.entry_first_folder = ttk.Entry(self.frame_content, width=85, font=('Arial', 8))
        self.entry_logo = ttk.Entry(self.frame_content, width=85, font=('Arial', 8))
        self.var1 = IntVar()
        self.c1 = ttk.Checkbutton(self.frame_content, text='Revised', variable=self.var1, onvalue=1, offvalue=0)
        self.entry_first_pdf.grid(row=1, column=0, padx=5)
        self.entry_second_pdf.grid(row=3, column=0, padx=5)
        self.entry_first_folder.grid(row=5, column=0, padx=5)
        self.entry_logo.grid(row=7, column=0, padx=5)
        self.c1.grid(row=9, column=0, padx=5, sticky='w')

        ttk.Button(self.frame_content, text='Launch',
                   command=self.submit).grid(row=10, column=0, padx=5, pady=5, sticky='w')
        ttk.Button(self.frame_content, text='Clear',
                   command=self.clear).grid(row=10, column=0, padx=5, pady=5, sticky='e')
        import sys

        exe_path = sys.executable
        folder_path = os.path.dirname(exe_path)
        full_path = os.path.abspath(os.path.join(folder_path, "cbre_logo.jpg"))
        self.entry_logo.insert(0, full_path)

    def get_first_pdf(self) -> None:
        """
            function get full path of first pdf file
        """
        file_path = filedialog.askopenfilename()
        self.entry_first_pdf.delete(0, 'end')  # clear previous value
        self.entry_first_pdf.insert(0, file_path)

    def get_second_pdf(self) -> None:
        """
            function get full path of second pdf file
        """
        file_path = filedialog.askopenfilename()
        self.entry_second_pdf.delete(0, 'end')  # clear previous value
        self.entry_second_pdf.insert(0, file_path)

    def get_first_folder(self) -> None:
        """
            function get full path folder
        """
        file_path = filedialog.askdirectory()
        self.entry_first_folder.delete(0, 'end')  # clear previous value
        self.entry_first_folder.insert(0, file_path)

    def get_logo(self) -> None:
        """
            function get full path of logo file
        """
        file_path = filedialog.askopenfilename()
        self.entry_logo.delete(0, 'end')  # clear previous value
        self.entry_logo.insert(0, file_path)

    '''
    def get_embedding_macro_path(self) -> None:
        """
           TODO function get full path of xlsm file from user
        """
        file_path = filedialog.askopenfilename()
        self.entry_macro_path.delete(0, 'end')  # clear previous value
        self.entry_macro_path.insert(0, file_path)
    '''
    def submit(self) -> None:
        """
            function run main code passing values from GUI and show up final message
        """
        final_message = ""
        if not self.entry_first_pdf.get().lower().endswith("pdf"):
            messagebox.showerror("path error", "incorrect extension of first pdf file")
        elif not self.entry_second_pdf.get().lower().endswith("pdf"):
            messagebox.showerror("path error", "incorrect extension of second pdf file")
        elif not self.entry_logo.get().lower().endswith("jpg"):
            messagebox.showerror("path error", "incorrect extension of second logo file")
        elif not os.path.isdir(self.entry_first_folder.get().lower()):
            messagebox.showerror("path error", "expected directory location")
        else:
            final_message = invoice_reader.create_pdf_file(self.entry_first_pdf.get(),
                                                           self.entry_second_pdf.get(),
                                                           self.entry_first_folder.get(),
                                                           self.entry_logo.get(),
                                                           self.var1.get())
        if final_message == config.FINAL_MESSAGE or final_message == config.FINAL_MESSAGE_2_PAGES:
            messagebox.showinfo("Final statement", final_message)
        else:
            messagebox.showerror("Error - not completed", final_message)

    def clear(self) -> None:
        """
            function clear all path selected in gui
        """
        self.entry_first_pdf.delete(0, 'end')
        self.entry_second_pdf.delete(0, 'end')
        self.entry_first_folder.delete(0, 'end')
        self.entry_logo.delete(0, 'end')
        self.var1.set(0)


def main() -> None:
    root = Tk()
    IbkCombineInvoices(root)
    root.mainloop()


if __name__ == "__main__":
    main()
