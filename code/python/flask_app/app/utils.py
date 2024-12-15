import math
import json
import random


# read json file
def read_json(file_path):
    """
    Reads a JSON file containing a list of points and returns the list of points

    Parameters
    ----------
    file_path : str
        The path to the JSON file

    Returns
    -------
    list
        A list of points in the format [{'x': float, 'y': float, 'label': str}]
    """
    with open(file_path, 'r') as file:
        return json.load(file)['points']

# Get the euclidean distance for each point
def euclidean_distance(x1, y1, x2, y2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)

    Parameters
    ----------
    x1 : float
    y1 : float
    x2 : float
    y2 : float

    Returns
    -------
    float
        The Euclidean distance between the two points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to calculate Euclidean distance from a point to all predefined points
def calculate_distances(x, y, persona_scape):
    """
    Calculate Euclidean distance from (x, y) to all predefined points
    
    Parameters
    ----------
    x : float
    y : float
    persona_scape : list(dict)
    
    Returns
    -------
    list
        A list of Euclidean distances from (x, y) to each predefined point
        A list of labels for each predefined point
    """
    distances = []
    labels = []
    for point in persona_scape:
        distances.append(euclidean_distance(x, y, point['x'], point['y']))
        labels.append(point['label'])
    return distances, labels

# Function to calculate affinity of a point to all predefined points
def calculate_affinity(x, y, persona_compass):
    """
    Calculate affinity of (x, y) to all predefined points
    
    Parameters
    ----------
    x : float
    y : float
    
    Returns
    -------
    list
        A list of affinities from (x, y) to each predefined point
    """
    distances, labels = calculate_distances(x, y, persona_compass)
    max_distance = max(distances)
    inverted_distances = [max_distance - dist for dist in distances]
    sum_inverted_distances = sum(inverted_distances)
    normalized_affinity = [round(dist / sum_inverted_distances, 3) for dist in inverted_distances]

    # Zip the labels and normalized affinities
    affinity_dict = dict(zip(labels, normalized_affinity))
    return affinity_dict

# Generate random point
def generate_random_point():
    """
    Generate a random point within the unit square [0, 1] x [0, 1].

    Returns
    -------
    dict
        A dictionary with 'x' and 'y' keys, where the values are 
        the x and y coordinates of the point, rounded to one decimal place.
    """

    return {"x": round(random.uniform(0, 1), 1), "y": round(random.uniform(0, 1), 1)}

