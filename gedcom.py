import re
import sys
print(sys.executable)

from prettytable import PrettyTable
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
            if individual.get('death_date') is None:
                continue
            death_date = parse_date(individual['death_date'])
            if birth_date and death_date and birth_date >= death_date:
                print(f"ERROR: Individual: US06 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is not earlier than death date {individual['death_date']}.")

    # US01 check all dates are before current date
    def check_dates_before_current():
        for individual in individuals.values():
            current_date = datetime.now()
            birth_date = parse_date(individual['birthday'])
            if individual.get('death_date') is None: continue
            death_date = parse_date(individual['death_date'])
            if birth_date and birth_date > current_date:
                print(f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is after the current date.")
            if death_date and death_date > current_date:
                print(f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Death date {individual['death_date']} is after the current date.")
        for family in families.values():
            if family.get('marriage_date') is None: continue
            current_date = datetime.now()
            marriage_date = parse_date(family.get('marriage_date'))
            if family.get('divorce_date') is None: continue
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
                        print(f"ERROR: US08: Individual: {individuals[child_id]['name']} ({child_id}): has birth date before the marriage of parents.")
        return None
    #US02 Birth before marriage of individual
    def check_birth_before_marriage():
        for individual in individuals.values():
            birth_date = individual.get('birthday')
            if not birth_date:
                continue
            birth_date = parse_date(birth_date)
            marriage_date = individual.get('marriage_date')
            if marriage_date:
                marriage_date = parse_date(marriage_date)
                if birth_date > marriage_date:
                    print(f"ERROR: US02: Individual: {individual['name']} ({individual['id']}): has birth date after marriage date.")

    #US09: Birth before death of parents
    def check_birth_before_death_parents():
        # child should be born before the death of the mother and before 9 months after the death of the father
        for family in families.values():
            mother_id = family.get('wife')
            father_id = family.get('husband')
            for child_id in family.get('children', []):
                if child_id in individuals:
                    child = individuals[child_id]
                    birth_date = child.get('birthday')
                    if not birth_date:
                        continue
                    birth_date = parse_date(birth_date) # child birthday
                    death_date_mother = individuals[mother_id].get('death_date')
                    death_date_father = individuals[father_id].get('death_date')
                    if death_date_mother:
                        death_date_mother = parse_date(death_date_mother)
                        if birth_date > death_date_mother:
                            print(f"ERROR: US09: Individual: {individuals[child_id]['name']} ({child_id}): has birth date before death date of mother.")
                    if death_date_father:
                        death_date_father = parse_date(death_date_father)
                        nine_months_after = death_date_father + datetime.timedelta(days=90)
                        if birth_date > nine_months_after:
                            print(f"ERROR: US09: Individual: {individuals[child_id]['name']} ({child_id}): has birth date before 9 months after death date of father.")
    # US10
    def check_marriage_after_14():
        # Marriage should be after 14 years of age
        for family in families.values():
            marriage_date = family.get('marriage_date')
            if not marriage_date:
                continue
            marriage_date = parse_date(marriage_date)
            mother_id = family.get('wife')
            father_id = family.get('husband')
            if mother_id in individuals and father_id in individuals:
                birth_date_mother = individuals[mother_id].get('birthday')
                birth_date_father = individuals[father_id].get('birthday')
                if birth_date_mother:
                    birth_date_mother = parse_date(birth_date_mother)
                    mother_comparison = birth_date_mother + relativedelta(years=14)
                    if marriage_date < mother_comparison:
                        print(f"ERROR: US10: Family: {family['id']}: has marriage date before 14 years of age of mother.")
                if birth_date_father:
                    birth_date_father = parse_date(birth_date_father)
                    father_comparison = birth_date_father + relativedelta(years=14)
                    if marriage_date < father_comparison:
                        print(f"ERROR: US10: Family: {family['id']}: has marriage date before 14 years of age of father.")
    #US12
    def mother_too_old():
        # Mother should be less than 60 years old compared to her children
        for family in families.values():
            mother_id = family.get('wife')
            for child_id in family.get('children', []):
                if child_id in individuals:
                    child = individuals[child_id]
                    birth_date = child.get('birthday')
                    if not birth_date:
                        continue
                    birth_date = parse_date(birth_date)
                    if mother_id in individuals:
                        mother = individuals[mother_id]
                        mother_birth_date = mother.get('birthday')
                        if mother_birth_date:
                            mother_birth_date = parse_date(mother_birth_date)
                            age = relativedelta(mother_birth_date, birth_date).years
                            if age > 60:
                                print(f"ERROR: US12: Family: {family['id']}: has mother too old.")
    #US13
    def siblings_spacing():
        # Sibling birth should be more than 8 months apart
        for family in families.values():
            for child_id in family.get('children', []):
                if child_id in individuals:
                    child = individuals[child_id]
                    birth_date = child.get('birthday')
                    if not birth_date:
                        continue
                    birth_date = parse_date(birth_date)
                    for sibling_id in family.get('children', []):
                        if sibling_id in individuals and sibling_id != child_id:
                            sibling = individuals[sibling_id]
                            sibling_birth_date = sibling.get('birthday')
                            if sibling_birth_date:
                                sibling_birth_date = parse_date(sibling_birth_date)
                                age = relativedelta(sibling_birth_date, birth_date).months
                                if age < 8:
                                    print(f"ERROR: US13: Family: {family['id']}: has sibling too young.")
    #US14
    def multiple_births():
        # No more than 5 siblings should have the same birthday
        for family in families.values():
            for child_id in family.get('children', []):
                if child_id in individuals:
                    child = individuals[child_id]
                    birth_date = child.get('birthday')
                    if not birth_date:
                        continue
                    birth_date = parse_date(birth_date)
                    for sibling_id in family.get('children', []):
                        if sibling_id in individuals and sibling_id != child_id:
                            sibling = individuals[sibling_id]
                            sibling_birth_date = sibling.get('birthday')
                            if sibling_birth_date:
                                sibling_birth_date = parse_date(sibling_birth_date)
                                if birth_date == sibling_birth_date:
                                    print(f"ERROR: US14: Family: {family['id']}: has multiple births.")
    # US 16
    def check_wife_last_name():
        for family in families.values():
            husband_id = family.get('husband')
            wife_id = family.get('wife')
            if husband_id in individuals and wife_id in individuals:
                husband_name = individuals[husband_id]['name']
                wife_name = individuals[wife_id]['name']
                husband_last_name = husband_name.split('/')[-1].strip() if '/' in husband_name else husband_name.split()[-1]
                wife_last_name = wife_name.split('/')[-1].strip() if '/' in wife_name else wife_name.split()[-1]
                if husband_last_name != wife_last_name:
                    print(f"ERROR: Family: {family['id']}: Wife {wife_name} ({wife_id}) does not have the same last name as husband {husband_name} ({husband_id}).")

    # US15 Check if there are more than 15 siblings
    def check_siblings_count():
        for family in families.values():
            if len(family['children']) > 15:
                print(f"ERROR: Family: US15 {family['id']} has more than 15 siblings.")





    # Call functions
    #US04
    check_marriage_before_divorce()
    #US05
    check_marriage_before_death()
    #US03
    check_birth_before_death()
    #US01
    check_dates_before_current()
    #US06
    check_divorce_before_death()
    #US08
    check_birth_before_parents_marriage()
    #US02
    check_birth_before_marriage()
    #US09
    check_birth_before_death_parents()
    #US10
    check_marriage_after_14()
    #US12
    mother_too_old()
    #US13
    siblings_spacing()
    #US14
    multiple_births()
    #US15
    check_siblings_count()
    #US16
    check_wife_last_name()
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
