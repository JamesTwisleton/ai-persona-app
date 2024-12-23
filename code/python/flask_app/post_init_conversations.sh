#!/bin/bash

# URL of the Flask API (assuming it's running locally on port 8050)
URL="http://127.0.0.1:8050/init-conversations"

# JSON payload for the POST request
DATA='{
  "conversations": [
    {
      "id": 1,
      "topic": "Economic Freedom Debate",
      "created": "2024-12-22T10:00:00",
      "user": {
        "id": 1,
        "username": "jane_doe",
        "creation_date": "2024-01-15T14:22:00"
      },
      "personas": [
        {
          "id": 1,
          "name": "Barry",
          "dob": "1990-06-15",
          "location": "New York",
          "profile_picture_s3_bucket_address": "https://example.com/images/barry.jpg",
          "creation_date": "2024-06-01T10:30:00",
          "attributes": [
                { "name": "economic", "value": 0.2, "attribute_type_id": 1 },
                { "name": "freedom", "value": 0.85, "attribute_type_id": 2 },
                { "name": "tone", "value": 0.8, "attribute_type_id": 3 },
                { "name": "cultural", "value": 1.0, "attribute_type_id": 4 },
                { "name": "conflict", "value": 0.3, "attribute_type_id": 5 },
                { "name": "optimism", "value": 1.0, "attribute_type_id": 6 }
          ]
        },
        {
          "id": 2,
          "name": "Susan",
          "dob": "1985-04-20",
          "location": "Los Angeles",
          "profile_picture_s3_bucket_address": "https://example.com/images/susan.jpg",
          "creation_date": "2024-06-01T10:35:00",
          "attributes": [
                { "name": "economic", "value": 0.5, "attribute_type_id": 1 },
                { "name": "freedom", "value": 0.5, "attribute_type_id": 2 },
                { "name": "tone", "value": 0.7, "attribute_type_id": 3 },
                { "name": "cultural", "value": 0.6, "attribute_type_id": 4 },
                { "name": "conflict", "value": 0.4, "attribute_type_id": 5 },
                { "name": "optimism", "value": 0.7, "attribute_type_id": 6 }
          ]
        },
        {
          "id": 3,
          "name": "Alex",
          "dob": "1995-08-10",
          "location": "Chicago",
          "profile_picture_s3_bucket_address": "https://example.com/images/alex.jpg",
          "creation_date": "2024-06-01T10:40:00",
          "attributes": [
            { "name": "economic", "value": 0.3, "attribute_type_id": 1 },
            { "name": "freedom", "value": 0.9, "attribute_type_id": 2 },
            { "name": "tone", "value": 0.9, "attribute_type_id": 3 },
            { "name": "cultural", "value": 0.9, "attribute_type_id": 4 },
            { "name": "conflict", "value": 0.5, "attribute_type_id": 5 },
            { "name": "optimism", "value": 1.0, "attribute_type_id": 6 }
          ]
        }
      ],
      "messages": [
        {
          "id": 1,
          "persona_id": 1,
          "toxicity": 0.2,
          "content": "I believe in balanced economic reforms.",
          "created": "2024-12-22T10:05:00"
        },
        {
          "id": 2,
          "persona_id": 2,
          "toxicity": 0.1,
          "content": "Freedom is essential for innovation.",
          "created": "2024-12-22T10:10:00"
        },
        {
          "id": 3,
          "persona_id": 3,
          "toxicity": 0.3,
          "content": "Compromise leads to better outcomes.",
          "created": "2024-12-22T10:15:00"
        }
      ]
    },
    {
      "id": 2,
      "topic": "Cultural Values Discussion",
      "created": "2024-12-23T15:00:00",
      "user": {
        "id": 1,
        "username": "jane_doe",
        "creation_date": "2024-02-01T12:00:00"
      },
      "personas": [
        {
          "id": 1,
          "name": "Barry",
          "dob": "1990-06-15",
          "location": "New York",
          "profile_picture_s3_bucket_address": "https://example.com/images/barry.jpg",
          "creation_date": "2024-06-01T10:30:00",
          "attributes": [
            { "name": "economic", "value": 0.7, "attribute_type_id": 1 },
            { "name": "freedom", "value": 0.8, "attribute_type_id": 2 },
            { "name": "tone", "value": 0.4, "attribute_type_id": 3 },
            { "name": "cultural", "value": 0.5, "attribute_type_id": 4 },
            { "name": "conflict", "value": 0.6, "attribute_type_id": 5 },
            { "name": "optimism", "value": 0.9, "attribute_type_id": 6 }
          ]
        },
        {
          "id": 2,
          "name": "Susan",
          "dob": "1985-04-20",
          "location": "Los Angeles",
          "profile_picture_s3_bucket_address": "https://example.com/images/susan.jpg",
          "creation_date": "2024-06-01T10:35:00",
          "attributes": [
            { "name": "economic", "value": 0.3, "attribute_type_id": 1 },
            { "name": "freedom", "value": 0.6, "attribute_type_id": 2 },
            { "name": "tone", "value": 0.7, "attribute_type_id": 3 },
            { "name": "cultural", "value": 0.4, "attribute_type_id": 4 },
            { "name": "conflict", "value": 0.2, "attribute_type_id": 5 },
            { "name": "optimism", "value": 0.8, "attribute_type_id": 6 }
          ]
        },
        {
          "id": 3,
          "name": "Alex",
          "dob": "1995-08-10",
          "location": "Chicago",
          "profile_picture_s3_bucket_address": "https://example.com/images/alex.jpg",
          "creation_date": "2024-06-01T10:40:00",
          "attributes": [
            { "name": "economic", "value": 0.5, "attribute_type_id": 1 },
            { "name": "freedom", "value": 0.7, "attribute_type_id": 2 },
            { "name": "tone", "value": 0.6, "attribute_type_id": 3 },
            { "name": "cultural", "value": 0.8, "attribute_type_id": 4 },
            { "name": "conflict", "value": 0.3, "attribute_type_id": 5 },
            { "name": "optimism", "value": 0.4, "attribute_type_id": 6 }
          ]
        }
      ],
      "messages": [
        {
          "id": 1,
          "persona_id": 1,
          "toxicity": 0.3,
          "content": "Traditional values are the foundation of our society.",
          "created": "2024-12-23T15:10:00"
        },
        {
          "id": 2,
          "persona_id": 2,
          "toxicity": 0.4,
          "content": "Progressive ideas help us move forward.",
          "created": "2024-12-23T15:15:00"
        },
        {
          "id": 3,
          "persona_id": 3,
          "toxicity": 0.2,
          "content": "Finding common ground is essential.",
          "created": "2024-12-23T15:20:00"
        }
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


