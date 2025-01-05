#!/bin/bash

# Call to get all conversation objects in the DB (assuming using Flask localhost on port 8050)
curl -X GET http://127.0.0.1:8050/conversations | jq . > conversations_payload.json
