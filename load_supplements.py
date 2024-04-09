import pandas as pd
import json
import copy

COMPOUND_UNITS = [
        {'unit': 'µg', 'alt_names': ['mcg']},
        {'unit': 'mg', 'alt_names': []},
        {'unit': 'units', 'alt_names': []},
        {'unit': 'g', 'alt_names': []},
    ]

SERVING_UNITS = [
        {'unit': 'capsules', 'alt_names': ['capsule']},
        {'unit': 'scoop', 'alt_names': []},
    ]

def convert_units(amount: str, units: list[dict, ]):
    amount = amount.replace(' ','')

    unit = None
    inputed_unit = None
    for unit in units:
        if unit['unit'] in amount:
            inputed_unit = unit['unit']
            break
        for alt_name in unit['alt_names']:
            if alt_name in amount:
                inputed_unit = alt_name
                break
        if inputed_unit:
            break
    
    if not inputed_unit:
        raise ValueError(f'Didn\'t understand unit of {amount}')
        
    amount_number_str = amount.replace(inputed_unit,'')

    try:
        amount_number = float(amount_number_str)
    except ValueError:
        raise ValueError(f'Didn\'t understand unit of {amount}: Something none-numeric is left in {amount_number_str} after removing unit of {inputed_unit}')

    return amount_number, unit['unit']

def import_supplements():
    with open(r'supplements\supplements_sources.json', 'r') as file:
        supplements = json.load(file)
    
    for supplement_name, info in supplements.items():

        df = pd.read_excel(r'supplements\\' + info['file'])


        amount_number, unit = convert_units(info['serving_size'], SERVING_UNITS)
        info['serving_size'] = amount_number
        info['serving_unit'] = unit

        info['compounds'] = {}
        for index, row in df.iterrows():
            amount_number, unit = convert_units(row['amount'], COMPOUND_UNITS)
            info['compounds'][row['name']] = {'amount': amount_number, 'unit': unit, 'notes': row['notes']}

    # print(supplements)
    # exit()
    return supplements
    

def import_diet(supplements_library):
    with open(r'diets\Bryan_Johnson.json', 'r') as file:
        diet = json.load(file)

    if 'compounds' not in diet.keys():
        diet['compounds'] = {}

    new_compounds = {}
    for compound, compound_info in diet['compounds'].items():
        if compound == 'EITHER':
            for compound, compound_info in compound_info.items():
                pass # We just take the last item of the either

        amount_number, unit = convert_units(compound_info['amount'], COMPOUND_UNITS)
        new_compounds[compound] = {'amount': amount_number, 'unit': unit, 'notes': ''}
    
    diet['compounds'] = new_compounds

    for supplement_name, supplement_info in diet['supplements'].items():
        if supplement_name not in supplements_library.keys():
            print(f'Couldn\'t find {supplement_name} in supplements library')
            continue

        amount_diet, unit_diet = convert_units(supplement_info['amount'], SERVING_UNITS)
        
        unit_supplement_library = supplements_library[supplement_name]['serving_unit']
        if unit_diet != unit_supplement_library:
            print(f'Diet and library unit miss match for {supplement_name}. {unit_diet} and {unit_supplement_library}')
            continue

        amount_conversion = amount_diet / supplements_library[supplement_name]['serving_size']

        for compound, compound_info in supplements_library[supplement_name]['compounds'].items():
            if compound not in diet['compounds'].keys():
                diet['compounds'][compound] = copy.deepcopy(compound_info)
                diet['compounds'][compound]['amount'] = compound_info['amount'] * amount_conversion
            else:
                diet['compounds'][compound]['amount'] += compound_info['amount'] * amount_conversion

    print(diet['compounds'])


    

if __name__ == '__main__':
    supplements = import_supplements()
    import_diet(supplements)