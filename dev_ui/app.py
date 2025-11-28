"""Streamlit UI for local debugging of FinWeave service."""

import json
import os
from typing import Any

import requests
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="FinWeave Debug UI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Default service URL (can be configured via environment variable)
DEFAULT_SERVICE_URL = os.getenv("FINWEAVE_SERVICE_URL", "http://localhost:5001")


def check_service_health(service_url: str) -> dict[str, Any]:
    """Check the health of the FinWeave service.

    Args:
        service_url: Base URL of the FinWeave service

    Returns:
        Dictionary with health status and response data

    """
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        response.raise_for_status()
        return {"status": "healthy", "data": response.json(), "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "data": {"error": "Connection refused. Is the service running?"},
            "status_code": None,
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "data": {"error": "Request timeout"}, "status_code": None}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "data": {"error": str(e)}, "status_code": None}


def main() -> None:
    """Main Streamlit application."""
    st.title("🔍 FinWeave Debug UI")
    st.markdown("Local debugging interface for FinWeave service")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        service_url = st.text_input(
            "Service URL",
            value=DEFAULT_SERVICE_URL,
            help="Base URL of the FinWeave Flask service",
        )
        st.divider()

        # Health check button
        if st.button("🔍 Check Service Health", use_container_width=True):
            with st.spinner("Checking service health..."):
                health_result = check_service_health(service_url)
                if health_result["status"] == "healthy":
                    st.success("✅ Service is healthy!")
                    st.json(health_result["data"])
                else:
                    st.error("❌ Service is not available")
                    st.json(health_result["data"])

    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Service Status", "🔧 API Testing", "📝 Logs & Info"])

    with tab1:
        st.header("Service Status")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Health Check")
            if st.button("Check Health", type="primary"):
                with st.spinner("Checking..."):
                    health_result = check_service_health(service_url)
                    if health_result["status"] == "healthy":
                        st.success("✅ Service is healthy")
                        st.json(health_result["data"])
                    else:
                        st.error("❌ Service is not available")
                        st.json(health_result["data"])

        with col2:
            st.subheader("Service Information")
            st.info(f"**Service URL:** {service_url}")
            st.info(f"**Health Endpoint:** {service_url}/health")

    with tab2:
        st.header("API Testing")
        st.markdown("Test various API endpoints of the FinWeave service")

        # API endpoint selector
        endpoint_type = st.selectbox(
            "Select Endpoint Type",
            ["Health Check", "Custom Endpoint"],
            help="Choose a predefined endpoint or enter a custom one",
        )

        if endpoint_type == "Health Check":
            endpoint = "/health"
            method = "GET"
        else:
            endpoint = st.text_input("Endpoint Path", value="/", help="Enter the API endpoint path (e.g., /api/funds)")
            method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE", "PATCH"])

        # Request parameters
        if method in ["POST", "PUT", "PATCH"]:
            request_body = st.text_area(
                "Request Body (JSON)",
                value="{}",
                height=200,
                help="Enter JSON request body",
            )

        # Send request button
        if st.button("🚀 Send Request", type="primary"):
            try:
                url = f"{service_url}{endpoint}"
                headers = {"Content-Type": "application/json"}

                with st.spinner("Sending request..."):
                    json_data = {}
                    if method in ["POST", "PUT", "PATCH"] and request_body:
                        try:
                            json_data = json.loads(request_body)
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON in request body: {str(e)}")
                            return

                    if method == "GET":
                        response = requests.get(url, timeout=10)
                    elif method == "POST":
                        response = requests.post(url, json=json_data, headers=headers, timeout=10)
                    elif method == "PUT":
                        response = requests.put(url, json=json_data, headers=headers, timeout=10)
                    elif method == "DELETE":
                        response = requests.delete(url, timeout=10)
                    elif method == "PATCH":
                        response = requests.patch(url, json=json_data, headers=headers, timeout=10)

                    # Display response
                    st.subheader("Response")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Status Code", response.status_code)
                    with col2:
                        st.metric("Response Time", f"{response.elapsed.total_seconds():.2f}s")

                    try:
                        response_json = response.json()
                        st.json(response_json)
                    except ValueError:
                        st.text(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Connection refused. Make sure the service is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with tab3:
        st.header("Logs & Information")
        st.markdown("View service logs and debugging information")

        st.subheader("Service Configuration")
        config_data = {
            "Service URL": service_url,
            "Health Endpoint": f"{service_url}/health",
            "Environment": os.getenv("ENVIRONMENT", "development"),
        }
        st.json(config_data)

        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Refresh Status"):
                st.rerun()

        with col2:
            if st.button("📋 Copy Service URL"):
                st.code(service_url, language=None)

        with col3:
            if st.button("🌐 Open in Browser"):
                st.info(f"Open: {service_url}/health")


if __name__ == "__main__":
    main()
