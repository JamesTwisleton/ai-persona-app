import json
import numpy as np
from datetime import datetime
from sqlalchemy.sql import text

# read json file
def read_json(file_path):
    """
    Reads a JSON file containing a list of points and returns the list of points

    Parameters
    ----------
    file_path : str
        The path to the JSON file

    Returns: ???
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def get_archetype_as_list(db):

    query = text("""
        SELECT 
            arch.name AS archetype_name, 
            arch.value AS value, 
            att.name AS attribute_name, 
            arch.attribute_type_id AS attribute_type_id,
            att.id AS attribute_id
        FROM archetypes AS arch
        JOIN attribute_types AS att 
        ON arch.attribute_type_id = att.id
        ORDER BY arch.name, att.id
    """)

    # Execute the query
    result = db.session.execute(query)

    # Initialize a dictionary to organize data
    archetype_data = {}

    # Process the query result
    for row in result:
        archetype_name = row.archetype_name
        attribute_name = row.attribute_name.lower()  # Dynamically handle all attribute names
        value = row.value

        # Check if the archetype_name is already added
        if archetype_name not in archetype_data:
            # Initialize the archetype's dictionary with name and empty coordinates
            archetype_data[archetype_name] = {
                "name": archetype_name,
                "coordinates": {}  # Empty dictionary for coordinates
            }

        # Add the attribute name and value to coordinates
        archetype_data[archetype_name]["coordinates"][attribute_name] = value

    # Convert the dictionary to a list of dictionaries
    archetype_list = list(archetype_data.values())

    return archetype_list

def calculate_age(dob):
    """
    Calculate age from the date of birth.
    """
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

class PersonaSpace:
    def __init__(self, persona_attributes, archetype_attributes):
        self.persona_state = persona_attributes
        self.archetype_states = archetype_attributes
        self.archetype_names = self.get_archetype_names()
        self.persona_vector = None
        self.archetype_vector = None

    def get_vectors(self):
        p_vec = list(self.persona_state.values())
        a_vec = []
        
        for archetype in self.archetype_states:
            coordinates = list(archetype['coordinates'].values())
            a_vec.append(coordinates)
            self.archetype_vectors = np.array(a_vec)
            self.persona_vector = np.array(p_vec)  

    def get_archetype_names(self):    
        archetype_names = []
        for archetype in self.archetype_states:
            archetype_names.append(archetype['name'])
        return archetype_names
 
    def calculate_similarity(self):

        self.get_vectors()

        # Calculate the cosine similarity between the persona vector and each archetype vector
        d_cos = np.dot(self.archetype_vectors, self.persona_vector) / (
            np.linalg.norm(self.archetype_vectors, axis=1) * np.linalg.norm(self.persona_vector))

        # Normalize the cosine similarities
        d_cos_norm = (d_cos - np.min(d_cos)) / (
            np.max(d_cos) - np.min(d_cos))
        
        # Their normalized cosine similarities should together sum to 1
        d_cos_norm = d_cos_norm / np.sum(d_cos_norm)

        # Add back the archetype names as a dictionary
        archetype_similarity = {}
        for i, archetype_name in enumerate(self.archetype_names):
            archetype_similarity[archetype_name] = round(d_cos_norm[i], 3)

        # return archetype_similarity
        return archetype_similarity

if __name__ == "__main__":
    print("This module is not intended to be run as a standalone script.")
    print("Please import the module in another script.")

    # Example usage:
    archetype_dicts = [
    {
        "name": "The visionary Rebel",
        "coordinates": {
            "economic": 0.1,
            "freedom": 0.9,
            "tone": 0.2,
            "culture": 0.9,
            "conflict": 0.3,
            "optimism": 0.8
            }
        },

    {
        "name": "The Authoritarian Realist",
        "coordinates": {
            "economic": 0.8,
            "freedom": 0.1,
            "tone": 0.3,
            "culture": 0.1,
            "conflict": 0.8,
            "optimism": 0.2
        }
    },
    {
        "name": "The Diplomatic Centrist",
        "coordinates": {
            "economic": 0.5,
            "freedom": 0.5,
            "tone": 0.9,
            "culture": 0.5,
            "conflict": 0.7,
            "optimism": 0.6
        }
    },
    {
        "name": "The Cynical Firebrand",
        "coordinates": {
            "economic": 0.2,
            "freedom": 0.4,
            "tone": 0.1,
            "culture": 0.7,
            "conflict": 0.2,
            "optimism": 0.3
        }
    },
    {
        "name": "The Progressive Idealist",
        "coordinates": {
            "economic": 0.3,
            "freedom": 0.8,
            "tone": 0.8,
            "culture": 1,
            "conflict": 0.6,
            "optimism": 1.6
        }
    },
    {
        "name": "The Pragmatic Traditionalist",
        "coordinates": {
            "economic": 0.9,
            "freedom": 0.3,
            "tone": 0.5,
            "culture": 0.2,
            "conflict": 0.4,
            "optimism": 0.4
            }   
        },
    ]

    persona_dict = {
        "economic": 0.7,
        "freedom": 0.5,
        "tone": 0.4,
        "culture": 0.8,
        "conflict": 0.6,
        "optimism": 0.9
    }

    # Generate the persona affinities
    persona_space = PersonaSpace(persona_dict, archetype_dicts)
    archetype_similarity = persona_space.calculate_similarity()
    print(archetype_similarity)
