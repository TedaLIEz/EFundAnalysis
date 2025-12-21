# Self-Hosting the React App

This guide explains how to run the FinWeave React frontend locally on your machine.

## Prerequisites

- **Node.js** 18+ and **npm** (or **yarn**/ **pnpm**)
- **Backend API** running (default: `http://localhost:5001`)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend/react
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

Vite will automatically reload when you make changes to the code.

## Development Mode

### Running the Dev Server

```bash
npm run dev
```

**Features:**
- Hot Module Replacement (HMR) - instant updates
- Fast refresh for React components
- Proxy configured for `/socket.io` and `/health` endpoints
- Runs on port 3000 by default

### Environment Variables (Optional)

Create a `.env` file in `frontend/react/` directory:

```env
VITE_API_URL=http://localhost:5001
```

If not set, the app defaults to `http://localhost:5001` for local development.

### Changing the Port

Edit `vite.config.js`:

```javascript
server: {
  port: 3000,  // Change this to your preferred port
}
```

## Production Build (Self-Hosted)

### 1. Build the App

```bash
npm run build
```

This creates a `dist/` folder with optimized production files.

### 2. Preview Production Build Locally

```bash
npm run preview
```

This serves the production build at `http://localhost:4173` (default Vite preview port).

### 3. Serve with a Static Server

You can use any static file server:

**Using Python:**
```bash
cd dist
python -m http.server 8080
```

**Using Node.js (http-server):**
```bash
npm install -g http-server
cd dist
http-server -p 8080
```

**Using nginx:**
```bash
# Copy dist folder to nginx html directory
cp -r dist/* /usr/share/nginx/html/
# Or configure nginx to serve from dist folder
```

## Configuration

### Backend URL Configuration

The app automatically detects the backend URL:

1. **Environment Variable** (`VITE_API_URL`) - highest priority
2. **Auto-detection** - if hostname is not `localhost`, uses `${protocol}//${hostname}:5001`
3. **Default** - `http://localhost:5001` for local development

### Changing Backend URL

**Option 1: Environment Variable**
```bash
# Create .env file
echo "VITE_API_URL=http://your-backend:5001" > .env

# Or set inline
VITE_API_URL=http://your-backend:5001 npm run dev
```

**Option 2: Edit `src/App.jsx`**
Modify the `getBackendUrl()` function to return your backend URL.

**Option 3: Use Config Panel**
The UI has a config panel where you can change the backend URL at runtime.

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:

```bash
# Vite will automatically try the next available port
npm run dev

# Or specify a port
npm run dev -- --port 3001
```

### Cannot Connect to Backend

1. **Check backend is running:**
   ```bash
   curl http://localhost:5001/health
   ```

2. **Check CORS settings** - Ensure backend allows requests from `http://localhost:3000`

3. **Check backend URL** - Verify the URL in the config panel matches your backend

### Socket.IO Connection Issues

1. **Verify backend Socket.IO path** - Should be `/socket.io`
2. **Check WebSocket support** - Ensure your backend supports WebSocket connections
3. **Check firewall** - Ensure ports are not blocked

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Development Tips

### Hot Reload

Vite provides instant HMR. Changes to `.jsx` files will update without full page reload.

### Debugging

- Open browser DevTools (F12)
- Check Console for errors
- Use React DevTools extension for component inspection
- Network tab to inspect Socket.IO connections

### Linting

```bash
npm run lint
```

## Production Deployment

For production deployment, see:
- `../DEPLOYMENT.md` - Azure App Service deployment
- `README.md` - General documentation

## Common Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Next Steps

1. **Start backend API** - Ensure your FastAPI backend is running on port 5001
2. **Start frontend** - Run `npm run dev` in `frontend/react`
3. **Open browser** - Navigate to `http://localhost:3000`
4. **Connect** - Click "Connect" button (backend URL should be pre-filled)
5. **Start chatting** - Type a message and send!
