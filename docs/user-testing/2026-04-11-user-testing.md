# User Testing Feedback and Action Plan

## Summary
The user testing session was a humbling experience, highlighting several UI quirks and UX friction points. Key feedback was provided by **Rebecca**, who offered a designer's perspective on branding inconsistencies, and even **Henry** (the dog) made a background appearance. The session yielded critical insights into how users perceive the tool's value proposition and interface.

---

## Core Learnings: UX & Onboarding
* **Vague Value Proposition**: Features like "Challenge Mode" are not intuitive without an introductory explanation.
* **Missing Landing Page**: There is no guide or landing page to explain how focus groups work before users enter the interface.
* **Misleading Branding**: The current music-note logo implies musical composition rather than persona building.
* **Technical Language**: Instructions like "Enter to send, Shift+Enter for a new line" feel exclusionary to non-developers.
* **Unclear Interaction Triggers**: Users do not intuitively know they must click "Next Turn" to prompt an AI response.
* **Lack of System Feedback**: Missing loading states or progress bars leave users wondering if the app has broken during generation.
* **Invisible Sharing**: Users are forced to manually copy URLs because there are no recognizable share buttons.
* **UI Placement**: Critical options, such as making a persona private, are hidden or confusingly placed.

## Core Learnings: AI Behavior & Interaction
* **Robotic Dialogue**: Responses often feel like standard, non-human AI output.
* **Hostile Personas**: In debate scenarios, personas can become overly argumentative or repeat stances stubbornly.
* **Verbal Abuse**: The AI has been observed insulting the user, using phrases like "deliberately thick" or "boring".
* **Character Breaks**: When challenged for sounding robotic, personas fail to give a human-like defensive response and instead break character.
* **Buggy Interactions**: The upvote counter is bugged, jumping from zero to two upon a single click.
* **Poor Social Iconography**: The use of an arrow and a zero for upvotes is not recognizable as a social engagement tool.
* **Persona Discovery**: Hovering over public personas provides insufficient context regarding their traits.

---

## The Action Plan

| Category | Task | Description |
| :--- | :--- | :--- |
| **Onboarding** | **Build a Landing Page** | Create a screen explaining the tool's purpose (instant focus groups) with a showcase example. |
| **UI/UX** | **Overhaul Chat UI** | Replace technical keyboard instructions with a visible "Send" button. |
| **UI/UX** | **Progress Indicators** | Add a progress bar or spinner for backend generations. |
| **AI logic** | **Refine System Prompts** | Adjust prompts to prevent insults, encourage active listening, and sound more human. |
| **Features** | **Fix Upvote Component** | Resolve the state management bug and update the icon to standard web conventions. |
| **Features** | **Enhance Persona Context** | Implement detailed hover states or rankings based on topic relevance. |
| **Features** | **Add Native Sharing** | Build dedicated share buttons for platforms like WhatsApp or Facebook. |
| **Branding** | **Redesign Branding** | Update the logo to reflect human profile construction instead of music. |

---

### Transcript Highlights
* **James:** Notes the need for a "generate backstory" feature for new personas.
* **Rebecca:** Suggests the "Next Turn" button should be at the bottom of the chat, similar to ChatGPT.
* **Observations:** The "convinced" indicator in Challenge Mode is currently unclear and visually overwhelming with red circles.