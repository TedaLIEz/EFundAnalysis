# FinWeave React Frontend

A modern React + Vite frontend for the FinWeave chat application.

## Features

- Real-time chat using Socket.IO
- Streaming message support
- Modern React hooks and components
- Responsive design
- Environment-based configuration

## Development

### Prerequisites

- Node.js 18+ and npm

### Setup

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment.

### Preview Production Build

```bash
npm run preview
```

## Configuration

### Environment Variables

Create a `.env` file in the root of this directory:

```env
VITE_API_URL=https://your-backend-api.azurewebsites.net
```

For Azure App Service deployment, set `VITE_API_URL` in Application Settings.

### Backend URL

The app automatically detects the backend URL:
1. Checks `VITE_API_URL` environment variable
2. Falls back to auto-detection based on hostname
3. Defaults to `http://localhost:5001` for local development

## Deployment to Azure App Service

### Option 1: Deploy Built Files

1. Build the app: `npm run build`
2. Deploy the `dist/` folder to Azure App Service
3. Set `VITE_API_URL` in Azure App Service Configuration

### Option 2: Use GitHub Actions

The workflow in `.github/workflows/deploy-frontend.yml` can be configured to deploy this React app.

Update the workflow to:
- Build the React app
- Deploy the `dist/` folder

### Option 3: Azure Static Web Apps

This app is compatible with Azure Static Web Apps:

```bash
az staticwebapp create \
  --name finweave-frontend \
  --resource-group <your-resource-group> \
  --location eastus2
```

Then configure the build settings:
- App location: `frontend/react`
- Api location: (leave empty)
- Output location: `dist`

## Project Structure

```
frontend/react/
├── src/
│   ├── components/      # React components
│   │   ├── Header.jsx
│   │   ├── ConfigPanel.jsx
│   │   ├── ChatContainer.jsx
│   │   └── InputContainer.jsx
│   ├── App.jsx          # Main app component
│   ├── App.css          # App styles
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies
```

## Technologies

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Socket.IO Client** - Real-time communication
- **ESLint** - Code linting
