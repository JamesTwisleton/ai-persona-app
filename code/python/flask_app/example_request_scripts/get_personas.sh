#!/bin/bash

# Call to get all persona objects in the DB (assuming using Flask localhost on port 8050)
curl -X GET http://127.0.0.1:8050/personas | jq . > personas_payload.json
