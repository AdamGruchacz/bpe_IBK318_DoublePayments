"""Paid items
IBK: 318+560
Developed by: Adam Gruchacz, PAT
Process Expert: Piotr Kolanowski
11/10/2022
"""

import messagebox
import data_processing

'#Global variables'
STR_FINAL_INFORMATION: str = ""
MB_YESNO: int = 4
IDYES: int = 6
IDNO: int = 7
IDOK: int = 0


def mainprocess(to_be_paid_path: str, paid_list: list, outputfolder: str, selectederp: str) -> None:
    """
       function checks after user confirmation if all paths selected in user interface
       :param selectederp: string including Dynamics or PeopleSoft
       :param to_be_paid_path:  path of file including data to payments to be paid
       :param paid_list:  list of paths to files including data to paid payments
       :param outputfolder:  path of directory where output file will be stored
       :return: None
     """

    global STR_FINAL_INFORMATION
    global IDOK
    if not all([to_be_paid_path, len(paid_list), outputfolder, selectederp]):
        STR_FINAL_INFORMATION = "at least one file or ERP system not chosen"
    elif not STR_FINAL_INFORMATION:
        data_processing.process(to_be_paid_path, tuple(paid_list), outputfolder, selectederp)
        if not STR_FINAL_INFORMATION:
            STR_FINAL_INFORMATION = 'Completed'

    messagebox.showinformation('Final result', STR_FINAL_INFORMATION)