# FashionHero Storefront Preview

Local Next.js copy of the FashionHero storefront prepared for collaborative development and Vercel preview deployments.

## Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run test`

## Deployment Workflow

- Keep `main` connected to the main Vercel project.
- Use feature branches for preview deployments.
- Share public Vercel preview URLs for review before changes merge to `main`.

## Scope

This v1 covers storefront routes only:

- `/`
- `/about`
- `/collections/[slug]`
- `/products/[slug]`
- `/wishlist`
- `/account/login`

The app runs entirely on local mock data and local assets. No external API or auth backend is required.
