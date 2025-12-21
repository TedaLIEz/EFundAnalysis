# Quick Start: Deploy Frontend to Azure App Service

## 🚀 Fastest Option: Static HTML (5 minutes)

### 1. Create Azure App Service
```bash
az webapp create --resource-group <your-rg> \
  --plan <your-plan> \
  --name finweave-frontend \
  --runtime "NODE:20-lts"
```

### 2. Set Backend URL
```bash
az webapp config appsettings set \
  --resource-group <your-rg> \
  --name finweave-frontend \
  --settings REACT_APP_API_URL="https://your-backend.azurewebsites.net"
```

### 3. Deploy
```bash
cd dev_ui
az webapp up --name finweave-frontend --resource-group <your-rg>
```

**Done!** Visit `https://finweave-frontend.azurewebsites.net`

---

## ⭐ Recommended Option: React/Vite App

### 1. Build
```bash
cd frontend/react
npm install
npm run build
```

### 2. Deploy dist folder
```bash
cd dist
az webapp up --name finweave-frontend --resource-group <your-rg>
```

### 3. Set Backend URL in Azure Portal
- Go to App Service → Configuration → Application settings
- Add: `VITE_API_URL` = `https://your-backend.azurewebsites.net`

---

## 📋 What's Included

✅ **Enhanced dev_ui** - Production-ready static HTML frontend
✅ **React/Vite app** - Modern React frontend with components
✅ **Azure deployment configs** - web.config, staticwebapp.config.json
✅ **GitHub Actions workflow** - Automated deployment
✅ **Documentation** - Complete deployment guides

---

## 📚 Full Documentation

See `frontend/DEPLOYMENT.md` for detailed instructions, troubleshooting, and alternatives.
