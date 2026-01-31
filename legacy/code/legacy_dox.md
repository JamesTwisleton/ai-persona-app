# Project overview
An AI focus group app that allows generation of AI personas with personal characteristics such as name, description, age, gender, personal motto and an AI generated profile photo. 

Users are able to share a link to a persona once it has been created. Users can ask personas their opinions on any subject, and share a link to the discussion. Personas can interact with each other as well as a user, in a "focus group" session. Focus group sessions also have shareable links.

Conversations should have a reasonable limit to their length. Once the length limit is reached, the user should be able to click "continue" to make the conversation continue.

# User flows
## Creation of personas
Users should be presented with a form interface which allows them to enter the following fields:
* name
* age
* gender
* description
* attitude

It should also have a cartesian grid representing the personas political alignment. The user should be able to drop a pin to specify the created personas political weighting. Check out `utils.py` and `personas.json` for the work we've done on this so far.

Finally, a button labelled "create persona" should be displayed. Clicking this will kick off the persona creation process, showing a loading indicator. Once the persona has been created, the user should be redirected to a new page with a unique link showing information about the created persona - the "Viewing a single existing persona" page.

## Viewing a single existing persona
Each persona will have a unique six character identifier. When a user goes to `http://app_url/p/{UNIQUE_SIX_CHARACTER_IDENTIFIER}`, the user will see a "profile page" for this persona in the style of a minimal social media profile. This will include:
* the ai generated photo of the persona
* their name
* their age
* their gender
* their description
* their motto

Underneath the profile component, there should be a button labelled "Start a conversation with {PERSONA_NAME}". Clicking this button will take the user to the Conversation session page

## Conversation session page



# User security considerations
All best practices should be followed in terms of infosec requirements.

# General instructions
Don't overcomplicate! Add descriptive comments that will allow a junior developer to be able to follow along. Stick to object oriented paradigm.

