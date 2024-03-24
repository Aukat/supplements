import pandas as pd
import json

INGREDIENT_UNITS = [
        {'unit': 'µg', 'alt_names': ['mcg']},
        {'unit': 'mg', 'alt_names': []},
        {'unit': 'units', 'alt_names': []},
        {'unit': 'g', 'alt_names': []},
    ]

SERVING_UNITS = [
        {'unit': 'capsules', 'alt_names': []},
    ]

def convert_units(amount: str, units: list[dict, ]):
    amount = amount.replace(' ','')

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
        supplements_sources = json.load(file)
    
    for supplement_name, info in supplements_sources.items():

        df = pd.read_excel(r'supplements\\' + info['file'])


        amount_number, unit = convert_units(info['serving_size'], SERVING_UNITS)
        info['serving_size'] = amount_number
        info['serving_unit'] = unit

        info['ingredients'] = {}
        for index, row in df.iterrows():
            amount_number, unit = convert_units(row['amount'], INGREDIENT_UNITS)
            info['ingredients'][row['name']] = {'amount': amount_number, 'unit': unit, 'notes': row['notes']}

    print(supplements_sources)
    


if __name__ == '__main__':
    import_supplements()