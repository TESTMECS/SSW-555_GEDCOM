
import unittest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Mock data and functions for testing
def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

individuals = {
    'I1': {'id': 'I1', 'name': 'John Doe', 'birthday': '1980-01-01', 'death_date': None, 'spouse': 'F1', 'sex': 'M'},
    'I2': {'id': 'I2', 'name': 'Jane Doe', 'birthday': '1985-02-02', 'death_date': '2020-02-02', 'spouse': 'F1', 'sex': 'F'},
    'I3': {'id': 'I3', 'name': 'Child1 One', 'birthday': '2010-03-03', 'death_date': None, 'spouse': None, 'sex': 'M'},
    'I4': {'id': 'I4', 'name': 'Child2 Two', 'birthday': '2012-04-04', 'death_date': None, 'spouse': None, 'sex': 'F'},
}

families = {
    'F1': {'id': 'F1', 'husband': 'I1', 'wife': 'I2', 'marriage_date': '2005-01-01', 'divorce_date': '2015-01-01', 'children': ['I3', 'I4']},
}


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
            return f"ERROR: Individual: US04 {individual['name']}: ({individual['id']}): {marriage_date}: has marriage date after divorce date."
    return None

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
            return f"ERROR: Individual: US05 {individual['name']}: ({individual['id']}): {marriage_date}: has marriage date after death date."
    return None

def check_birth_before_death():
    for individual in individuals.values():
        birth_date = parse_date(individual['birthday'])
        if individual.get('death_date') is None:
            continue
        death_date = parse_date(individual['death_date'])
        if birth_date and death_date and birth_date >= death_date:
            return f"ERROR: Individual: US06 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is not earlier than death date {individual['death_date']}."
    return None

def check_dates_before_current():
    for individual in individuals.values():
        current_date = datetime.now()
        birth_date = parse_date(individual['birthday'])
        if individual.get('death_date') is None: continue
        death_date = parse_date(individual['death_date'])
        if birth_date and birth_date > current_date:
            return f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Birth date {individual['birthday']} is after the current date."
        if death_date and death_date > current_date:
            return f"ERROR: Individual: US07 {individual['name']}: ({individual['id']}): Death date {individual['death_date']} is after the current date."
    for family in families.values():
        if family.get('marriage_date') is None: continue
        current_date = datetime.now()
        marriage_date = parse_date(family.get('marriage_date'))
        if family.get('divorce_date') is None: continue
        divorce_date = parse_date(family.get('divorce_date'))
        if marriage_date and marriage_date > current_date:
            return f"ERROR: Family: US07 {family['id']}: Marriage date {family['marriage_date']} is after the current date."
        if divorce_date and divorce_date > current_date:
            return f"ERROR: Family: US07 {family['id']}: Divorce date {family['divorce_date']} is after the current date."

    #US06 Divorce before death
def check_divorce_before_death():
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
                return f"Error: Family: {family['id']}: has divorce date after husband's death date."
        if wife_death_date:
            wife_death_date = parse_date(wife_death_date)
            if divorce_date > wife_death_date:
                return f"Error: Family: {family['id']}: has divorce date after wife's death date."
#US08 Birth before marriage of parents
def check_birth_before_parents_marriage():
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
                    return f"ERROR: US08: Individual: {individuals[child_id]['name']} ({child_id}): has birth date before the marriage of parents."
    return None
#US02 Birth before marriage of individual
def check_birth_before_marriage():
    for individual in individuals.values():
        birth_date = individual.get('birthday')
        if not birth_date:
            continue
        birth_date = parse_date(birth_date)
        individual_family = individual.get('spouse')
        if individual_family is None:
            continue
        marriage_date = families[individual_family].get('marriage_date')
        if marriage_date:
            marriage_date = parse_date(marriage_date)
            if birth_date > marriage_date:
                return f"ERROR: US02: Individual: {individual['name']} ({individual['id']}): has birth date after marriage date."
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
                        return f"ERROR: US09: Individual: {individuals[child_id]['name']} ({child_id}): has birth date after death date of mother."
                if death_date_father:
                    death_date_father = parse_date(death_date_father)
                    nine_months_after = death_date_father + timedelta(days=270)
                    if birth_date > nine_months_after:
                        return f"ERROR: US09: Individual: {individuals[child_id]['name']} ({child_id}): has birth date after 9 months after death date of father."
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
                    return f"ERROR: US10: Family: {family['id']}: has marriage date before 14 years of age of mother."
            if birth_date_father:
                birth_date_father = parse_date(birth_date_father)
                father_comparison = birth_date_father + relativedelta(years=14)
                if marriage_date < father_comparison:
                    return f"ERROR: US10: Family: {family['id']}: has marriage date before 14 years of age of father."
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
                        age = age * -1
                        if age > 60:
                            return f"ERROR: US12: Family: {family['id']}: has mother too old."
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
                            delta = relativedelta(sibling_birth_date, birth_date)
                            age_in_months = delta.years * 12 + delta.months
                            if age_in_months < 0:
                                age_in_months = age_in_months * -1
                            if age_in_months < 8:
                               return f"ERROR: US13: Family: {family['id']}: has sibling too young."
#US14
def multiple_births():
    # No more than 5 siblings should have the same birthday
    count = 0
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
                                count += 1
                                if count > 5:
                                    return f"ERROR: US14: Family: {family['id']}: has multiple births."
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
                return f"ERROR: US16: Family: {family['id']}: Wife {wife_name} ({wife_id}) does not have the same last name as husband {husband_name} ({husband_id})."

# US15 Check if there are more than 15 siblings
def check_siblings_count():
    for family in families.values():
        if len(family['children']) > 15:
            return f"ERROR: Family: US15 {family['id']} has more than 15 siblings."

def check_marriage_to_descendants():
    map = {}
    for family in families.values():
        for child_id in family.get('children', []):
            newlist = []
            if child_id:
                husband_id = family.get('husband')
                wife_id = family.get('wife')
                newlist.append(husband_id)
                newlist.append(wife_id)
                map[child_id] = newlist

    for family in families.values():
        husband_id = family.get('husband')
        wife_id = family.get('wife')
        if husband_id in map:
            if wife_id in map[husband_id]:
                return f"ERROR: US17: Family: {family['id']}: has marriage to descendants."
        if wife_id in map:
            if husband_id in map[wife_id]:
                return f"ERROR: US17: Family: {family['id']}: has marriage to descendants."

# US18
def check_siblings_marriage():
    siblings = []
    husband_sib = False
    wife_sib = False
    for family in families.values():
        newlist = []
        for child_id in family.get('children', []):

            newlist.append(child_id)
        siblings.append(newlist)
        newlist = []
    for family in families.values():
        husband_id = family.get('husband')
        wife_id = family.get('wife')
        for sibling in siblings:
            if husband_id in sibling:
                husband_sib = True
            if wife_id in sibling:
                wife_sib = True
        if husband_sib and wife_sib:
            return f"ERROR: US18: Family: {family['id']}: has siblings married."
        husband_sib = False
        wife_sib = False

def check_no_first_cousin_marriages():
# Create a mapping of individuals to their grandparents
    grandparent_map = {}
    for family in families.values():
        children = family.get('children', [])
        for child in children:
            if child in individuals:
                child_family_id = individuals[child].get('child')
                if child_family_id and child_family_id in families:
                    grandparents = families[child_family_id]
                    grandparent_map[child] = grandparents
    # Identify first cousins
    first_cousin_pairs = set()
    for child1, grandparents1 in grandparent_map.items():
        for child2, grandparents2 in grandparent_map.items():
            if child1 != child2 and grandparents1 == grandparents2:
                first_cousin_pairs.add((child1, child2))
                first_cousin_pairs.add((child2, child1))
    # Check marriages against first cousin pairs

    for family in families.values():
        husband = family.get('husband')
        wife = family.get('wife')
        if (husband, wife) in first_cousin_pairs or (wife, husband) in first_cousin_pairs:
            husband_name = individuals[husband]['name'] if husband in individuals else "Unknown"
            wife_name = individuals[wife]['name'] if wife in individuals else "Unknown"
            return f"ERROR: Family: {family['id']}: First cousins {husband_name} ({husband}) and {wife_name} ({wife}) are married."
def check_no_aunt_uncle_niece_nephew_marriages():
    # Create a mapping of individuals to their parents
    parent_map = {}
    for family in families.values():
        children = family.get('children', [])
        for child in children:
            if child in individuals:
                parent_map[child] = (family.get('husband'), family.get('wife'))

    # Create a set of aunt/uncle to niece/nephew pairs
    aunt_uncle_niece_nephew_pairs = set()
    for family in families.values():
        parents = (family.get('husband'), family.get('wife'))
        children = family.get('children', [])
        for child in children:
            if child in parent_map:
                grandparents = parent_map[child]
                for sibling in children:
                    if sibling != child and sibling in parent_map:
                        uncle_aunt_family = parent_map[sibling]
                        if grandparents == uncle_aunt_family:
                            for uncle_aunt in uncle_aunt_family:
                                if uncle_aunt:
                                    aunt_uncle_niece_nephew_pairs.add((uncle_aunt, child))
                                    aunt_uncle_niece_nephew_pairs.add((child, uncle_aunt))

    # Check marriages against aunt/uncle and niece/nephew pairs
    for family in families.values():
        husband = family.get('husband')
        wife = family.get('wife')
        if (husband, wife) in aunt_uncle_niece_nephew_pairs or (wife, husband) in aunt_uncle_niece_nephew_pairs:
            husband_name = individuals[husband]['name'] if husband in individuals else "Unknown"
            wife_name = individuals[wife]['name'] if wife in individuals else "Unknown"
            return f"ERROR: Family: {family['id']}: Aunt/Uncle {husband_name} ({husband}) and Niece/Nephew {wife_name} ({wife}) are married."

def check_parents_gender():
    for family in families.values():
        husband_id = family.get('husband')
        wife_id = family.get('wife')
        # Check if the husband's gender is male
        if husband_id in individuals:
            husband_gender = individuals[husband_id].get('sex')
            if husband_gender != 'M':
                husband_name = individuals[husband_id]['name'] if husband_id in individuals else "Unknown"
                return f"ERROR: Family: {family['id']}: Husband {husband_name} ({husband_id}) is not male."
        # Check if the wife's gender is female
        if wife_id in individuals:
            wife_gender = individuals[wife_id].get('sex')
            if wife_gender != 'F':
                wife_name = individuals[wife_id]['name'] if wife_id in individuals else "Unknown"
                return f"ERROR: Family: {family['id']}: Wife {wife_name} ({wife_id}) is not female."
def check_unique_individual_ids():
    seen_ids = set()
    for individual_id in individuals:
        if individual_id in seen_ids:
            return f"ERROR: Individual {individual_id}: Duplicate individual ID found."
        else:
            seen_ids.add(individual_id)
def check_unique_names_and_birthdays():
    seen_names_birthdays = set()
    for individual in individuals.values():
        name = individual['name']
        birthday = individual['birthday']
        if (name, birthday) in seen_names_birthdays:
            return f"ERROR: Individual {individual['id']}: Duplicate name '{name}' and birthday '{birthday}' found."
        else:
            seen_names_birthdays.add((name, birthday))
def check_unique_spouses():
    seen_spouses = set()
    for family in families.values():
        husband_id = family.get('husband')
        wife_id = family.get('wife')
        if (husband_id, wife_id) in seen_spouses or (wife_id, husband_id) in seen_spouses:
            return f"ERROR: Family {family['id']}: Duplicate spouses found with husband {husband_id} and wife {wife_id}."
        else:
            seen_spouses.add((husband_id, wife_id))
#US 25
def check_unique_first_names():
    seen_first_names = set()
    for individual in individuals.values():
        first_name = individual.get('name').split()[0]
        if first_name in seen_first_names:
            return f"ERROR: US25: Individual {individual['id']}: Duplicate first name '{first_name}' found."
        else:
            seen_first_names.add(first_name)
#US 26
def check_membership():
    # indivudal must be a spouse or a child
    for individual in individuals.values():
        if individual.get('spouse') is None and individual.get('children') == []:
            return f"ERROR: US26: Individual {individual['id']}: Must be a spouse or child."



# Unit test class
class TestAnomalies(unittest.TestCase):
    #US04
    def test_check_marriage_before_divorce(self):
        self.assertEqual(check_marriage_before_divorce(), None)
        # Introduce error case
        families['F1']['marriage_date'] = '2020-01-01'
        error = check_marriage_before_divorce()
        print(error)
        self.assertIsNotNone(error)
        families['F1']['marriage_date'] = '2005-01-01'

    #US05
    def test_check_marriage_before_death(self):
        self.assertEqual(check_marriage_before_death(), None)
        # Introduce error case
        individuals['I1']['death_date'] = '2000-01-01'
        error = check_marriage_before_death()
        print(error)
        self.assertIsNotNone(error)
        individuals['I1']['death_date'] = None
    #us03
    def test_check_birth_before_death(self):
        self.assertEqual(check_birth_before_death(), None)
        # Introduce error case
        individuals['I3']['death_date'] = '2000-01-01'
        error = check_birth_before_death()
        print(error)
        self.assertIsNotNone(error)
        individuals['I3']['death_date'] = None
    #us01
    def test_check_dates_before_current(self):
        self.assertEqual(check_dates_before_current(), None)
        # Introduce error case for individual birth date
        individuals['I2']['birthday'] = '3000-01-01'
        self.assertIsNotNone(check_dates_before_current())
        individuals['I2']['birthday'] = '1980-01-01'

        # Introduce error case for individual death date
        individuals['I2']['death_date'] = '3000-01-01'
        self.assertIsNotNone(check_dates_before_current())
        individuals['I2']['death_date'] = '2020-02-02'

        # Introduce error case for family marriage date
        families['F1']['marriage_date'] = '3000-01-01'
        self.assertIsNotNone(check_dates_before_current())
        families['F1']['marriage_date'] = '2005-01-01'

        # Introduce error case for family divorce date
        families['F1']['divorce_date'] = '3000-01-01'
        self.assertIsNotNone(check_dates_before_current())
        families['F1']['divorce_date'] = '2015-01-01'
    #us06
    def test_check_divorce_before_death(self):
        self.assertEqual(check_divorce_before_death(), None)
        # Introduce error case for husband's death date
        individuals['I1']['death_date'] = '2014-01-01'
        self.assertIsNotNone(check_divorce_before_death())
        individuals['I1']['death_date'] = None

        # Introduce error case for wife's death date
        individuals['I2']['death_date'] = '2014-01-01'
        self.assertIsNotNone(check_divorce_before_death())
        individuals['I2']['death_date'] = '2020-02-02'
    #US08
    def test_check_birth_before_parents_marriage(self):
        self.assertEqual(check_birth_before_parents_marriage(), None)
        # Introduce error case
        individuals['I3']['birthday'] = '2000-01-01'
        error = check_birth_before_parents_marriage()
        print(error)
        self.assertIsNotNone(error)
        individuals['I3']['birthday'] = '2010-03-03'
    #US02
    def test_check_birth_before_marriage(self):
        self.assertEqual(check_birth_before_marriage(), None)
        # Introduce error case
        individuals['I1']['birthday'] = '2006-01-01'
        error = check_birth_before_marriage()
        print(error)
        self.assertIsNotNone(error)
        individuals['I1']['birthday'] = '1980-01-01'
    # US09
    def test_check_birth_before_parents_death(self):
        self.assertEqual(check_birth_before_death_parents(), None)
        #error case
        individuals['I3']['birthday'] = '2021-01-01'
        error = check_birth_before_death_parents()
        print(error)
        self.assertIsNotNone(error)
        individuals['I3']['birthday'] = '2010-03-03'
        #error case
        individuals['I4']['birthday'] = '2002-01-01'
        individuals['I1']['death_date'] = '2000-01-01'
        error = check_birth_before_death_parents()
        print(error)
        self.assertIsNotNone(error)
        individuals['I4']['birthday'] = '2012-04-04'
        individuals['I1']['death_date'] = None
    #US10
    def test_check_marriage_after_14(self):
        self.assertEqual(check_marriage_after_14(), None)

        # Introduce error case
        individuals['I1']['birthday'] = '2000-01-01'
        error = check_marriage_after_14()
        print(error)
        self.assertIsNotNone(error)
        individuals['I1']['birthday'] = '1980-01-01'

        # Introduce error case
        individuals['I2']['birthday'] = '2000-01-01'
        error = check_marriage_after_14()
        print(error)
        self.assertIsNotNone(error)
        individuals['I2']['birthday'] = '1985-02-02'

    #US12
    def test_mother_too_old(self):
        self.assertEqual(mother_too_old(), None)

        # Introduce error case
        individuals['I2']['birthday'] = '1900-01-01'
        error = mother_too_old()
        print(error)
        self.assertIsNotNone(error)
        individuals['I2']['birthday'] = '1985-02-02'

    #US13
    def test_siblings_spacing(self):
        self.assertEqual(siblings_spacing(), None)
        # Introduce error case
        individuals['I3']['birthday'] = '2011-09-04'
        error = siblings_spacing()
        print(error)
        self.assertIsNotNone(error)
        individuals['I3']['birthday'] = '2010-03-03'

    #US14
    def test_multiple_births(self):
        self.assertEqual(multiple_births(), None)
        families['F2'] = {'id': 'F2', 'husband': None , 'wife': None , 'marriage_date': None, 'divorce_date': None, 'children': ['I5', 'I6', 'I7', 'I8', 'I9']}
        individuals['I5'] = {'id': 'I5', 'name': None, 'birthday': '2000-01-01', 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I6'] = {'id': 'I6', 'name': None, 'birthday': '2000-01-01', 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I7'] = {'id': 'I7', 'name': None, 'birthday': '2000-01-01', 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I8'] = {'id': 'I8', 'name': None, 'birthday': '2000-01-01', 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I9'] = {'id': 'I9', 'name': None, 'birthday': '2000-01-01', 'death_date': None, 'spouse': None, 'sex': 'F'}
        error = multiple_births()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        del individuals['I5']
        del individuals['I6']
        del individuals['I7']
        del individuals['I8']
        del individuals['I9']

    # US16
    def test_check_wife_name(self):
        self.assertEqual(check_wife_last_name(), None)

        individuals['I2']['name'] = 'Jane Smith'
        error = check_wife_last_name()
        print(error)
        self.assertIsNotNone(error)
        individuals['I2']['name'] = 'Jane Doe'

    #US17
    def test_check_siblings_count(self):
        self.assertEqual(check_siblings_count(), None)
        families['F2'] = {'id': 'F2', 'husband': None , 'wife': None , 'marriage_date': None, 'divorce_date': None, 'children': ['I5', 'I6', 'I7', 'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15', 'I16', 'I17', 'I18', 'I19', 'I20']}
        individuals['I5'] = {'id': 'I5', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I6'] = {'id': 'I6', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I7'] = {'id': 'I7', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I8'] = {'id': 'I8', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I9'] = {'id': 'I9', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I10'] = {'id': 'I10', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I11'] = {'id': 'I11', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I12'] = {'id': 'I12', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I13'] = {'id': 'I13', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I14'] = {'id': 'I14', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I15'] = {'id': 'I15', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I16'] = {'id': 'I16', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I17'] = {'id': 'I17', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I18'] = {'id': 'I18', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I19'] = {'id': 'I19', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        individuals['I20'] = {'id': 'I20', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'}
        error = check_siblings_count()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        del individuals['I5']
        del individuals['I6']
        del individuals['I7']
        del individuals['I8']
        del individuals['I9']
        del individuals['I10']
        del individuals['I11']
        del individuals['I12']
        del individuals['I13']
        del individuals['I14']
        del individuals['I15']
        del individuals['I16']
        del individuals['I17']
        del individuals['I18']
        del individuals['I19']
        del individuals['I20']

    def test_marriage_to_descendents(self):
        self.assertIsNone(check_marriage_to_descendants(), None)
        families['F2'] = {'id': 'F2', 'husband': 'I1', 'wife': 'I3', 'marriage_date': None, 'divorce_date': None, 'children': []}
        individuals['I3']['spouse'] = 'F2'
        individuals['I1']['spouse'] = 'F2'
        error = check_marriage_to_descendants()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        individuals['I3']['spouse'] = None
        individuals['I1']['spouse'] = None

    def test_marriage_to_siblings(self):
        self.assertIsNone(check_siblings_marriage(), None)
        families['F2'] = {'id': 'F2', 'husband': 'I4', 'wife': 'I3', 'marriage_date': None, 'divorce_date': None, 'children': []}
        individuals['I4']['spouse'] = 'F2'
        individuals['I3']['spouse'] = 'F2'
        error = check_siblings_marriage()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        individuals['I4']['spouse'] = None
        individuals['I3']['spouse'] = None

    def test_first_cousin_marriage(self):
        self.assertIsNone(check_no_first_cousin_marriages(), None)
        # family 1
        families['F2'] = {'id': 'F2', 'husband': 'I3', 'wife': 'I5', 'marriage_date': None, 'divorce_date': None, 'children': ['I6']}
        individuals['I5'] = {'id': 'I5', 'name': None, 'birthday': None, 'death_date': None, 'spouse': 'F2', 'sex': 'F'}
        individuals['I6'] = {'id': 'I6', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'M'} # cousin
        # family 2
        families['F3'] = {'id': 'F3', 'husband': 'I7', 'wife': 'I4', 'marriage_date': None, 'divorce_date': None, 'children': ['I9']}
        individuals['I7'] = {'id': 'I7', 'name': None, 'birthday': None, 'death_date': None, 'spouse': 'F3', 'sex': 'M'}
        individuals['I9'] = {'id': 'I9', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'} # cousin
        families['F4'] = {'id': 'F4', 'husband': 'I6', 'wife': 'I9', 'marriage_date': None, 'divorce_date': None, 'children': []}
        error = check_no_first_cousin_marriages()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        del families['F3']
        del families['F4']
        del individuals['I5']
        del individuals['I6']
        del individuals['I7']
        del individuals['I9']
    def test_check_no_aunt_uncle_niece_nephew_marriages(self):
        self.assertIsNone(check_no_aunt_uncle_niece_nephew_marriages(), None)
        # family 1
        families['F2'] = {'id': 'F2', 'husband': 'I3', 'wife': 'I5', 'marriage_date': None, 'divorce_date': None, 'children': ['I6']}
        individuals['I5'] = {'id': 'I5', 'name': None, 'birthday': None, 'death_date': None, 'spouse': 'F2', 'sex': 'F'}
        individuals['I6'] = {'id': 'I6', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'M'} # nephew
        # family 2
        families['F3'] = {'id': 'F3', 'husband': 'I7', 'wife': 'I4', 'marriage_date': None, 'divorce_date': None, 'children': ['I9']}
        individuals['I7'] = {'id': 'I7', 'name': None, 'birthday': None, 'death_date': None, 'spouse': 'F3', 'sex': 'M'}
        individuals['I9'] = {'id': 'I9', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'F'} # Niece

        families['F4'] = {'id': 'F4', 'husband': 'I7', 'wife': 'I9', 'marriage_date': None, 'divorce_date': None, 'children': []}
        error = check_no_aunt_uncle_niece_nephew_marriages()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        del families['F3']
        del families['F4']
        del individuals['I5']
        del individuals['I6']
        del individuals['I7']
        del individuals['I9']
    def test_check_parents_gender(self):
        self.assertIsNone(check_parents_gender(), None)
        families['F2'] = {'id': 'F2', 'husband': 'I4', 'wife': 'I3', 'marriage_date': None, 'divorce_date': None, 'children': []}
        individuals['I4']['spouse'] = 'F2'
        individuals['I3']['spouse'] = 'F2'
        error = check_parents_gender()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        individuals['I4']['spouse'] = None
        individuals['I3']['spouse'] = None

    def test_unique_individuals(self):
        #this will never occur because of how we parsed the GEDCOM file.
        self.assertIsNone(check_unique_individual_ids(), None)
        individuals['I1'] = {'id': 'I1', 'name': None, 'birthday': None, 'death_date': None, 'spouse': None, 'sex': 'M'}
        error = check_unique_individual_ids()
        print(error)
        self.assertIsNotNone(error)
        print(individuals)
        del individuals['I1']
    def test_unique_names_birthdays(self):
        self.assertIsNone(check_unique_names_and_birthdays(), None)
        individuals['I5'] = {'id': 'I5', 'name': 'John', 'birthday': '1990-01-01', 'death_date': None, 'spouse': None, 'sex': 'M'}
        error = check_unique_names_and_birthdays()
        print(error)
        self.assertIsNotNone(error)
        del individuals['I5']
    def test_unique_spouses(self):
        self.assertIsNone(check_unique_spouses(), None)
        families['F2'] = {'id': 'F2', 'husband': 'I2', 'wife': 'I1', 'marriage_date': None, 'divorce_date': None, 'children': []}
        individuals['I2']['spouse'] = 'F2'
        individuals['I1']['spouse'] = 'F2'
        error = check_unique_spouses()
        print(error)
        self.assertIsNotNone(error)
        del families['F2']
        individuals['I2']['spouse'] = None
        individuals['I1']['spouse'] = None
    def test_unique_firstnames(self):
        self.assertIsNone(check_unique_first_names(), None)
        individuals['I5'] = {'id': 'I5', 'name': 'Jane', 'birthday': '1990-01-01', 'death_date': None, 'spouse': None, 'sex': 'M'}
        error = check_unique_first_names()
        print(error)
        self.assertIsNotNone(error)
        del individuals['I5']
    def test_check_membership(self):
        self.assertIsNone(check_membership(), None)
        individuals['I5'] = {'id': 'I5', 'name': 'Jane', 'birthday': '1990-01-01', 'death_date': None, 'spouse': None, 'sex': 'M', 'children': []}
        error = check_membership()
        print(error)
        self.assertIsNotNone(error)
        del individuals['I5']







    # Additional test methods for other functions...

if __name__ == '__main__':
    unittest.main()
