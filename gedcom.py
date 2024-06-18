import re
import sys
print(sys.executable)

from prettytable import PrettyTable
from datetime import datetime

valid_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

individuals = {}
families = {}

def parse_date(date_str):
    for date_format in ("%d %b %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass
    return None

def process_gedcom(file_path):
    current_individual = None
    current_family = None
    current_date_tag = None

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            print(f"--> {line}")

            parts = line.split(' ', 2)
            level = parts[0]
            tag = parts[1]
            arguments = parts[2] if len(parts) > 2 else ""

            is_valid = "Y" if tag in valid_tags else "N"
            print(f"<-- {level}|{tag}|{is_valid} : {arguments}")

            if level == '0':
                current_date_tag = None
                if re.match(r'@I\d+@', tag):
                    current_individual = tag
                    individuals[current_individual] = {'id': tag, 'name': None, 'sex': None, 'birthday': None, 'child': None, 'spouse': None}
                elif re.match(r'@F\d+@', tag):
                    current_family = tag
                    families[current_family] = {'id': tag, 'husband': None, 'wife': None, 'children': []}
                else:
                    current_individual = None
                    current_family = None
            elif level == '1':
                current_date_tag = None
                if current_individual:
                    if tag == 'NAME':
                        individuals[current_individual]['name'] = arguments
                    elif tag == 'SEX':
                        individuals[current_individual]['sex'] = arguments
                    elif tag == 'BIRT':
                        current_date_tag = 'birthday'
                    elif tag == 'FAMC':
                        individuals[current_individual]['child'] = arguments
                    elif tag == 'FAMS':
                        individuals[current_individual]['spouse'] = arguments
                    elif tag == 'DEAT':
                        current_date_tag = 'death_date'
                if current_family:
                    if tag == 'HUSB':
                        families[current_family]['husband'] = arguments
                    elif tag == 'WIFE':
                        families[current_family]['wife'] = arguments
                    elif tag == 'CHIL':
                        families[current_family]['children'].append(arguments)
                    elif tag == "MARR":
                        current_date_tag = 'marriage_date'
                    elif tag == "DIV":
                        current_date_tag = 'divorce_date'
            elif level == '2' and current_date_tag:
                if tag == 'DATE':
                    if current_individual:
                        individuals[current_individual][current_date_tag] = arguments
                    if current_family:
                        families[current_family][current_date_tag] = arguments

def print_individuals_and_families(output_file):
    sorted_individuals = sorted(individuals.values(), key=lambda x: x['id'])
    sorted_families = sorted(families.values(), key=lambda x: x['id'])

    with open(output_file, 'w') as f:
        f.write("Individuals:\n")
        ind_table = PrettyTable(["ID", "Name", "Gender", "Birthday", "Child", "Spouse"])
        for ind in sorted_individuals:
            ind_table.add_row([ind['id'], ind['name'], ind['sex'], ind['birthday'], ind['child'], ind['spouse']])
        f.write(ind_table.get_string())
        f.write("\n\nFamilies:\n")
        fam_table = PrettyTable(["Family ID", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"])
        for fam in sorted_families:
            husband_name = individuals[fam['husband']]['name'] if fam['husband'] in individuals else "Unknown"
            wife_name = individuals[fam['wife']]['name'] if fam['wife'] in individuals else "Unknown"
            children_ids = ', '.join(fam['children'])
            fam_table.add_row([fam['id'], fam['husband'], husband_name, fam['wife'], wife_name, children_ids])
        f.write(fam_table.get_string())


def check_anomalies():
    # US04 check marriage before divorce
    def check_marriage_before_divorce():
        for individual in individuals.values():
            family = individual['spouse']
            try:
                marriage_date = families[family]['marriage_date']
            except KeyError:
                continue
            try:
                divorce_date = families[family]['divorce_date']
            except KeyError:
                continue
            marriage_date = parse_date(marriage_date)
            divorce_date = parse_date(divorce_date)
            if marriage_date and divorce_date and marriage_date > divorce_date:
                    print( f"ERROR: Individual: US04 {individual['name']}: ({individual['id']}): {marriage_date}: has marriage date after divorce date." )
        return None
    # US05 check marriage before death
    def check_marriage_before_death():
        for individual in individuals.values():

            family = individual['spouse']

            if not family:
               continue
            try:
                marriage_date = families[family]['marriage_date']
            except KeyError:
                continue
            try:
                death_date = individual['death_date']
            except KeyError:
                continue
            marriage_date = parse_date(marriage_date)
            death_date = parse_date(death_date)
            if marriage_date and death_date and marriage_date > death_date:
                print( f"ERROR: Individual: US05 {individual['name']}: ({individual['id']}): {marriage_date}: has marriage date after death date." )
    # US03 check birth before death
    def check_birth_before_death():
        for individual in individuals.values():
            birth_date = parse_date(individual['birthday'])
            death_date = parse_date(individual['death_date'])
            if birth_date and death_date and birth_date >= death_date:
                print(f"ERROR: Individual: US06 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is not earlier than death date {individual['death_date']}.")

    # US01 check all dates are before current date
    def check_dates_before_current():
        for individual in individuals.values():
            birth_date = parse_date(individual['birthday'])
            death_date = parse_date(individual['death_date'])
            if birth_date and birth_date > current_date:
                print(f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is after the current date.")
            if death_date and death_date > current_date:
                print(f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Death date {individual['death_date']} is after the current date.")
        for family in families.values():
            marriage_date = parse_date(family.get('marriage_date'))
            divorce_date = parse_date(family.get('divorce_date'))
            if marriage_date and marriage_date > current_date:
                print(f"ERROR: Family: US07 {family['id']}: Marriage date {family['marriage_date']} is after the current date.")
            if divorce_date and divorce_date > current_date:
                print(f"ERROR: Family: US07 {family['id']}: Divorce date {family['divorce_date']} is after the current date.")

    #US06 Divorce before death    
    def check_divorce_before_death():
    #errors = []
     for family in families.values():
        divorce_date = family.get('divorce_date')
        if not divorce_date:
            continue
        divorce_date = parse_date(divorce_date)
        
        husband_id = family.get('husband')
        wife_id = family.get('wife')
        
        husband_death_date = individuals.get(husband_id, {}).get('death_date')
        wife_death_date = individuals.get(wife_id, {}).get('death_date')
        
        if husband_death_date:
            husband_death_date = parse_date(husband_death_date)
            if divorce_date > husband_death_date:
                #errors.append
                print(f"Error: Family: {family['id']}: has divorce date after husband's death date.")
        
        if wife_death_date:
            wife_death_date = parse_date(wife_death_date)
            if divorce_date > wife_death_date:
                #errors.append
                print(f"Error: Family: {family['id']}: has divorce date after wife's death date.")
                
     return None
#errors
    
    #US08 Birth before marriage of parents
    def check_birth_before_parents_marriage():
       # errors = []
        for family in families.values():
            marriage_date = family.get('marriage_date')
            if not marriage_date:
                continue
            marriage_date = parse_date(marriage_date)
        
        for child_id in family.get('children', []):
            if child_id in individuals:
                birth_date = individuals[child_id].get('birthday')
                if birth_date:
                    birth_date = parse_date(birth_date)
                    if birth_date < marriage_date:
                        #errors.append
                        print(f"Error: Individual: {individuals[child_id]['name']} ({child_id}): has birth date before the marriage of parents.")
        return None 
    
    
    
    # Call functions
    check_marriage_before_divorce()
    check_marriage_before_death()
    check_birth_before_death()
    check_dates_before_current()
# Prompt for the GEDCOM file path
file_path = input("Please enter the path to the GEDCOM file: ")

# Process the GEDCOM file
process_gedcom(file_path)
# Check for anomalies
check_anomalies()


# Prompt for the output file path
output_file_path = input("Please enter the path for the output file: ")

# Write individuals and families to the output file
print_individuals_and_families(output_file_path)
