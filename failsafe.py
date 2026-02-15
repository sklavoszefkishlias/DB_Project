from typing import Any, List, Tuple



SCHEMA = {
    "Employee": [
        ("employee_id", "int"),
        ("first_name", "str"),
        ("last_name", "str"),
        ("address", "str"),
        ("city", "str"),
        ("country", "str"),
        ("phone", "str"),
        ("email", "str"),
        ("supply_percentage", "float"),
        ("total_commission", "float"),
    ],
    "Customer": [
        ("customer_id", "int"),
        ("first_name", "str"),
        ("last_name", "str"),
        ("address", "str"),
        ("city", "str"),
        ("country", "str"),
        ("phone", "str"),
        ("email", "str"),
        ("team", "str"),
        ("number_of_players", "int"),
        ("balance", "float"),
        ("employee_id", "int"),
    ],
    "Discount": [
        ("discount_id", "int"),
        ("discount_percent", "float"),
        ("max_amount_kit1", "int"),
        ("max_amount_kit2", "int"),
        ("max_amount_kit3", "int"),
        ("number_of_players", "int"),
    ],
    "Item": [
        ("item_id", "int"),
        ("name", "str"),
        ("description", "str"),
        ("color", "str"),
        ("size", "str"),
        ("category", "str"),
        ("kit_type", "int"),
        ("price", "float"),
        ("wholesale_cost", "float"),
        ("stock", "int"),
    ],
    "Orders": [
        ("order_id", "int"),
        ("customer_id", "int"),
        ("order_date", "str"),
        ("total_price", "float"),
    ],

    "Order_Item": [
        (("order_id", "item_id"), "composite"),
        ("item_amount", "int"),
    ],
}


TABLE_NAMES = list(SCHEMA.keys())


def _strip_sql_quotes(value: Any) -> Any:
  
    if not isinstance(value, str):
        return value
    v = value.strip()
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1]
    return v


def is_integer_like(value: Any) -> bool:
    
    v = _strip_sql_quotes(value)
    if isinstance(v, int):
        return True
    if isinstance(v, float):
        return v.is_integer()
    if isinstance(v, str):
        return v.isdigit()
    return False


def is_float_like(value: Any) -> bool:
  
    v = _strip_sql_quotes(value)
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def is_string_like(value: Any) -> bool:
    
    if value is None:
        return True
    return isinstance(value, str)


def is_valid_name(value: Any) -> bool:
   
    v = _strip_sql_quotes(value)
    if not isinstance(v, str) or len(v.strip()) == 0:
        return False

    if any(c.isdigit() for c in v):
        return False

    return any(c.isalpha() for c in v)


def is_valid_email(value: Any) -> bool:
   
    v = _strip_sql_quotes(value)
    if not isinstance(v, str):
        return False
    v = v.strip()
    if '@' not in v or len(v) < 5:  
        return False
    parts = v.split('@')
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        return False
    return True


def is_valid_phone(value: Any) -> bool:

    v = _strip_sql_quotes(value)
    if not isinstance(v, str):
        return False

    if not v.isdigit():
        return False

    return len(v) >= 7


def validate(att_array: List[Any], table_type: int, action_type: int) -> Tuple[bool, Any]:
    if table_type < 0 or table_type >= len(TABLE_NAMES):
        return False, f"Invalid table index: {table_type}"

    table_name = TABLE_NAMES[table_type]
    schema = SCHEMA[table_name]


    if table_name == "Order_Item":

        if action_type == 2: 
            if not isinstance(att_array, list) or len(att_array) == 0:
                return False, "Delete expects a list containing the composite id"
            pair = att_array[0]
            if isinstance(pair, list) and len(pair) > 0 and isinstance(pair[0], list):
                pair = pair[0]
            if not (isinstance(pair, (list, tuple)) and len(pair) == 2):
                return False, "Order_Item delete id must be two values: (order_id, item_id)"
            if not is_integer_like(pair[0]) or not is_integer_like(pair[1]):
                return False, "Order_Item ids must be integers"
            return True, att_array


        if not (isinstance(att_array, list) and len(att_array) >= 2):
            return False, "Order_Item expects [ [order_id, item_id], item_amount ]"
        id_pair, amount = att_array[0], att_array[1]
        if not (isinstance(id_pair, (list, tuple)) and len(id_pair) == 2):
            return False, "Order_Item id must be a pair [order_id, item_id]"
        if not is_integer_like(id_pair[0]) or not is_integer_like(id_pair[1]):
            return False, "Order_Item ids must be integers"
        if not is_integer_like(amount):
            return False, "Order_Item amount must be integer"
        return True, att_array


    try:
        if action_type == 0: 

            expected_columns = schema[1:]
            if not isinstance(att_array, list) or len(att_array) != len(expected_columns):
                return False, f"Add expects {len(expected_columns)} values for {table_name}, got {len(att_array)}"
            for (col_name, expected_type), value in zip(expected_columns, att_array):
                if expected_type == "str" and not is_string_like(value):
                    return False, f"Column '{col_name}' expects a string"

                if expected_type == "str":
                    if col_name in ('first_name', 'last_name'):
                        if not is_valid_name(value):
                            return False, f"Column '{col_name}' must contain at least one letter (not numbers)"
                    elif col_name == 'email':
                        if not is_valid_email(value):
                            return False, f"Column '{col_name}' must be a valid email (contain @)"
                    elif col_name == 'phone':
                        if not is_valid_phone(value):
                            return False, f"Column '{col_name}' must be a valid phone number (at least 7 digits)"
                if expected_type == "int" and not is_integer_like(value):
                    return False, f"Column '{col_name}' expects an integer"
                if expected_type == "float" and not is_float_like(value):
                    return False, f"Column '{col_name}' expects a number"
            return True, att_array

        if action_type == 1: 

            if not isinstance(att_array, list) or len(att_array) < 1:
                return False, "Edit expects a list starting with the primary key"
            pk = att_array[0]
            pk_name, _ = schema[0]
            if not is_integer_like(pk):
                return False, f"Primary key '{pk_name}' must be integer"

            remaining_values = att_array[1:]
            if len(remaining_values) != len(schema) - 1:
                return False, f"Edit expects {len(schema)-1} following elements (use 'noval' to skip)"
            for (col_name, expected_type), value in zip(schema[1:], remaining_values):
                if value == 'noval':

                    continue
                if expected_type == "str" and not is_string_like(value):
                    return False, f"Column '{col_name}' expects a string"

                if expected_type == "str":
                    if col_name in ('first_name', 'last_name'):
                        if not is_valid_name(value):
                            return False, f"Column '{col_name}' must contain at least one letter (not numbers)"
                    elif col_name == 'email':
                        if not is_valid_email(value):
                            return False, f"Column '{col_name}' must be a valid email (contain @)"
                    elif col_name == 'phone':
                        if not is_valid_phone(value):
                            return False, f"Column '{col_name}' must be a valid phone number (at least 7 digits)"
                if expected_type == "int" and not is_integer_like(value):
                    return False, f"Column '{col_name}' expects an integer"
                if expected_type == "float" and not is_float_like(value):
                    return False, f"Column '{col_name}' expects a number"
            return True, att_array

        if action_type == 2: 
            if not isinstance(att_array, list) or len(att_array) == 0:
                return False, "Delete expects a list containing the id"
            pk = att_array[0]

            if isinstance(pk, (list, tuple)) and len(pk) > 0:
                pk = pk[0]
            pk_name, _ = schema[0]
            if not is_integer_like(pk):
                return False, f"Primary key '{pk_name}' must be integer for delete"
            return True, att_array

        return False, f"Unknown action type: {action_type}"

    except Exception as exc:
        return False, f"Validation failure: {exc}"


if __name__ == '__main__':
    example = ['John', 'Doe', '1 Main St', 'Town', 'Country', '555-0000', 'me@example.com', 0.1, 100.0]
    ok, msg = validate(example, TABLE_NAMES.index('Employee'), 0)
    print('Valid example for Employee Add?', ok, msg)
