

import json

def sum_numeric_from_json(data):
    """
    Recursively sum all numeric values in a nested dict/list structure.
    Converts numeric strings to float automatically.
    """
    total = 0.0

    if isinstance(data, dict):
        for value in data.values():
            total += sum_numeric_from_json(value)
    elif isinstance(data, list):
        for item in data:
            total += sum_numeric_from_json(item)
    else:
        try:
            num = float(data)
            total += num
        except (ValueError, TypeError):
            pass

    return total


