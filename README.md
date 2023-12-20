# ai-persona-app

## Running locally

### Requirements
[Next.Js](https://nextjs.org/docs/getting-started/installation)

First, create a `.env.local` file - check out [.env.local.example](.env.local.example) for the format.

Run the dev server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Creating your own instance
### Provisioning an s3 bucket
in the [terraform](terraform/) directory

```
terraform init
terraform plan
terraform apply
```

## Deployment
Pushes to main will be deployed to:

[ai-persona-nzdwfgkhm-james-projects-c64cb551.vercel.app](https://ai-persona-nzdwfgkhm-james-projects-c64cb551.vercel.app)

Production deployment at:

[ai-persona-app.vercel.app](https://ai-persona-app.vercel.app)

