def retrieve_value_by_key(json_data, jsonpath_x):
    return jsonpath_x.find(json_data)
