#!/usr/bin/env python3
"""
ARIA v4.1 - Environment Verification Script
Verifies all required dependencies are properly installed
"""

import sys
import subprocess
import importlib

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"?? {package_name}: Installed")
        return True
    except ImportError:
        print(f"?? {package_name}: NOT installed")
        return False

def check_version(package_name):
    """Get package version"""
    try:
        result = subprocess.run([sys.executable, "-c", 
            f"import {package_name}; print({package_name}.__version__)"], 
            capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown"
    except:
        return "Unknown"

def main():
    """Main verification function"""
    print("ARIA v4.1 - Environment Verification")
    print("=" * 50)
    
    # Required packages
    required_packages = {
        'osmnx': 'osmnx',
        'networkx': 'networkx', 
        'geopandas': 'geopandas',
        'rasterio': 'rasterio',
        'matplotlib': 'matplotlib',
        'shapely': 'shapely',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    print("Checking required packages:")
    all_installed = True
    
    for package, import_name in required_packages.items():
        installed = check_package(package, import_name)
        if installed:
            version = check_version(import_name)
            print(f"   Version: {version}")
        else:
            all_installed = False
    
    print("\n" + "=" * 50)
    
    if all_installed:
        print("?? All required packages are installed!")
        print("Environment is ready for ARIA v4.1 analysis.")
        return 0
    else:
        print("?? Some packages are missing.")
        print("Install missing packages with:")
        print("pip install osmnx networkx geopandas rasterio matplotlib shapely pandas numpy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
