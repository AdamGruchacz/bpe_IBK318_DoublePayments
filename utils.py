import re
import config
import os
import fitz  # PyMuPDF


def combine_invoice_names_in_one_name(invoice1st: str, invoice2nd: str) -> str:
    """
         function recognizes which invoice number is lower and then combine both of them using  & character.
         First in the name need be lower number of invoice
         :param invoice1st: string representing first invoice name
         :param invoice2nd: string representing second invoice name
         :return: str
        """
    invoice1st_cleaned = invoice1st.replace("-", "")
    invoice2nd_cleaned = invoice2nd.replace("-", "")
    if invoice2nd_cleaned > invoice1st_cleaned:
        return invoice1st + " & " + invoice2nd
    else:
        return invoice2nd + " & " + invoice1st


def get_invoice_number(lst: list) -> str:
    """
     function recognized invoice name in passed list.
     :param lst: including lines of documents
     :return: str
    """

    for element in lst:

        pattern = config.INVOICE_PATTERN  # r'(?<=INVOICE : )[\d-]+'
        match = re.search(pattern, str(element))
        if match:
            invoice_number = match.group()
            return invoice_number
        else:
            return "invoice not recognized"


def get_producer_name(lst: list) -> str:
    """
     function recognized producer name in passed list.
     corresponding producer name is 2 elements further than phrase 'Producer Name'
     :param lst: including lines of documents
     :return: str
    """

    counter = 0
    for element in lst:
        line_text = str(element)
        line_text = line_text.replace('\\', "")
        line_text = line_text.replace("'", "")
        line_text = line_text.replace("n>", "")
        line_text = line_text.replace("<LTTextLineHorizontal ", "")
        line_text = line_text.replace(".", "")
        line_text = line_text.replace(",", "")
        line_text = re.sub(r"\d", "", line_text)  # remove digits
        line_text = re.sub(r"^\s+", "", line_text)  # remove spaces before first another character

        has_small_letter = False
        if "Producer Name" in str(element):
            counter = 1
        elif counter > 0:
            counter += 1
            if counter == 2 and "Bill To:" in str(element):
                break
            for char in line_text:
                if char.islower():
                    has_small_letter = True
                    break
        if has_small_letter:
            return line_text

    for element in reversed(lst):  # if section in pdf in different way
        if "DEAL INFORMATION" in str(element):
            counter = 1
        elif counter > 0:
            counter += 1
        if counter == 2:
            producer_line = str(element)
            producer_line = producer_line.replace('\\', "")
            producer_line = producer_line.replace("'", "")
            producer_line = producer_line.replace("n>", "")
            producer_line = producer_line.replace("<LTTextLineHorizontal ", "")
            producer_line = producer_line.replace(".", "")
            producer_line = producer_line.replace(",", "")
            producer_line = re.sub(r"\d", "", producer_line)  # remove digits
            producer_line = re.sub(r"^\s+", "", producer_line)  # remove spaces before first another character
            return producer_line


def merge_string_if_not_equal(first_string: str, second_string: str) -> str:
    """
         function merge string if not equals.
         :param first_string: self-explanatory
         :param second_string: self-explanatory
         :return: str
    """
    if first_string == second_string:
        return first_string
    else:
        return first_string + "," + second_string


def get_final_total(first_amount: float, second_amount: float, minus_sign: bool) -> str:
    """
        function sum two values and convert to string format where each 3 digits seperated by comma
        format with sign minus and after dolar character
        :param first_amount: self-explanatory
        :param second_amount: self-explanatory
        :param minus_sign: true if final value to be multiply by minus one
        :return: str
   """
    total_payment_received = first_amount + second_amount
    if minus_sign:
        total_payment_received = '-$' + str("{:,.2f}".format(total_payment_received))
    else:
        total_payment_received = '$' + str("{:,.2f}".format(total_payment_received))
    return total_payment_received


def add_number_of_pages(canvas_name: str, output_folder: str, output_filename: str) -> None:
    """
       function print number of page  - including number of all pages - in bottom right corner
       :param canvas_name: input pdf full path
       :param output_folder: oath of folder to save the file
       :param output_filename: self-explanatory
       :return: Nono
  """
    doc = fitz.open(canvas_name)

    # Loop through each page and add the page number
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = f"Page {page_num + 1} of {str(len(doc))}"
        position = fitz.Point(page.rect.width - 65, page.rect.height - 20)  # Adjust position as needed
        page.insert_text(position, text, fontsize=9, color=(0, 0, 0))

    # Save the modified PDF
    doc.save(os.path.join(output_folder, output_filename))
    doc.close()


def collect_history_details(section: list, dict_check_date: dict) -> dict:
    """
    function assigns to dictionary aggregated = by check and date - details of history section
    :param section: list of deal payment history section
    :param dict_check_date: dictionary including details from section, key is check + " " + date
    return: dictionary
    """
    collecting = False
    line_collected = False
    check = ""
    payment_received_date = ""
    invoice = ""
    payment_received_amount = ""
    for line in section:
        if line_collected:
            if not check + "_" + payment_received_date in dict_check_date.keys():
                dict_check_date[check + "_" + payment_received_date] = \
                    [payment_received_date, check, invoice,
                        float(payment_received_amount.replace("$", "").replace(",", ""))]
            elif check + "_" + payment_received_date in dict_check_date.keys():
                dict_item = dict_check_date[check + "_" + payment_received_date]
                payment_amount_updated = dict_item[3] + float(payment_received_amount.replace("$", "").replace(",", ""))
                dict_check_date[check + "_" + payment_received_date] = \
                    [payment_received_date, check, dict_item[2] + " & " + invoice, payment_amount_updated]
            line_collected = False
        if "/" in str(line.get_text()) and collecting:
            payment_received_date = str(line.get_text())
        elif "-" in str(line.get_text()) and collecting:
            invoice = str(line.get_text())
        elif "$" in str(line.get_text()) and collecting:
            payment_received_amount = str(line.get_text())
            line_collected = True
        elif "Payment Received".upper() in str(line.get_text()).upper():
            collecting = True
        elif collecting:
            check = str(line.get_text())

    return dict_check_date
