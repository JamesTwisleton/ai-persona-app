# ai-persona-app

## Running locally

### Requirements
* [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

### Instructions

1. Navigate to the [nextjs](./code/nextjs/) folder.

2. Create a `.env.local` file - check out [.env.local.example](./code/nextjs/.env.local.example) for the format.


3. Install and run the app:
    ```bash
    npm install
    npm run dev
    ```

5. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Development
* after cloning the repo, copy [pre-commit](./code/hooks/pre-commit) into the `.git/hooks` folder to add a pre-commit which runs eslint

## Deployment
Pushes to `main` branch will be deployed to:

[personacomposer.app](https://personacomposer.app)
