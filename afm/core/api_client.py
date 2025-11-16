"""
API client for Plugin Registry Server
Handles all HTTP requests to the remote plugin registry API
"""
import os
import json
import zipfile
import io
import requests
from typing import Optional, Dict, List, Any
from rich.console import Console

console = Console()


class PluginRegistryAPI:
    """Client for Plugin Registry API"""
    
    def __init__(self, base_url: str):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the API server (e.g., "http://localhost:8089/api/v1")
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params)
    
    def _post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, data=data, files=files)
    
    def list_plugins(self, search: Optional[str] = None, author: Optional[str] = None,
                     page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        List all plugins with optional filtering
        
        Args:
            search: Search by plugin name or description
            author: Filter by author
            page: Page number
            per_page: Items per page (max: 100)
        
        Returns:
            Response data with plugins list and metadata
        """
        params = {
            'page': page,
            'per_page': min(per_page, 100)
        }
        if search:
            params['search'] = search
        if author:
            params['author'] = author
        
        response = self._get('/plugins', params=params)
        response.raise_for_status()
        return response.json()
    
    def get_plugin_details(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific plugin
        
        Args:
            name: Plugin name
        
        Returns:
            Plugin details including all versions
        """
        response = self._get(f'/plugins/{name}')
        response.raise_for_status()
        return response.json()
    
    def get_plugin_version_details(self, name: str, version: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific plugin version
        
        Args:
            name: Plugin name
            version: Plugin version
        
        Returns:
            Plugin version details
        """
        response = self._get(f'/plugins/{name}/versions/{version}')
        response.raise_for_status()
        return response.json()
    
    def download_plugin(self, name: str, version: Optional[str] = None, 
                       format: str = 'zip') -> Any:
        """
        Download plugin files
        
        Args:
            name: Plugin name
            version: Plugin version (if None, downloads latest)
            format: Response format ('zip' or 'json')
        
        Returns:
            Plugin files as bytes (ZIP) or Dict (JSON format)
        """
        if version:
            endpoint = f'/plugins/{name}/versions/{version}/download'
        else:
            endpoint = f'/plugins/{name}/download'
        
        params = {'format': format}
        response = self._get(endpoint, params=params)
        response.raise_for_status()
        
        if format == 'zip':
            return response.content
        else:
            return response.json()
    
    def download_plugin_file(self, name: str, version: str, filename: str) -> bytes:
        """
        Download a specific file from a plugin version
        
        Args:
            name: Plugin name
            version: Plugin version
            filename: File name to download
        
        Returns:
            File content as bytes
        """
        response = self._get(f'/plugins/{name}/versions/{version}/files/{filename}')
        response.raise_for_status()
        return response.content
    
    def search_plugins(self, query: str, field: str = 'all', 
                      page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Advanced search with multiple criteria
        
        Args:
            query: Search query
            field: Search field ('name', 'description', 'author', or 'all')
            page: Page number
            per_page: Items per page (max: 100)
        
        Returns:
            Search results
        """
        params = {
            'q': query,
            'field': field,
            'page': page,
            'per_page': min(per_page, 100)
        }
        response = self._get('/plugins/search', params=params)
        response.raise_for_status()
        return response.json()
    
    def get_plugin_index(self) -> Dict[str, Any]:
        """
        Get simplified plugin index (similar to index.json format)
        
        Returns:
            Plugin index data
        """
        response = self._get('/plugins/index')
        response.raise_for_status()
        return response.json()
    
    def publish_plugin(self, plugin_dir: str, name: Optional[str] = None,
                      version: Optional[str] = None, description: Optional[str] = None,
                      author: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload/publish a plugin to the registry
        
        Args:
            plugin_dir: Local directory containing plugin files
            name: Plugin name (required if manifest not provided)
            version: Version override (defaults to manifest version)
            description: Description override
            author: Author override
        
        Returns:
            Response data
        """
        files = {}
        data = {}
        
        # Read manifest.json first to get metadata if not provided
        manifest_file_path = os.path.join(plugin_dir, 'manifest.json')
        if os.path.exists(manifest_file_path):
            with open(manifest_file_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                if not name:
                    name = manifest.get('name')
                if not version:
                    version = manifest.get('version')
                if not description:
                    description = manifest.get('description')
                if not author:
                    author = manifest.get('author')
        
        # Normalize version format (e.g., "0.1" -> "0.1.0")
        if version:
            version_parts = str(version).split('.')
            if len(version_parts) == 2:
                version = f"{version_parts[0]}.{version_parts[1]}.0"
            elif len(version_parts) == 1:
                version = f"{version_parts[0]}.0.0"
        
        # Read plugin.py - use actual file object to preserve filename
        plugin_file_path = os.path.join(plugin_dir, 'plugin.py')
        if not os.path.exists(plugin_file_path):
            raise FileNotFoundError(f"plugin.py not found in {plugin_dir}")
        
        # Open file in binary mode for upload
        plugin_file_obj = open(plugin_file_path, 'rb')
        files['plugin_file'] = ('plugin.py', plugin_file_obj, 'text/x-python')
        
        # Read manifest.json for upload (optional)
        if os.path.exists(manifest_file_path):
            manifest_file_obj = open(manifest_file_path, 'rb')
            files['manifest_file'] = ('manifest.json', manifest_file_obj, 'application/json')
        
        # Add metadata to form data
        if name:
            data['name'] = name
        if version:
            data['version'] = version
        if description:
            data['description'] = description
        if author:
            data['author'] = author
        
        # Add additional files
        # Note: requests library handles multiple files with same name using list of tuples
        additional_files_list = []
        for item in os.listdir(plugin_dir):
            item_path = os.path.join(plugin_dir, item)
            if os.path.isfile(item_path) and item not in ['plugin.py', 'manifest.json']:
                with open(item_path, 'rb') as f:
                    file_content = f.read()
                additional_files_list.append(('additional_files', (item, io.BytesIO(file_content), 'application/octet-stream')))
        
        # Convert files dict to list format for requests (required format)
        # Format: [('field_name', ('filename', file_obj, 'content_type'))]
        files_list = [
            ('plugin_file', files['plugin_file'])
        ]
        if 'manifest_file' in files:
            files_list.append(('manifest_file', files['manifest_file']))
        files_list.extend(additional_files_list)
        
        # Use files_list format for requests
        try:
            response = self._post('/plugins', data=data, files=files_list)
            
            # Better error handling
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP {response.status_code} Error"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                console.print(f"❌ {error_msg}", style="red")
                raise requests.exceptions.HTTPError(error_msg) from e
            
            return response.json()
        finally:
            # Close file objects
            if 'plugin_file' in files:
                files['plugin_file'][1].close()
            if 'manifest_file' in files:
                files['manifest_file'][1].close()
    
    def extract_zip_to_directory(self, zip_data: bytes, target_dir: str) -> None:
        """
        Extract ZIP data to target directory
        
        Args:
            zip_data: ZIP file content as bytes
            target_dir: Target directory to extract to
        """
        os.makedirs(target_dir, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            zip_ref.extractall(target_dir)

