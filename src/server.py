#!/usr/bin/env python3
import os
import sys
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
from fastmcp import FastMCP

mcp = FastMCP("PowerSchool MCP Server")

# Global variable to cache the authentication token
_auth_cache = {
    "token": None,
    "expires_at": None
}

class PowerSchoolAPI:
    """Client for PowerSchool API interactions"""
    
    def __init__(self):
        self.base_url = os.environ.get("POWERSCHOOL_URL", "").rstrip("/")
        self.client_id = os.environ.get("POWERSCHOOL_CLIENT_ID", "")
        self.client_secret = os.environ.get("POWERSCHOOL_CLIENT_SECRET", "")
        self.username = os.environ.get("POWERSCHOOL_USERNAME", "")
        self.password = os.environ.get("POWERSCHOOL_PASSWORD", "")
        
        if not all([self.base_url, self.client_id, self.client_secret]):
            raise ValueError("PowerSchool configuration incomplete. Set POWERSCHOOL_URL, POWERSCHOOL_CLIENT_ID, and POWERSCHOOL_CLIENT_SECRET environment variables.")
    
    def _get_token(self) -> str:
        """Get or refresh authentication token"""
        global _auth_cache
        
        # Check if we have a valid cached token
        if _auth_cache["token"] and _auth_cache["expires_at"]:
            if datetime.now() < _auth_cache["expires_at"]:
                return _auth_cache["token"]
        
        # Request new token
        auth_url = f"{self.base_url}/oauth/access_token"
        
        # PowerSchool supports both client credentials and password grant types
        if self.username and self.password:
            # Password grant type for student login
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }
        else:
            # Client credentials grant type
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        
        try:
            response = requests.post(auth_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            _auth_cache["token"] = token_data["access_token"]
            # Set expiration to 5 minutes before actual expiration for safety
            expires_in = token_data.get("expires_in", 3600)
            _auth_cache["expires_at"] = datetime.now() + timedelta(seconds=expires_in - 300)
            
            return _auth_cache["token"]
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from PowerSchool authentication: {e}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to authenticate with PowerSchool: {e}")
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to PowerSchool API"""
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from PowerSchool: {e}")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request to PowerSchool timed out after 30 seconds")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to PowerSchool: {e}")
    
    def get_student_info(self) -> Dict:
        """Get current student information"""
        return self._make_request("/ws/v1/student")
    
    def get_grades(self) -> Dict:
        """Get current grades for the student"""
        return self._make_request("/ws/v1/student/grades")
    
    def get_assignments(self, section_id: Optional[int] = None) -> Dict:
        """Get assignments, optionally filtered by section"""
        if section_id:
            return self._make_request(f"/ws/v1/student/assignments/section/{section_id}")
        return self._make_request("/ws/v1/student/assignments")
    
    def get_grade_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get historical grades"""
        endpoint = "/ws/v1/student/grades/history"
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        if params:
            endpoint += "?" + urlencode(params)
        
        return self._make_request(endpoint)
    
    def get_courses(self) -> Dict:
        """Get student's current courses/sections"""
        return self._make_request("/ws/v1/student/sections")
    
    def get_attendance(self) -> Dict:
        """Get student attendance records"""
        return self._make_request("/ws/v1/student/attendance")

# Initialize the API client (will be created on first use)
_api_client = None

def get_api_client() -> PowerSchoolAPI:
    """Get or create the PowerSchool API client"""
    global _api_client
    if _api_client is None:
        _api_client = PowerSchoolAPI()
    return _api_client

@mcp.tool(description="Get current student information including name, grade level, school, and student ID")
def get_student_info() -> dict:
    """
    Retrieve basic information about the logged-in student.
    
    Returns:
        dict: Student information including name, student ID, grade level, and school
    """
    try:
        client = get_api_client()
        result = client.get_student_info()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get current grades for all courses")
def get_current_grades() -> dict:
    """
    Retrieve the student's current grades for all enrolled courses.
    Shows letter grades, percentage scores, and course information.
    
    Returns:
        dict: Current grades for all courses including letter grade, percentage, and course details
    """
    try:
        client = get_api_client()
        result = client.get_grades()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get list of assignments, optionally filtered by course section ID")
def get_assignments(section_id: Optional[int] = None) -> dict:
    """
    Retrieve assignments for the student. Can be filtered by a specific course section.
    
    Args:
        section_id: Optional course section ID to filter assignments for a specific class
        
    Returns:
        dict: List of assignments with details like name, due date, score, and status
    """
    try:
        client = get_api_client()
        result = client.get_assignments(section_id)
        return {
            "success": True,
            "data": result,
            "section_id": section_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get historical grade data with optional date range filtering")
def get_grade_history(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    """
    Retrieve historical grade data for the student. Useful for tracking grade changes over time.
    
    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        
    Returns:
        dict: Historical grade information showing how grades have changed over the specified period
    """
    try:
        client = get_api_client()
        result = client.get_grade_history(start_date, end_date)
        return {
            "success": True,
            "data": result,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get list of current courses/sections the student is enrolled in")
def get_courses() -> dict:
    """
    Retrieve all courses (sections) that the student is currently enrolled in.
    Includes course names, teachers, periods, and section IDs.
    
    Returns:
        dict: List of courses with details like course name, teacher, period, and section ID
    """
    try:
        client = get_api_client()
        result = client.get_courses()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get student attendance records")
def get_attendance() -> dict:
    """
    Retrieve attendance records for the student showing present, absent, tardy, and excused status.
    
    Returns:
        dict: Attendance records with dates, status, and any related notes
    """
    try:
        client = get_api_client()
        result = client.get_attendance()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool(description="Get comprehensive information including server status and configuration check")
def get_server_info() -> dict:
    """
    Get information about the PowerSchool MCP server including configuration status.
    
    Returns:
        dict: Server information including version, environment, and configuration status
    """
    config_status = {
        "powerschool_url_set": bool(os.environ.get("POWERSCHOOL_URL")),
        "client_id_set": bool(os.environ.get("POWERSCHOOL_CLIENT_ID")),
        "client_secret_set": bool(os.environ.get("POWERSCHOOL_CLIENT_SECRET")),
        "username_set": bool(os.environ.get("POWERSCHOOL_USERNAME")),
        "password_set": bool(os.environ.get("POWERSCHOOL_PASSWORD"))
    }
    
    return {
        "server_name": "PowerSchool MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": sys.version.split()[0],
        "configuration": config_status,
        "configured": config_status["powerschool_url_set"] and config_status["client_id_set"] and config_status["client_secret_set"]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting PowerSchool MCP server on {host}:{port}")
    print(f"PowerSchool URL: {os.environ.get('POWERSCHOOL_URL', 'NOT SET')}")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
