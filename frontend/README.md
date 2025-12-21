# FinWeave Frontend

This directory contains deployment-ready frontend files for Azure App Service.

## Quick Deploy Option 1: Static HTML (dev_ui)

The `dev_ui` directory contains a production-ready static HTML/JS frontend that can be deployed directly to Azure App Service.

### Deployment Steps

1. **Create Azure App Service** (Static Web App or Web App):
   ```bash
   az webapp create --resource-group <your-resource-group> \
     --plan <your-app-service-plan> \
     --name finweave-frontend \
     --runtime "NODE:20-lts"
   ```

2. **Configure Application Settings**:
   - Go to Azure Portal → Your App Service → Configuration → Application settings
   - Add: `REACT_APP_API_URL` = `https://your-backend-api.azurewebsites.net`
   - Or set it to your backend API URL

3. **Deploy using GitHub Actions**:
   - Set up the secret `AZURE_WEBAPP_PUBLISH_PROFILE` in GitHub Secrets
   - Get the publish profile from: Azure Portal → Your App Service → Get publish profile
   - Push to main branch or manually trigger the workflow

4. **Manual Deployment** (using Azure CLI):
   ```bash
   cd dev_ui
   az webapp up --name finweave-frontend --resource-group <your-resource-group>
   ```

## Quick Deploy Option 2: React/Vite App

For a more modern, maintainable frontend, use the React/Vite app in `frontend/react/`.

### Setup

```bash
cd frontend/react
npm install
```

### Development

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

The built files will be in `dist/` directory, which can be deployed to Azure App Service.

### Environment Variables

Create a `.env` file:
```
VITE_API_URL=https://your-backend-api.azurewebsites.net
```

For Azure App Service, set this in Application Settings as `VITE_API_URL`.

## Configuration

### Backend URL Configuration

The frontend automatically detects the backend URL:
- Checks for `REACT_APP_API_URL` or `VITE_API_URL` environment variable
- Falls back to `http://localhost:5001` for local development
- For production, set the environment variable in Azure App Service Configuration

### CORS

Ensure your backend has CORS configured to allow requests from your frontend domain. The backend already has CORS enabled for all origins in development.

## Azure Static Web Apps (Alternative)

You can also deploy to Azure Static Web Apps, which is optimized for static sites:

```bash
az staticwebapp create \
  --name finweave-frontend \
  --resource-group <your-resource-group> \
  --location eastus2
```

Then connect it to your GitHub repository and configure the build settings.
