"""Tool Manager untuk Agent Pribadi (AG)

Mengelola download, installation, dan maintenance dari development tools.
Mendukung: Nginx, PHP, MySQL, PostgreSQL, Node.js, MongoDB, Go, dll.
"""

import os
import yaml
import requests
import tarfile
import zipfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from config.settings import PROJECT_ROOT, TOOLS_CONFIG_PATH, BIN_DIR

logger = logging.getLogger(__name__)


class ToolsManager:
    """Manager untuk mengelola development tools."""
    
    def __init__(self):
        """Inisialisasi Tools Manager."""
        self.config_path = TOOLS_CONFIG_PATH
        self.bin_dir = BIN_DIR
        self.tools_config = self._load_config()
        
        # Ensure bin directory exists
        self.bin_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load tools configuration dari YAML file.
        
        Returns:
            Dict: Tools configuration
        """
        try:
            if not self.config_path.exists():
                logger.error(f"Config file not found: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded tools config: {len(config)} tools available")
            return config
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def list_available_tools(self) -> Dict[str, List[str]]:
        """List semua tools yang tersedia di config.
        
        Returns:
            Dict: {tool_name: [versions]}
        """
        result = {}
        for tool_name, versions in self.tools_config.items():
            if isinstance(versions, dict):
                result[tool_name] = list(versions.keys())
        return result
    
    def list_installed_tools(self) -> List[Dict[str, str]]:
        """List semua tools yang sudah terinstall.
        
        Returns:
            List[Dict]: [{tool: str, version: str, path: str}]
        """
        installed = []
        
        if not self.bin_dir.exists():
            return installed
        
        # Scan bin directory
        for tool_dir in self.bin_dir.iterdir():
            if tool_dir.is_dir() and not tool_dir.name.startswith('.'):
                tool_name = tool_dir.name
                
                # Scan versions
                for version_dir in tool_dir.iterdir():
                    if version_dir.is_dir():
                        installed.append({
                            'tool': tool_name,
                            'version': version_dir.name,
                            'path': str(version_dir)
                        })
        
        return installed
    
    def get_tool_path(self, tool: str, version: str) -> Optional[Path]:
        """Get path ke installed tool.
        
        Args:
            tool: Nama tool
            version: Versi tool
        
        Returns:
            Optional[Path]: Path ke tool atau None jika tidak ada
        """
        tool_path = self.bin_dir / tool / version
        
        if tool_path.exists() and tool_path.is_dir():
            return tool_path
        
        return None
    
    def is_tool_installed(self, tool: str, version: str) -> bool:
        """Cek apakah tool sudah terinstall.
        
        Args:
            tool: Nama tool
            version: Versi tool
        
        Returns:
            bool: True jika sudah terinstall
        """
        return self.get_tool_path(tool, version) is not None
    
    def get_download_url(self, tool: str, version: str) -> Optional[str]:
        """Get download URL untuk tool tertentu.
        
        Args:
            tool: Nama tool
            version: Versi tool
        
        Returns:
            Optional[str]: URL atau None jika tidak ditemukan
        """
        if tool not in self.tools_config:
            logger.warning(f"Tool '{tool}' not found in config")
            return None
        
        tool_versions = self.tools_config[tool]
        
        if not isinstance(tool_versions, dict):
            logger.warning(f"Invalid config format for tool '{tool}'")
            return None
        
        if version not in tool_versions:
            logger.warning(f"Version '{version}' not found for tool '{tool}'")
            return None
        
        return tool_versions[version]
    
    def download_tool(self, tool: str, version: str) -> Optional[Path]:
        """Download tool dari URL.
        
        Args:
            tool: Nama tool
            version: Versi tool
        
        Returns:
            Optional[Path]: Path ke downloaded file atau None jika gagal
        """
        url = self.get_download_url(tool, version)
        
        if not url:
            return None
        
        # Determine filename from URL
        filename = url.split('/')[-1]
        download_path = self.bin_dir / f".downloads" / filename
        
        # Create downloads directory
        download_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Downloading {tool} {version} from {url}")
            
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(download_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                logger.info(f"Downloaded: {progress:.1f}%")
            
            logger.info(f"Download complete: {download_path}")
            return download_path
        
        except requests.RequestException as e:
            logger.error(f"Download error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return None
    
    def extract_tool(self, archive_path: Path, tool: str, version: str) -> bool:
        """Extract archive ke bin directory.
        
        Args:
            archive_path: Path ke archive file
            tool: Nama tool
            version: Versi tool
        
        Returns:
            bool: True jika berhasil
        """
        target_dir = self.bin_dir / tool / version
        temp_extract_dir = self.bin_dir / f".extract_{tool}_{version}"
        
        try:
            # Create temp extract directory
            temp_extract_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Extracting {archive_path} to {temp_extract_dir}")
            
            # Detect archive type and extract
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
            
            elif archive_path.suffix in ['.gz', '.xz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(temp_extract_dir)
            
            else:
                logger.error(f"Unsupported archive format: {archive_path.suffix}")
                return False
            
            # Move extracted content to target directory
            # Handle case where archive contains a single root directory
            extracted_items = list(temp_extract_dir.iterdir())
            
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                # Archive has single root dir, move its contents
                source_dir = extracted_items[0]
            else:
                # Archive has multiple items at root, use temp dir itself
                source_dir = temp_extract_dir
            
            # Ensure target parent exists
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            
            # Move to final location
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            shutil.move(str(source_dir), str(target_dir))
            
            logger.info(f"Extracted successfully to {target_dir}")
            
            # Cleanup temp directory
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            
            return True
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            
            # Cleanup on failure
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            
            return False
    
    def setup_tool(self, tool: str, version: str, force: bool = False) -> Tuple[bool, str]:
        """Setup tool: download + extract.
        
        Args:
            tool: Nama tool
            version: Versi tool
            force: Force reinstall jika sudah ada
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Check if already installed
        if self.is_tool_installed(tool, version) and not force:
            path = self.get_tool_path(tool, version)
            return True, f"{tool} {version} sudah terinstall di {path}"
        
        # Check if tool exists in config
        url = self.get_download_url(tool, version)
        if not url:
            available = self.list_available_tools()
            if tool in available:
                versions = ', '.join(available[tool])
                return False, f"Versi '{version}' tidak ditemukan. Versi tersedia: {versions}"
            else:
                return False, f"Tool '{tool}' tidak ditemukan dalam konfigurasi"
        
        logger.info(f"Setting up {tool} {version}")
        
        # Download
        archive_path = self.download_tool(tool, version)
        if not archive_path:
            return False, "Gagal mendownload tool"
        
        # Extract
        if not self.extract_tool(archive_path, tool, version):
            return False, "Gagal mengekstrak tool"
        
        # Cleanup download
        try:
            archive_path.unlink()
        except:
            pass
        
        tool_path = self.get_tool_path(tool, version)
        return True, f"Berhasil setup {tool} {version} di {tool_path}"
    
    def remove_tool(self, tool: str, version: str) -> Tuple[bool, str]:
        """Remove installed tool.
        
        Args:
            tool: Nama tool
            version: Versi tool
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        tool_path = self.get_tool_path(tool, version)
        
        if not tool_path:
            return False, f"{tool} {version} tidak ditemukan"
        
        try:
            shutil.rmtree(tool_path)
            logger.info(f"Removed {tool} {version} from {tool_path}")
            return True, f"Berhasil menghapus {tool} {version}"
        
        except Exception as e:
            logger.error(f"Error removing tool: {e}")
            return False, f"Gagal menghapus tool: {str(e)}"


# Singleton instance
_tools_manager_instance = None


def get_tools_manager() -> ToolsManager:
    """Get singleton instance of ToolsManager.
    
    Returns:
        ToolsManager: Instance
    """
    global _tools_manager_instance
    if _tools_manager_instance is None:
        _tools_manager_instance = ToolsManager()
    return _tools_manager_instance
