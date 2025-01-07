# ai-persona-app

## Running conversations locally

### Requirements
* [docker](http://docker.com/)

### Instructions

1. Create a `.env.local` file for the frontend - check out [.env.local.example](./code/nextjs/.env.local.example) for the format.
2. Create a `.env` file for the backend - check out [.env.example](./code/python/flask_app/.env) for the format.
3. Navigate to the [code](./code/) folder.
4. Run `docker compose up`
5. Open http://localhost:3000/conversations with your browser to see the result.

## Running frontend locally

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
1. Navigate to [dash_app](./code/python/dash_app) folder. 

2. Run the bash script 'compose_docker.sh' to build, or if already built - to launch the application.
    ```bash
    ./compose_docker.sh
    ```
    To rebuild the app after code changes, run:
    ```bash
    ./compose_docker.sh --rebuild
    ```

3. Follow the first of the two browser links that are generated. Press CTRL+C in the terminal to stop the app.

### Miro
https://miro.com/app/board/o9J_l3Gv7S0=/