#!/bin/bash

# URL of the Flask API (assuming it's running locally on port 5000)
URL="http://127.0.0.1:8050/populate_attributes_and_archetypes"

# JSON payload for the POST request
DATA='{
    "AttributeTypes": [
        {
            "name": "economic",
            "left_name": "left",
            "right_name": "Right",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.1},
                {"name": "The Authoritarian Realist", "value": 0.8},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.3},
                {"name": "The Pragmatic Traditionalist", "value": 0.9}
            ]
        },
        {
            "name": "freedom",
            "left_name": "Authoritarian",
            "right_name": "Libertarian",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.9},
                {"name": "The Authoritarian Realist", "value": 0.1},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.8},
                {"name": "The Pragmatic Traditionalist", "value": 0.3}
            ]
        },
        {
            "name": "tone",
            "left_name": "Negative",
            "right_name": "Positive",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.2},
                {"name": "The Authoritarian Realist", "value": 0.3},
                {"name": "The Diplomatic Centrist", "value": 0.9},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.8},
                {"name": "The Pragmatic Traditionalist", "value": 0.5}
            ]
        },
        {
            "name": "cultural",
            "left_name": "Traditional",
            "right_name": "Progressive",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.9},
                {"name": "The Authoritarian Realist", "value": 0.1},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.9},
                {"name": "The Progressive Idealist", "value": 1.0},
                {"name": "The Pragmatic Traditionalist", "value": 0.2}
            ]
        },
        {
            "name": "conflict",
            "left_name": "Avoidant",
            "right_name": "Confrontational",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.3},
                {"name": "The Authoritarian Realist", "value": 0.8},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 0.6},
                {"name": "The Pragmatic Traditionalist", "value": 0.4}
            ]
        },
        {
            "name": "optimism",
            "left_name": "Pessimistic",
            "right_name": "Optimistic",
            "archetypes": [
                {"name": "The Visionary Rebel", "value": 0.8},
                {"name": "The Authoritarian Realist", "value": 0.2},
                {"name": "The Diplomatic Centrist", "value": 0.5},
                {"name": "The Traditionalist", "value": 0.5},
                {"name": "The Progressive Idealist", "value": 1.0},
                {"name": "The Pragmatic Traditionalist", "value": 0.4}
            ]
        }
    ]
}'


# Make the POST request with curl
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "$DATA"

# Optionally, you can output the result of the curl request
echo -e "\nRequest sent successfully!"
