# FinWeave DevUI Module

This module contains a Streamlit-based UI for local debugging and testing of the FinWeave service.

## Purpose

The DevUI module is designed for local development and debugging purposes. It provides an interactive interface to:
- Check service health status
- Test API endpoints
- Monitor service configuration
- Debug service interactions

## Setup

1. Install UI dependencies using `uv`:

```bash
# From the project root, install the UI dependency group
uv sync --group ui
```

2. Make sure the FinWeave Flask service is running:

```bash
# From the project root
uv run flask run --host 0.0.0.0 --port=5001 --debug
```

3. Run the DevUI:

```bash
# From the project root (recommended)
uv run streamlit run dev_ui/app.py

# Or activate the virtual environment and run directly
source .venv/bin/activate  # on macOS/Linux
streamlit run dev_ui/app.py
```

The UI will be available at `http://localhost:8501` by default.

## Configuration

You can configure the service URL in two ways:

1. **Environment Variable**: Set `FINWEAVE_SERVICE_URL` environment variable:
   ```bash
   export FINWEAVE_SERVICE_URL=http://localhost:5001
   uv run streamlit run dev_ui/app.py
   ```

2. **UI Sidebar**: Use the sidebar in the DevUI to change the service URL interactively.

## Features

### Service Status Tab
- Health check functionality
- Service information display
- Quick status monitoring

### API Testing Tab
- Test various API endpoints
- Support for GET, POST, PUT, DELETE, PATCH methods
- JSON request body editor
- Response viewer with status codes and timing

### Logs & Info Tab
- Service configuration display
- Quick actions for debugging
- Environment information

## Usage Tips

1. **Health Check**: Always start by checking the service health to ensure it's running
2. **API Testing**: Use the API Testing tab to test endpoints before integrating them
3. **Custom Endpoints**: Use the "Custom Endpoint" option to test any endpoint path
4. **Request Body**: For POST/PUT/PATCH requests, use valid JSON format in the request body field

## Notes

- The DevUI module is for **local debugging only** and should not be used in production
- The DevUI connects to the Flask service via HTTP requests
- Make sure the Flask service is running before using the DevUI
- The default service URL is `http://localhost:5001` but can be configured
