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
* after cloning the repo, copy [pre-commit](./code/hooks/pre-commit) into the `.git/hooks` folder to add a pre-commit which runs prettier

## Deployment
Pushes to `main` branch will be deployed to:

[personacomposer.app](https://personacomposer.app)

## Persona Compass Application
1. Navigate to [app](./app/) folder. 

2. Run the bash script 'compose_docker.sh' to build, or if pre-build - to launch the application.
    ```bash
    bash compose_docker.sh
    ```

3. Follow the first of the two browser links that are generated.
