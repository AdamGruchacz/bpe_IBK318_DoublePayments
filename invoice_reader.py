import os.path


from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBox, LTTextLineHorizontal, LTChar
import re
from reportlab.lib.utils import ImageReader
import reportlab.lib.colors as colors
from reportlab.pdfgen import canvas

import config
import utils


list_breakpoints = [config.CONSIDERATION_COMMISSION,
                    config.INVOICE_DETAIL,
                    "DEAL PAYMENT HISTORY",
                    "Comments :|DEAL SUMMARY:",
                    "REMITTANCE INSTRUCTION:"]


class Invoice:
    page_height = 0

    def __init__(self):
        self.header = []
        self.cc_calc = []
        self.inv_detail = []
        self.deal_pmt_history = []
        self.comments_summary = []
        self.remittance = []

        self.invoice_sections = [self.header, self.cc_calc, self.inv_detail, self.deal_pmt_history,
                                 self.comments_summary, self.remittance]


def print_history_and_get_values(original_section: list, dicthistory: dict, section: dict,
                                 output_canvas:  canvas.Canvas, start_y: float = 0) -> list:
    """
        function print section to canvas without text adjustment
        :param original_section: list including rows of section
        :param dicthistory: dictionary including aggregated details rom both deal history sections
        :param section: dictionary including rows of section
        :param output_canvas: self-explanatory
        :param start_y: start position
        :return: list (float, float, float)
   """
    total_amount = 0
    for value in dicthistory.values():
        total_amount = total_amount + value[3]

    if not section:
        return start_y, float(0.00), float(0.00)

    page_top_bottom_margin = 66
    gap_between_paragraphs = 15
    section_start_y = original_section[0].y - gap_between_paragraphs
    '''start_y = start_y + gap_between_paragraphs'''
    '''phrase_after = ""
    final_y = 0'''

    section_offset = 0
    '''if start_y != 0:
        section_offset = section_start_y - start_y + gap_between_paragraphs'''

    if original_section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        '''start_y = Invoice.page_height - page_top_bottom_margin'''
    '''    section_offset = section_start_y - start_y + gap_between_paragraphs
    else:
        section_offset = section_offset + gap_between_paragraphs - 100'''

    # print headers
    x_first_column = 41.4
    x_second_column = 171.9
    x_third_column = 279.9
    x_fourth_column = 505.51
    '''x_fourth_column_data = 548.10'''
    output_canvas.setFont("Times-Bold", 10.53)
    output_canvas.drawString(x_first_column, section_start_y-30 - 75, "DEAL PAYMENT HISTORY")
    output_canvas.setFillColor(colors.yellowgreen)
    output_canvas.rect(x_first_column, section_start_y - 30 - 11.50 - 75 - 3, config.RECTANGLE_WIDTH, 12, fill=1,
                       stroke=0)
    output_canvas.setFillColorRGB(0, 0, 0)  # back to black
    output_canvas.drawString(x_first_column, section_start_y - 30 - 11.50 - 75, "Payment Received Date")
    output_canvas.drawString(x_second_column, section_start_y - 30 - 11.50 - 75, "Check #")
    output_canvas.drawString(x_third_column, section_start_y - 30 - 11.50 - 75, "Invoice # Applied")
    output_canvas.drawString(x_fourth_column, section_start_y - 30 - 11.50 - 75, "Payment Received")
    output_canvas.setFont("Times-Roman", 9.05)
    for key, value in dicthistory.items():
        section_start_y = section_start_y - 11.5
        output_canvas.drawString(x_first_column, section_start_y - 30 - 11.50 - 75, value[0])
        output_canvas.drawString(x_second_column, section_start_y - 30 - 11.50 - 75, value[1])
        output_canvas.drawString(x_third_column, section_start_y - 30 - 11.50 - 75, value[2])
        formatted_amount = utils.get_final_total(value[3], 0, False)
        output_canvas.drawString(config.SUMMARY_X_POSITION_INVOICE_DETAIL - output_canvas.stringWidth(formatted_amount),
                                 section_start_y - 30 - 11.50 - 75, formatted_amount)
    section_start_y = section_start_y - 11.5
    output_canvas.setFont("Times-Bold", 9.38)
    output_canvas.drawString(364.62, section_start_y - 30 - 11.50 - 75, "Total Payment Received To Date:")
    formatted_amount = utils.get_final_total(total_amount, 0, False)
    output_canvas.drawString(config.SUMMARY_X_POSITION_INVOICE_DETAIL - output_canvas.stringWidth(formatted_amount),
                             section_start_y - 30 - 11.50 - 75, formatted_amount)
    section_start_y = section_start_y - gap_between_paragraphs - 170
    return section_start_y, total_amount, total_amount


def first_character_from_line(text_line: LTTextLineHorizontal) -> LTChar:
    """
        function first_character_from_line
        :param text_line: LTTextLineHorizontal
        :return: LTChar
   """
    for character in text_line:
        if isinstance(character, LTChar):
            if character.get_text() in [" ", "-"]:
                continue
            return character


class TextBoxPDF:
    DECREASE_CHAR_SIZE_BY = 1

    def __init__(self, line: LTTextLineHorizontal):
        self.text = line.get_text().strip(' \n')
        if not self.text:
            self.has_text = False
        else:
            self.has_text = True
            character: LTChar = first_character_from_line(line)
            self.font_name = character.fontname
            self.font_size = character.size - TextBoxPDF.DECREASE_CHAR_SIZE_BY
            self.x = line.x0
            self.y = line.y1

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def append_text(self, text):
        self.text += text


def read_invoice(inv_path: str, page_order: int) -> tuple[list, float, float]:
    """
        function read invoice
        :param inv_path: self-explanatory
        :param page_order: indicate number of page in pdf
        :return: list, float, float
   """
    text_fields = []
    with open(inv_path, 'rb') as pdf:
        res_mgr = PDFResourceManager()
        la_params = LAParams(char_margin=1)
        device = PDFPageAggregator(res_mgr, laparams=la_params)
        interpreter = PDFPageInterpreter(res_mgr, device)
        for page in PDFPage.get_pages(pdf):
            interpreter.process_page(page)
            layout = device.get_result()
            page_h = page.mediabox[3]
            page_w = page.mediabox[2]
            if layout.pageid == page_order:
                for element in layout:
                    if isinstance(element, LTTextBox):
                        for text_line in element:
                            text_fields.append(text_line)

    return text_fields, page_h, page_w


def sort_invoice(boxes: list, height: float) -> list:
    """
        function sort invoice
        :param boxes: list
        :param height: float
        :return: list
   """
    Invoice.page_height = height
    y_sorted_fields = sorted(boxes, key=lambda f: height - f.y1)
    sorted_fields = []
    same_row = []
    for i in range(len(y_sorted_fields)):
        current_field = y_sorted_fields[i]
        same_row.append(current_field)

        if i == len(y_sorted_fields) - 1:
            same_row = sorted(same_row, key=lambda f: f.x0)
            sorted_fields.extend(same_row)
            same_row.clear()
            break

        next_field = y_sorted_fields[i + 1]

        if current_field.y1 - next_field.y1 > 8:
            same_row = sorted(same_row, key=lambda f: f.x0)
            sorted_fields.extend(same_row)
            same_row.clear()
    return sorted_fields


def section_invoice(inv_lines: list, page_order: int = 1) -> Invoice:
    """
        function get section of invoice
        :param inv_lines: list including rows of invoices
        :param page_order: integer indicating number of page on pdf
        :return: Invoice
   """
    sectioned_inv = Invoice()
    current_section = 0
    for i in inv_lines:
        line = TextBoxPDF(i)
        if line.has_text:
            if page_order == 1:
                for bp in range(len(list_breakpoints)):
                    if line.get_text().rstrip(" ") in list_breakpoints[bp]:
                        current_section = bp + 1
                sectioned_inv.invoice_sections[current_section].append(line)
            else:
                sectioned_inv.invoice_sections[5].append(line)  # remittance

    return sectioned_inv


def print_section_and_adjust_comment_section(section: list, total_amount_due_this_invoice: str, total_commission: str,
                                             remaining_balance_due: str, total_payment_received: str,
                                             output_canvas: canvas.Canvas,
                                             start_y: float = 0) -> float:
    """
        function print section to canvas without text adjustment
        :param section: list including rows of section
        :param total_amount_due_this_invoice: text replacement of less_total_paid_to_date
        :param total_commission: presented as string
        :param remaining_balance_due: presented as string
        :param total_payment_received: presented as string
        :param output_canvas: self-explanatory
        :param start_y: start position
        :return: float
   """
    if not section:
        return start_y

    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = start_y  # section[0].y

    final_y = 0

    section_offset = 0
    if start_y != 0:
        section_offset = section_start_y - gap_between_paragraphs

    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs

    update_less_total_paid_to_date = False
    update_total_amount_due_this_invoice = False
    update_plus_reimbursable_expense = False
    update_less_cooperating_broker_paid_by_client = False
    update_commission = False
    update_remaining_balance_due = False
    for line in section:
        output_canvas.setFont(line.font_name, line.font_size)
        if update_less_total_paid_to_date:
            output_canvas.drawString(config.SUMMARY_X_POSITION - output_canvas.stringWidth(total_payment_received),
                                     line.y - section_offset, total_payment_received)
            update_less_total_paid_to_date = False
        elif update_remaining_balance_due:
            output_canvas.drawString(config.SUMMARY_X_POSITION - output_canvas.stringWidth(remaining_balance_due),
                                     line.y - section_offset, remaining_balance_due)
            update_remaining_balance_due = False
        elif update_commission:
            output_canvas.drawString(config.SUMMARY_X_POSITION - output_canvas.stringWidth(total_commission),
                                     line.y - section_offset, total_commission)
            update_commission = False
        elif update_total_amount_due_this_invoice:
            output_canvas.drawString(config.SUMMARY_X_POSITION -
                                     output_canvas.stringWidth(total_amount_due_this_invoice),
                                     line.y - section_offset, total_amount_due_this_invoice)
            update_total_amount_due_this_invoice = False
        elif update_plus_reimbursable_expense:
            output_canvas.drawString(config.SUMMARY_X_POSITION - output_canvas.stringWidth("$0.00"), line.y -
                                     section_offset, "$0.00")  # constant amount
            update_plus_reimbursable_expense = False
        elif update_less_cooperating_broker_paid_by_client:
            output_canvas.drawString(config.SUMMARY_X_POSITION - output_canvas.stringWidth("-$0.00"), line.y -
                                     section_offset, "-$0.00")  # constant amount
            update_less_cooperating_broker_paid_by_client = False
        elif "Remaining Balance Due".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_remaining_balance_due = True
        elif "Transaction Commission".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_commission = True
        elif "Less: Total Paid To Date".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_less_total_paid_to_date = True
        elif "Total amount Due this Invoice".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_total_amount_due_this_invoice = True
        elif "Plus: Reimbursable Expense".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_plus_reimbursable_expense = True
        elif "Cooperating  Broker paid by Client".upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            update_less_cooperating_broker_paid_by_client = True
        else:
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
        final_y = line.y - section_offset
    return final_y


def print_history_and_get_value(dicthistory: dict, section: list, output_canvas:  canvas.Canvas,
                                first_invoice_name: str, second_invoice_name: str,
                                first: bool, start_y: float = 0) -> list:
    """
        function print section to canvas without text adjustment
        :param dicthistory: dictionary including aggregated details rom both deal history sections
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param first_invoice_name: self-explanatory
        :param second_invoice_name: self-explanatory
        :param start_y: start position
        :param first: True equals for first passed deal history section
        :return: list (float, float, float)
   """
    total_amount = 0
    if not first:
        for value in dicthistory.values():
            total_amount = total_amount + value[3]

    if not section:
        return start_y, float(0.00), float(0.00)

    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = section[0].y
    final_y = 0

    section_offset = 0
    if start_y != 0:
        if first:
            section_offset = section_start_y - start_y + gap_between_paragraphs
        else:
            section_offset = section_start_y - start_y - 13

    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs

    get_invoice_value = False
    start_printing = False
    payment_received_date_collected = False
    invoices_amount = 0
    check = ""
    payment_received_date = ""
    total_printing = False
    if first:
        start_printing = True
    for line in section:
        if (("Payment Received".upper() in str(line.get_text()).upper() and not first and not
            "Payment Received Date".upper() in str(line.get_text()).upper()) and not "Total".upper() in
                str(line.get_text()).upper()):
            start_printing = True
            if not "Payment Received".upper() and not first:
                output_canvas.setFont(line.font_name, line.font_size)
                output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
        else:
            if payment_received_date_collected:
                check = str(line.get_text())
                payment_received_date_collected = False
            if "/" in str(line.get_text()):
                payment_received_date = str(line.get_text())
                payment_received_date_collected = True
            if config.TOTAL_PAYMENT_RECEIVED_TO_DATE.upper() in str(line.get_text()).upper() and first:
                break
            if "Payment Received Date".upper() in str(line.get_text()).upper() and first:
                # Draw the background rectangle
                output_canvas.setFillColor(colors.yellowgreen)
                output_canvas.rect(line.x, line.y - section_offset - 1, config.RECTANGLE_WIDTH, 9, fill=1, stroke=0)
                output_canvas.setFillColorRGB(0, 0, 0)  # back to black
            if start_printing:
                output_canvas.setFont(line.font_name, line.font_size)
                if "-" in str(line.get_text()):
                    dict_item = dicthistory[check + "_" + payment_received_date]
                    output_canvas.drawString(line.x, line.y - section_offset, dict_item[2])
                elif "$" in str(line.get_text()) and not total_printing:
                    dict_item = dicthistory[check + "_" + payment_received_date]
                    formatted_amount = utils.get_final_total(dict_item[3], 0, False)
                    output_canvas.drawString(config.SUMMARY_X_POSITION_INVOICE_DETAIL -
                                             output_canvas.stringWidth(formatted_amount), line.y - section_offset,
                                             formatted_amount)
                else:
                    if total_printing:
                        total_amount_formatted = utils.get_final_total(total_amount, 0, False)
                        output_canvas.drawString(config.SUMMARY_X_POSITION_INVOICE_DETAIL -
                                                 output_canvas.stringWidth(total_amount_formatted),
                                                 line.y - section_offset, total_amount_formatted)
                        total_printing = False
                    elif "Total".upper() in str(line.get_text()).upper() and not first:
                        total_printing = True
                        output_canvas.setFont(line.font_name, line.font_size)
                        output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
                    elif not total_printing:
                        output_canvas.setFont(line.font_name, line.font_size)
                        output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
                final_y = line.y - section_offset
            if get_invoice_value:
                invoices_amount = (invoices_amount +
                                   float(str(line.get_text()).replace("$", "").replace(",", "")))
                get_invoice_value = False
            if first_invoice_name in str(line.get_text()) or second_invoice_name in str(line.get_text()):
                get_invoice_value = True
    return final_y, total_amount, invoices_amount


def print_section_with_adjustments(section: list, output_canvas: canvas.Canvas, invoice_name: str,
                                   original_producer: str, new_producer: str, revision: int,
                                   start_y: float = 0) -> float:
    """
        function print section to canvas with adjustment where needed
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param invoice_name: to be appeared on new document
        :param original_producer: value to be replaced
        :param new_producer: replacement value foe original_producer
        :param start_y: vertical start position
        :param revision - if 1 then add R on the end of merged invoices number
        :return: float
   """

    if not section:
        return start_y
    if revision == 1:
        additional_r = "R"
    else:
        additional_r = ""
    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = section[0].y

    final_y = 0

    section_offset = 0
    if start_y != 0:
        section_offset = section_start_y - start_y + gap_between_paragraphs

    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs

    for line in section:
        match_deal_id = re.search(config.DEAL_ID_PATTERN, str(line.get_text()))
        if (original_producer == str(line.get_text()).replace(".",
           "").replace("'", "").replace(",", "")):  # Producer name adjustment
            output_canvas.setFont(line.font_name, line.font_size)
            output_canvas.drawString(line.x, line.y - section_offset,
                                    str(line.get_text()).replace(".", "").replace("'",
                                    "").replace(",", "").replace(original_producer, new_producer))
        elif match_deal_id:  # deal id
            output_canvas.setFont(line.font_name, line.font_size)
            if str(invoice_name[:+config.DEAL_ID_LENGTH]) == str(invoice_name[18:-4]):
                output_canvas.drawString(line.x, line.y - section_offset, invoice_name[18:-4])
            else:
                output_canvas.drawString(line.x, line.y - section_offset, invoice_name[:+config.DEAL_ID_LENGTH] +
                                         invoice_name[15:-4])
        elif invoice_name != '':  # Invoice adjustment
            match = re.search(config.INVOICE_PATTERN, str(line.get_text()))
            if match:
                output_canvas.setFont(line.font_name, line.font_size - 7)
                output_canvas.drawString(line.x, line.y - section_offset - 7, "INVOICE : " +
                                         invoice_name + additional_r)
            else:
                output_canvas.setFont(line.font_name, line.font_size)
                output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
        else:
            output_canvas.setFont(line.font_name, line.font_size)
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())

        final_y = line.y - section_offset

    return final_y


def print_section_with_update_and_get_total_commission(section: list, output_canvas: canvas.Canvas,
                                                       text_to_be_added: str, expected_phrase: str,
                                                       start_y: float = 0) -> list:
    """
        function print section to canvas with adjustment for reference information
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param text_to_be_added: to be appeared on new document
        :param expected_phrase: text to be recognized in line; to this text function add
         text_text_to_be_added
        :param start_y: vertical start position
        :return: list (float, float, string)
   """

    if not section:
        return start_y, float(0.00), "$0.00",
    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = section[0].y

    final_y = 0

    section_offset = 0
    if start_y != 0:
        section_offset = section_start_y - start_y + gap_between_paragraphs

    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs
    total_commission_recognized = False
    for line in section:
        output_canvas.setFont(line.font_name, line.font_size)
        if expected_phrase.upper() in str(line.get_text()).upper():
            output_canvas.drawString(line.x, line.y - section_offset,
                                     expected_phrase + " " + text_to_be_added)
        else:
            if "CHARGE DESCRIPTION" in str(line.get_text()).upper():
                # Draw the background rectangle
                output_canvas.setFillColor(colors.yellowgreen)
                output_canvas.rect(line.x, line.y - section_offset - 2, config.RECTANGLE_WIDTH, 13, fill=1, stroke=0)
                output_canvas.setFillColorRGB(0, 0, 0)  # back to black
            output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
            if total_commission_recognized:
                total_commission = line.get_text()
        if "Total Commission".upper() in str(line.get_text()).upper():
            total_commission_recognized = True
        final_y = line.y - section_offset

    return final_y, float(total_commission.replace("$", "").replace(",", "")), total_commission


def preparing_one_cc_section_and_get_total_commission(section: list, output_canvas: canvas.Canvas,
                                                      text_to_be_added: str, expected_phrase: str,
                                                      start_y: float = 0) -> list:
    """
        function print only one cc section to canvas with adjustment if both cc section are similar
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param text_to_be_added: to be appeared on new document
        :param expected_phrase: text to be recognized in line; to this text function add
         text_text_to_be_added
        :param start_y: vertical start position
        :return: list (float, float, string)
   """

    if not section:
        return start_y, float(0.00), "$0.00",
    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = section[0].y

    final_y = 0

    section_offset = 0
    if start_y != 0:
        section_offset = section_start_y - start_y + gap_between_paragraphs

    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs
    total_commission_recognized = False
    comm_percentage_recognized = False
    for line in section:
        output_canvas.setFont(line.font_name, line.font_size)
        if expected_phrase.upper() in str(line.get_text()).upper():
            # draw string
            output_canvas.drawString(line.x, line.y - section_offset,
                                     expected_phrase + " " + text_to_be_added)
        else:
            if "%" in str(line.get_text()).upper() and "COMM" not in str(line.get_text()).upper():
                comm_percentage = str(line.get_text()).replace("%", "")
                comm_percentage = float(comm_percentage.replace("$", "").replace(",", ""))
                comm_percentage = utils.get_final_total(comm_percentage, comm_percentage, False)
                comm_percentage = comm_percentage.replace("$", "") + "%"
                output_canvas.drawString(config.X_POSITION_COMM_PERCENTAGE - output_canvas.stringWidth(comm_percentage),
                                         line.y - section_offset, comm_percentage)
                comm_percentage_recognized = True
            elif comm_percentage_recognized:
                commission_amount = line.get_text()
                commission_amount = float(commission_amount.replace("$", "").replace(",", ""))
                commission_amount = utils.get_final_total(commission_amount, commission_amount, False)
                output_canvas.drawString(config.X_POSITION_COMMISION - output_canvas.stringWidth(commission_amount),
                                         line.y - section_offset, commission_amount)
                comm_percentage_recognized = False
            elif total_commission_recognized:
                total_commission = line.get_text()
                total_commission = float(total_commission.replace("$", "").replace(",", ""))
                total_commission = utils.get_final_total(total_commission, total_commission, False)
                output_canvas.drawString(config.X_POSITION_COMMISION - output_canvas.stringWidth(total_commission),
                                         line.y - section_offset, total_commission)
                total_commission_recognized = False
            else:
                if "CHARGE DESCRIPTION" in str(line.get_text()).upper():
                    # Draw the background rectangle
                    output_canvas.setFillColor(colors.yellowgreen)
                    output_canvas.rect(line.x, line.y - section_offset - 2, config.RECTANGLE_WIDTH,
                                       13, fill=1, stroke=0)
                    output_canvas.setFillColorRGB(0, 0, 0)  # back to black

                output_canvas.drawString(line.x, line.y - section_offset, line.get_text())

        if "Total Commission".upper() in str(line.get_text()).upper():
            total_commission_recognized = True

        final_y = line.y - section_offset

    return final_y, float(total_commission.replace("$", "").replace(",", "")), total_commission


def print_section_with_update_and_get_total_invoice_due(section: list, output_canvas: canvas.Canvas,
                                                        text_to_be_added: str, expected_phrase: str,
                                                        start_y: float, first: bool,
                                                        first_total_invoice_due_amount: float = 0) -> list:
    """
        function print section to canvas with adjustment for reference information
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param text_to_be_added: to be appeared on new document
        :param expected_phrase: text to be recognized in line; to this text function add
         text_text_to_be_added
        :param start_y: vertical start position
        :param first: true - data from first document, false, data from second one
        :param first_total_invoice_due_amount - total amount from first document
        :return: list(float, float)
   """

    if not section:
        return start_y, float(0.00)
    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    section_start_y = section[0].y

    final_y = 0

    section_offset = 0
    if start_y != 0:
        if first:
            section_offset = section_start_y - start_y + gap_between_paragraphs
        else:
            section_offset = section_start_y - start_y - 25
    if section[-1].y - section_offset < page_top_bottom_margin:
        output_canvas.showPage()
        start_y = Invoice.page_height - page_top_bottom_margin
        section_offset = section_start_y - start_y + gap_between_paragraphs

    total_invoice_due = False
    if first:
        start_printing = True
    else:
        start_printing = False
    for line in section:
        if "Due Date".upper() in str(line.get_text()).upper() and first:
            # Draw the background rectangle
            output_canvas.setFillColor(colors.yellowgreen)
            output_canvas.rect(line.x, line.y - section_offset - 1, config.RECTANGLE_WIDTH, 9, fill=1, stroke=0)
            output_canvas.setFillColorRGB(0, 0, 0)  # back to black
        if total_invoice_due:
            total_invoice_due_amount = str(line.get_text())
            if first:
                final_y = line.y - section_offset
                return final_y, float(total_invoice_due_amount.replace("$", "").replace(",", ""))
            else:
                first_total_invoice_due_amount = (first_total_invoice_due_amount +
                                                  float(total_invoice_due_amount.replace("$", "").replace(",", "")))
        if expected_phrase.upper() in str(line.get_text()).upper() and start_printing:
            output_canvas.setFont(line.font_name, line.font_size)
            output_canvas.drawString(line.x, line.y - section_offset,
                                     expected_phrase + " " + text_to_be_added)

        else:
            if "Total Invoice Due".upper() in str(line.get_text()).upper() and first:
                pass
            else:
                if start_printing:
                    output_canvas.setFont(line.font_name, line.font_size)
                    if not total_invoice_due:
                        output_canvas.drawString(line.x, line.y - section_offset, line.get_text())
                    else:
                        output_canvas.drawString(config.SUMMARY_X_POSITION_INVOICE_DETAIL -
                                                 output_canvas.stringWidth('$' +
                                                 str("{:,.2f}".format(first_total_invoice_due_amount))),
                                                 line.y - section_offset,
                                                 '$' + str("{:,.2f}".format(first_total_invoice_due_amount)))
                        total_invoice_due = False
        if "Total Invoice Due".upper() in str(line.get_text()).upper():
            total_invoice_due = True
        if "Amount Due".upper() in str(line.get_text()).upper() and not first:
            start_printing = True

        final_y = line.y - section_offset

    return final_y, float(total_invoice_due_amount.replace("$", "").replace(",", ""))


def get_requested_value_from_list(section: list, expected_phrase: str, number_of_items_after: int) -> str:
    """
        function gets value of list item which position is determined by passed phrase and passed expected
        missed list items
        :param section: list including rows of section
        :param expected_phrase: self-explanatory
        :param number_of_items_after: it determines how many elements look up phrase is after expected_phrase
        :return: str
   """
    recognized_text = 0
    found_text = False
    for line in section:
        if recognized_text == number_of_items_after:
            requested_text = line.get_text()
            return requested_text
        if found_text:
            recognized_text += 1
        if expected_phrase.upper() in str(line.get_text()).upper():
            recognized_text += 1
            found_text = True
    return str(number_of_items_after)  # of not recognized treat as another values fount


def print_section_with_update(section: list, output_canvas: canvas.Canvas,
                              text_to_be_added: str, expected_phrase: str,
                              start_y: float = 0, y_type="y") -> float:
    """
        function print section to canvas with adjustment for reference information
        :param section: list including rows of section
        :param output_canvas: self-explanatory
        :param text_to_be_added: to be appeared on new document
        :param expected_phrase: text to be recognized in line; to this text function add
         text_text_to_be_added
        :param start_y: vertical start position
        :param y_type: y or y1
        :return: float
   """

    if not section:
        return start_y
    page_top_bottom_margin = 66
    gap_between_paragraphs = 30
    if y_type == "y":
        section_start_y = section[0].y
    else:
        section_start_y = section[0].y1

    final_y = 0

    section_offset = 0
    if start_y != 0:
        section_offset = section_start_y - start_y + gap_between_paragraphs
    if y_type == "y":
        if section[-1].y - section_offset < page_top_bottom_margin:
            output_canvas.showPage()
            start_y = Invoice.page_height - page_top_bottom_margin
            section_offset = section_start_y - start_y + gap_between_paragraphs
    else:
        if section[-1].y1 - section_offset < page_top_bottom_margin:
            output_canvas.showPage()
            start_y = Invoice.page_height - page_top_bottom_margin
            section_offset = section_start_y - start_y + gap_between_paragraphs

    offset_additional = 0
    for line in section:
        if expected_phrase.upper() in str(line.get_text()).upper():
            output_canvas.setFont(line.font_name, line.font_size)
            output_canvas.drawString(line.x, line.y - section_offset - offset_additional,
                                     expected_phrase + " " + text_to_be_added)
        else:
            output_canvas.setFont(line.font_name, line.font_size)
            output_canvas.drawString(line.x, line.y - section_offset - offset_additional, line.get_text())

        final_y = line.y - section_offset

    return final_y


def create_pdf_file(inv1: str, inv2: str, output_folder: str, logo_path: str, revision: int) -> str:
    """
         function create new pdf file merging file from path inv1 and from path inv2
         :param inv1: full path of first pdf
         :param inv2: full path of second pdf
         :param output_folder: path of folder where new pdf file will be created
         :param logo_path: string representing path of logo file
         :param revision: 1 = tickbox marked, 0 means tickbox unmarked
         :return: str
    """
    (lines,  page_height, page_width) = read_invoice(inv1, 1)
    lines2 = read_invoice(inv2, 1)[0]
    lines2_page2 = read_invoice(inv2, 2)[0]
    first_invoice_name = utils.get_invoice_number(lines)
    second_invoice_name = utils.get_invoice_number(lines2)
    final_invoice_name = utils.combine_invoice_names_in_one_name(first_invoice_name, second_invoice_name)
    first_producer_name = utils.get_producer_name(lines)
    second_producer_name = utils.get_producer_name(lines2)
    producer_name = utils.merge_string_if_not_equal(first_producer_name, second_producer_name)
    to_write1: list[LTTextLineHorizontal] = sort_invoice(lines, page_height)
    to_write2: list[LTTextLineHorizontal] = sort_invoice(lines2, page_height)
    to_write2_page2: list[LTTextLineHorizontal] = lines2_page2
    if revision == 1:
        output_filename = f"{final_invoice_name}R.pdf"
    else:
        output_filename = f"{final_invoice_name}.pdf"
    canvas_name = os.path.join(output_folder, "TEMP" + output_filename)
    c = canvas.Canvas(canvas_name, pagesize=(page_width, page_height))
    logo = ImageReader(logo_path)

    c.drawImage(logo, 40, page_height - 70, width=80, height=20)

    invoice1_sectioned = section_invoice(to_write1)
    invoice2_sectioned = section_invoice(to_write2)

    dict_check_date = {}
    dicthistory = utils.collect_history_details(invoice1_sectioned.deal_pmt_history, dict_check_date)
    dicthistory = utils.collect_history_details(invoice2_sectioned.deal_pmt_history, dict_check_date)

    invoice2_sectioned_page2 = section_invoice(to_write2_page2, 2)
    total_consideration1 = get_requested_value_from_list(invoice1_sectioned.cc_calc, "Total Consideration", 1)
    total_consideration2 = get_requested_value_from_list(invoice2_sectioned.cc_calc, "Total Consideration", 1)
    due_date1 = get_requested_value_from_list(invoice1_sectioned.inv_detail, "Amount Due", 1)
    due_date2 = get_requested_value_from_list(invoice2_sectioned.inv_detail, "Amount Due", 1)
    description1 = get_requested_value_from_list(invoice1_sectioned.inv_detail, "Amount Due", 2)
    description2 = get_requested_value_from_list(invoice2_sectioned.inv_detail, "Amount Due", 2)
    print_section_with_adjustments(invoice1_sectioned.header, c, final_invoice_name, first_producer_name,
                                   producer_name, revision)
    if total_consideration1 == total_consideration2 and due_date1 == due_date2 and description1 == description2:
        returned_list = preparing_one_cc_section_and_get_total_commission(invoice1_sectioned.cc_calc, c,
                                                                          first_invoice_name[:+config.DEAL_ID_LENGTH],
                                                                          config.CONSIDERATION_COMMISSION)
        total_commission_float = returned_list[1]
        total_commission = returned_list[2]
    else:
        returned_list = print_section_with_update_and_get_total_commission(invoice1_sectioned.cc_calc, c,
                                                                           first_invoice_name[:+config.DEAL_ID_LENGTH],
                                                                           config.CONSIDERATION_COMMISSION)
        total_commission = returned_list[1]
        total_commission_float = total_commission
        returned_list = print_section_with_update_and_get_total_commission(invoice2_sectioned.cc_calc, c,
                                                                           second_invoice_name[:+config.DEAL_ID_LENGTH],
                                                                           config.CONSIDERATION_COMMISSION,
                                                                           returned_list[0])
        total_commission_float = total_commission_float + returned_list[1]
        total_commission = utils.get_final_total(total_commission, returned_list[1], False)

    returned_list = print_section_with_update_and_get_total_invoice_due(invoice1_sectioned.inv_detail, c,
                                                                        first_invoice_name[:+config.DEAL_ID_LENGTH] +
                                                                        " & "
                                                                        + second_invoice_name[:+config.DEAL_ID_LENGTH],
                                                                        config.INVOICE_DETAIL, returned_list[0], True)
    total_invoice_due = returned_list[1]
    returned_list = print_section_with_update_and_get_total_invoice_due(invoice2_sectioned.inv_detail, c,
                                                                        second_invoice_name[:+config.DEAL_ID_LENGTH],
                                                                        config.INVOICE_DETAIL, returned_list[0], False,
                                                                        total_invoice_due)
    total_invoice_due = total_invoice_due + returned_list[1]
    '''returned_list = print_history_and_get_value(dicthistory, invoice1_sectioned.deal_pmt_history, c, 
                                                first_invoice_name,
                                                second_invoice_name, True, returned_list[0])'''
    returned_list = print_history_and_get_values(invoice1_sectioned.deal_pmt_history, dicthistory, dict_check_date,
                                                 c, returned_list[0])

    total_payment_received = returned_list[1]
    amount_already_paid = returned_list[2]
    total_payment_received_float = total_payment_received
    y = returned_list[0]
    '''returned_list = print_history_and_get_value(dicthistory, invoice2_sectioned.deal_pmt_history, c,
                                            first_invoice_name,
                                                second_invoice_name, False, returned_list[0])'''
    '''total_payment_received_float = total_payment_received_float + returned_list[1]

    y = returned_list[0]
    amount_already_paid = -1 * (amount_already_paid + returned_list[2])'''

    total_invoice_due = utils.get_final_total(total_invoice_due, -1 * amount_already_paid, False)
    remaining_balance_due = utils.get_final_total(total_commission_float, -1 * total_payment_received_float, False)
    total_payment_received = utils.get_final_total(total_payment_received_float, 0, True)

    y = print_section_and_adjust_comment_section(invoice1_sectioned.comments_summary, total_invoice_due,
                                                 total_commission, remaining_balance_due, total_payment_received, c, y)
    if len(invoice2_sectioned.remittance) > 0:
        print_section_with_update(invoice2_sectioned.remittance, c, final_invoice_name,
                                  config.REFERENCE_INFORMATION,  y)
    else:
        print_section_with_update(invoice2_sectioned_page2.remittance, c, final_invoice_name,
                                  config.REFERENCE_INFORMATION, y)

    c.save()
    utils.add_number_of_pages(canvas_name, output_folder, output_filename)

    os.remove(canvas_name)

    if len(invoice2_sectioned_page2.remittance) == 0:
        final_message = config.FINAL_MESSAGE
    else:
        final_message = config.FINAL_MESSAGE_2_PAGES
    return final_message
