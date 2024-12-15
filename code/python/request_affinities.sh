#!/bin/bash

# Example requests

# Capture the response from the curl request
response=$(curl -X POST http://localhost:8050/personify \
-H "Content-Type: application/json" \
-d '{ "political_compass": {"coordinates": [0.8, 0.2]}, "philosophy_compass": {"coordinates": [0.3, 0.1]}}')

# Echo the response
echo "$response"
