# ai-persona-app

## Running locally

### Requirements
* [Next.Js](https://nextjs.org/docs/getting-started/installation)

* [Docker](http://docker.com)

1. Navigate to the [nextjs](./code/nextjs/) folder.

2. Create a `.env.local` file - check out [.env.local.example](./code/nextjs/.env.local.example) for the format.


3. Build the docker image:
    ```bash
    docker build -t persona-composer .
    ```
4. Run the docker image:

    ```bash
    docker run -it -p 3000:3000 persona-composer
    ```

5. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Deployment
Pushes to main will be deployed to:

[ai-persona-app.vercel.app](https://ai-persona-app.vercel.app)