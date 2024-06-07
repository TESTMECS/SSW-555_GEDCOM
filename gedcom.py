import re

valid_tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

individuals = {}
families = {}

def process_gedcom(file_path):
    current_individual = None
    current_family = None
    
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
                if re.match(r'@I\d+@', tag):
                    current_individual = tag
                    individuals[current_individual] = {'id': tag, 'name': None}
                elif re.match(r'@F\d+@', tag):
                    current_family = tag
                    families[current_family] = {'id': tag, 'husband': None, 'wife': None}
                else:
                    current_individual = None
                    current_family = None
            elif level == '1' and current_individual and tag == 'NAME':
                individuals[current_individual]['name'] = arguments
            elif level == '1' and current_family:
                if tag == 'HUSB':
                    families[current_family]['husband'] = arguments
                elif tag == 'WIFE':
                    families[current_family]['wife'] = arguments

def print_individuals_and_families(output_file):
    sorted_individuals = sorted(individuals.values(), key=lambda x: x['id'])
    sorted_families = sorted(families.values(), key=lambda x: x['id'])
    
    with open(output_file, 'w') as f:
        f.write("\nIndividuals:\n")
        for ind in sorted_individuals:
            f.write(f"ID: {ind['id']}, Name: {ind['name']}\n")
        
        f.write("\nFamilies:\n")
        for fam in sorted_families:
            husband_name = individuals[fam['husband']]['name'] if fam['husband'] in individuals else "Unknown"
            wife_name = individuals[fam['wife']]['name'] if fam['wife'] in individuals else "Unknown"
            f.write(f"Family ID: {fam['id']}, Husband: {husband_name}, Wife: {wife_name}\n")

# Prompt for the GEDCOM file path
file_path = input("Please enter the path to the GEDCOM file: ")

# Process the GEDCOM file
process_gedcom(file_path)

# Prompt for the output file path
output_file_path = input("Please enter the path for the output file: ")

# Write individuals and families to the output file
print_individuals_and_families(output_file_path)
