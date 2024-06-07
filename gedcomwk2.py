import re
from tkinter import Tk, filedialog

def gedcom_test(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            print(f"--> {line}")
            match = re.match(r'^(\d+)\s+(\S+)(?:\s+(.*))?', line)
            if match:
                level, tag, arguments = match.groups()
                valid_tags = {'INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM',
                              'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TRLR', 'NOTE'}
                is_valid = 'Y' if tag in valid_tags else 'N'
                print(f"<-- {level}|{tag}|{is_valid} : {arguments if arguments else ''}")
            else:
                print("<-- Invalid GEDCOM line")

def select_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("GEDCOM files", "*.ged"), ("All files", "*.*")])
    if file_path:
        gedcom_test(file_path)

select_file()
