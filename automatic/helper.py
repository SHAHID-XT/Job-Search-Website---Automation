import json

def read_json(filename="automatic/checker.json"):
    """
    Reads data from a JSON file.

    Parameters:
    filename (str): The name of the JSON file to read from.

    Returns:
    dict: The data read from the JSON file, or an empty dictionary if the file doesn't exist or cannot be read.
    """
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        print(f"Data has been read from {filename}")
        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def write_json(data, filename="automatic/checker.json"):
    """
    Writes data to a JSON file.

    Parameters:
    data (dict): The data to write to the JSON file.
    filename (str): The name of the file to write the JSON data to.
    """
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data has been written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
