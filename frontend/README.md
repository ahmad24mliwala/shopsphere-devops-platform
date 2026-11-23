# ShopSphere Frontend

React 19 frontend built with Vite.

## Features
- Product catalogue, search, and category filters
- Shopping cart and quantity controls
- Customer checkout form and order confirmation
- Backend API integration through Nginx

## Requirements
- Node.js and npm

## Local development
```bash
npm install
npm run dev
```

## Quality checks
```bash
npm run lint
npm run build
```

## Deployment
Run `npm run build` and copy the generated `dist/` files to the Nginx document root. Frontend deployment is separate from the Jenkins backend deployment pipeline.
