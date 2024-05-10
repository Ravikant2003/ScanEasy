import openfoodfacts
import json
import re
from datetime import datetime

from mapping import group_name, grade_color, score_color
from utils import filter_ingredient, analyse_nutrient, filter_image

def scan(barcode='8901719104046'):
    api = openfoodfacts.API(user_agent='Green-Elixir/0.6')
    required_data = json.load(open('product_schema.json'))
    product_data = api.product.get(barcode, fields=required_data)

    if not product_data:
        print('Error: Product not found.')
        return

    product_data = {
        key: [
            re.sub(r'^en:', '', item) if isinstance(item, str) else item
            for item in value
        ]
        if isinstance(value, list)
        else re.sub(r'^en:', '', value) if isinstance(value, str) else value
        for key, value in product_data.items()
    }

    missing_fields = set(required_data) - set(product_data.keys())
    for field in missing_fields:
        print(f'Warning: Data for "{field}" is missing.')

    product_data.update(
        {
            'ingredients': filter_ingredient(product_data['ingredients']),
            'nova_group_name': group_name(product_data['nova_group']),
            'nutriments': analyse_nutrient(product_data['nutriments'], json.load(open('nutrient_limits.json'))),
            'nutriscore_grade_color': grade_color(product_data['nutriscore_grade']),
            'nutriscore_score_color': score_color(product_data['nutriscore_score']),
            'selected_images': filter_image(product_data['selected_images']),
            'search_date': datetime.now().strftime('%d-%B-%Y'),
            'search_time': datetime.now().strftime('%I:%M %p')
        }
    )

    formatted_data = json.dumps(product_data, indent=4)
    print(formatted_data)

if __name__ == '__main__':
    scan()
