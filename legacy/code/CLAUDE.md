# CLAUDE.md - Project Specification: AI Persona & Focus Group App

## 1. Project Overview
**"AI Focus Groups"** is a web application that allows users to generate specific AI personas (with distinct names, backstories, visual avatars, and personality weights) and assemble them into "Focus Groups."

Users can provide a topic (e.g., "Increasing taxes on the rich" or "Coke vs. Pepsi"), and the personas will debate or discuss the topic amongst themselves. The primary growth mechanism is **shareability**: users can share public links to specific Personas or generated Conversation logs.

### Core Value Proposition
To provide an instant, shareable "AI Focus Group" where representative synthetic personalities discuss user-defined topics, providing qualitative feedback or entertainment.

---

## 2. Technical Stack & Architecture (Modern 2026 Standards)
The application must be rebuilt from scratch using an idiomatic, modern stack.

* **Frontend:** Next.js (React) - Optimized for SEO and shareable links.
* **Backend/AI Service:** Python (FastAPI or similar) - Handling data science logic, vector math, and LLM orchestration.
* **Database:** AWS RDS
* **Containerization:** Fully Dockerized application.
* **Infrastructure:** AWS (Amazon Web Services).
    * Deployment target: AWS ECS (Elastic Container Service) or Fargate.
    * CI/CD: GitHub Actions.
    * IaC: Terraform (for provisioning infrastructure).
* **AI Models:**
    * **Text:** Large Language Models (LLM) for persona generation and conversation.
    * **Image:** OpenJourney or DALL-E (user selectable) for avatar generation.

---

## 3. Core Mechanics & Logic

### 3.1 Persona Vector Space (The "Personality Engine")
Personas are defined mathematically to ensure consistency.
* **Archetypes:** A JSON configuration defines "Archetypes" (e.g., "The Skeptic," "The Optimist," "The Traditionalist").
* **Euclidean Space:** These archetypes exist as fixed points in a 2D Euclidean space ($X, Y$).
* **Weighting Logic:**
    * The user places a "pin" on a Cartesian grid.
    * The system calculates the Euclidean distance between the user's pin and the Archetypes.
    * The final persona personality is a weighted blend of the nearest archetypes based on this distance.
    * *Reference:* See `utils.py` and `personas.json` for existing logic.

### 3.2 Content Moderation & Safety
To prevent abuse (racism, homophobia, extreme political toxicity), a safety layer is required before any output is shown.
* **Mechanism:** A lightweight Neural Network classifier.
* **Function:** Analyzes the sentiment/toxicity of generated messages.
* **Output:** A scale of $0$ to $1$. If the score exceeds a safety threshold, the response is flagged or regenerated.

---

## 4. User Flows

### 4.1 Authentication
* **Public:** Viewing Personas and Conversations does *not* require login.
* **Private:** Creating Personas or starting Focus Groups requires a user account.

### 4.2 Persona Creation
Users access a form interface to build a new identity.
* **Fields:** Name, Age, Gender, Description (Backstory).
* **Attitude Selector:** Neutral, Sarcastic, Comical, Somber.
* **Model Selector:** OpenJourney or DALL-E.
* **Personality Grid:** A visual Cartesian grid where users drop a pin to define political/social alignment.
* **Action:** Clicking "Create" triggers:
    1.  Vector math calculation.
    2.  Image generation API call.
    3.  Motto/Tagline generation.
    4.  Database storage.
* **Result:** Redirect to the **Persona Profile Page**.

### 4.3 Viewing a Single Persona (Public View)
**URL Scheme:** `/p/{UNIQUE_SIX_CHAR_ID}`
* Displays the AI-generated avatar.
* Displays metadata: Name, Age, Gender, Motto, Description.
* **Call to Action:** "Start a conversation with {Name}" (Lead into Focus Group flow).

### 4.4 Focus Group / Conversation Flow
* **Setup:** User selects one or multiple Personas (Group Chat).
* **Topic:** User enters a subject.
* **Interface:** A chat interface resembling a group messaging app.
    * Each persona "speaks" in turn based on the LLM orchestration.
    * **Limits:** Conversations have a reasonable length limit. Users must click "Continue" to extend execution.
* **Share:** Generates a unique link for the conversation log.

### 4.5 Conversation View (Public View)
**URL Scheme:** `/c/{UNIQUE_SIX_CHAR_ID}`
* Read-only view of a focus group session.
* Clear attribution of which persona said what.

---

## 5. Development Guidelines
* **Documentation:** Add descriptive comments for junior developers. Create Sphinx documentation.
* **Paradigm:** Stick to Object-Oriented Programming (OOP) where appropriate, particularly for the Python Backend (e.g., `Persona` class, `Conversation` class).
* **Security:** Follow all InfoSec best practices.
* **Research:** Attempt to source academic papers regarding "Representativeness of AI Personas in Focus Groups" to validate the USP.
* **Local development** when running locally, should spin up a Docker compose environment that emulates the AWS deployed stack - the only external service used when running locally should be the LLM providers.
* **Tests** must be test driven - write the tests first, then implement the code to make the tests pass.
