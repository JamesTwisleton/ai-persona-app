# Composing agents for real world usage
## The ask
I am composing a team of agents to take on a project. Each agent will have specialisms. Each agent will have a personality. Each agent will work in tandem with agents (and humans) with different strengths to achieve the team goals.

## Individuals
Users have the ability to create "personas"; these are the basis of the individual agents.

The user selects the attributes the persona should have.

1. What is the personas name?

2. What is the personas A/S/L (age, sex, location)?

3. What is the personas specialism?

4. What is the personas backstory

All attributes apart from specialism are randomisable. In this way, the user can create a persona with a particular set of skills, that still has a "human" touch.

For example, a persona with the senior developer specialism might be good at reviewing pull requests. A persona with a copywriting specialism might excel at slimming down copy.

Ultimately, a persona consists of a pre-prompt that the user will pass to whatever underlying LLM will be implementing the agent. Personas should be shareable, and on the shared persona page the entire pre-prompt should be shown, so users can use the persona in their own workflows.

## Teams
Once personas are constructed, the user can compose a team of personas. The user can opt to select from existing personas and ones they've created.

Maybe you need a project manager, two backend devs, two frontend devs, a delivery manager. 
