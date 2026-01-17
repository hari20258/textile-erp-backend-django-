"""
Base API Client for Textile Backend
Handles authentication and common API operations
"""
import requests
import json
from typing import Dict, Any, Optional


class BaseAPIClient:
    """Base client for API interactions"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
    
    def register(self, username: str, password: str, email: str, role: str, **kwargs) -> Dict[str, Any]:
        """Register a new user"""
        url = f"{self.base_url}/api/users/register/"
        data = {
            "username": username,
            "password": password,
            "email": email,
            "role": role,
            **kwargs
        }
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and obtain JWT tokens"""
        url = f"{self.base_url}/api/auth/token/"
        data = {"username": username, "password": password}
        response = self.session.post(url, json=data)
        result = self._handle_response(response)
        
        if 'access' in result:
            self.access_token = result['access']
            self.refresh_token = result['refresh']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
        
        return result
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token"""
        url = f"{self.base_url}/api/auth/token/refresh/"
        data = {"refresh": self.refresh_token}
        response = self.session.post(url, json=data)
        result = self._handle_response(response)
        
        if 'access' in result:
            self.access_token = result['access']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
        
        return result
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)
    
    def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PATCH request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.patch(url, json=data)
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return self._handle_response(response)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}
        
        if not response.ok:
            print(f"❌ Error {response.status_code}: {data}")
        
        return data
    
    def print_result(self, title: str, data: Any):
        """Pretty print results"""
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
        print(json.dumps(data, indent=2))
