# Frontend Deployment Guide for Azure App Service

This guide covers deploying the FinWeave frontend to Azure App Service.

## Quick Start: Choose Your Option

### Option 1: Static HTML (Fastest) ⚡
**Best for**: Quick deployment, simple setup
- Location: `dev_ui/` directory
- No build step required
- Deploy directly to Azure App Service

### Option 2: React/Vite App (Recommended) ⭐
**Best for**: Production, maintainability, scalability
- Location: `frontend/react/` directory
- Requires build step (`npm run build`)
- Modern React with component architecture

---

## Option 1: Deploy Static HTML Frontend

### Step 1: Create Azure App Service

```bash
# Create resource group (if not exists)
az group create --name finweave-rg --location eastus2

# Create App Service Plan
az appservice plan create \
  --name finweave-frontend-plan \
  --resource-group finweave-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group finweave-rg \
  --plan finweave-frontend-plan \
  --name finweave-frontend \
  --runtime "NODE:20-lts"
```

### Step 2: Configure Application Settings

Set the backend API URL:

```bash
az webapp config appsettings set \
  --resource-group finweave-rg \
  --name finweave-frontend \
  --settings REACT_APP_API_URL="https://your-backend-api.azurewebsites.net"
```

Or via Azure Portal:
1. Go to Azure Portal → Your App Service → Configuration
2. Add Application Setting:
   - Name: `REACT_APP_API_URL`
   - Value: `https://your-backend-api.azurewebsites.net`

### Step 3: Deploy Files

**Option A: Using Azure CLI (Quick)**
```bash
cd dev_ui
az webapp up --name finweave-frontend --resource-group finweave-rg
```

**Option B: Using GitHub Actions**
1. Get publish profile from Azure Portal:
   - Go to App Service → Get publish profile
   - Copy the content
2. Add to GitHub Secrets:
   - Repository → Settings → Secrets → Actions
   - Add secret: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Paste the publish profile content
3. Update `.github/workflows/deploy-frontend.yml`:
   ```yaml
   env:
     AZURE_WEBAPP_NAME: finweave-frontend
     AZURE_WEBAPP_PACKAGE_PATH: "./dev_ui"
   ```
4. Push to main branch or manually trigger workflow

**Option C: Using VS Code Azure Extension**
1. Install "Azure App Service" extension
2. Right-click `dev_ui` folder → Deploy to Web App
3. Select your App Service

**Option D: Using FTP/SCM**
```bash
# Get deployment credentials
az webapp deployment list-publishing-profiles \
  --name finweave-frontend \
  --resource-group finweave-rg

# Upload files via FTP or use Azure Portal → Deployment Center
```

### Step 4: Verify Deployment

Visit: `https://finweave-frontend.azurewebsites.net`

---

## Option 2: Deploy React/Vite Frontend

### Step 1: Build the App

```bash
cd frontend/react
npm install
npm run build
```

This creates a `dist/` folder with production-ready files.

### Step 2: Create Azure App Service

Same as Option 1, Step 1.

### Step 3: Configure Application Settings

```bash
az webapp config appsettings set \
  --resource-group finweave-rg \
  --name finweave-frontend \
  --settings VITE_API_URL="https://your-backend-api.azurewebsites.net"
```

### Step 4: Deploy Built Files

**Option A: Deploy dist folder**
```bash
cd frontend/react/dist
az webapp up --name finweave-frontend --resource-group finweave-rg
```

**Option B: Update GitHub Actions Workflow**

Update `.github/workflows/deploy-frontend.yml`:

```yaml
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: |
          cd frontend/react
          npm ci

      - name: Build React app
        run: |
          cd frontend/react
          npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: ./frontend/react/dist
```

### Step 5: Configure Static File Serving

For React SPA, ensure Azure serves `index.html` for all routes:

Create `web.config` in the `dist` folder (already created in `frontend/web.config`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

---

## Alternative: Azure Static Web Apps

Azure Static Web Apps is optimized for static sites and provides:
- Free SSL certificates
- Global CDN
- Custom domains
- GitHub Actions integration

### Setup

```bash
# Create Static Web App
az staticwebapp create \
  --name finweave-frontend \
  --resource-group finweave-rg \
  --location eastus2 \
  --sku Free
```

Then connect to GitHub repository and configure:
- **App location**: `dev_ui` (for static HTML) or `frontend/react` (for React)
- **Api location**: (leave empty)
- **Output location**: `.` (for static HTML) or `dist` (for React)

---

## Troubleshooting

### CORS Issues

If you see CORS errors, ensure your backend allows your frontend domain:

```python
# In extensions/ext_blueprint.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://finweave-frontend.azurewebsites.net",
        "http://localhost:3000",  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables Not Working

- For static HTML: Use `window.REACT_APP_API_URL` in `config.js`
- For React: Use `import.meta.env.VITE_API_URL`
- Ensure variables are set in Azure Portal → Configuration → Application settings
- Restart the app after adding environment variables

### Socket.IO Connection Issues

- Ensure backend URL includes protocol: `https://your-backend.azurewebsites.net`
- Check that Socket.IO path is correct: `/socket.io`
- Verify backend is accessible from frontend domain

### 404 Errors on Refresh

For React SPA, ensure `web.config` is deployed with the app to handle client-side routing.

---

## Cost Estimation

- **App Service Plan B1**: ~$13/month (Basic tier)
- **Static Web Apps Free**: $0/month (for development)
- **Static Web Apps Standard**: ~$9/month (for production)

---

## Next Steps

1. Set up custom domain (optional)
2. Configure SSL/TLS certificates (automatic with Azure)
3. Set up monitoring and logging
4. Configure CI/CD pipeline
5. Set up staging environment

---

## Support

For issues or questions:
- Check Azure App Service logs: Portal → App Service → Log stream
- Check browser console for frontend errors
- Verify backend is running and accessible
