#!/bin/bash

# Capture the response from the curl request
response=$(curl -X POST http://localhost:8050/generate-motto \
-H "Content-Type: application/json" \
-d '{"prompt": "Man who loves donuts.", "motto_tone": "comedic"}')

# Echo the response
echo "$response"
