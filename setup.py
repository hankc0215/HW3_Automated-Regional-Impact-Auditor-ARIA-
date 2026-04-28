from setuptools import setup, find_packages

setup(
    name="aria-v7-sar-sensor-fusion",
    version="1.0.0",
    description="ARIA V7 SAR Sensor Fusion for Flood Detection",
    author="ARIA Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "rasterio>=1.2.0",
        "rioxarray>=0.11.0",
        "pystac-client>=0.3.0",
        "planetary-computer>=0.4.0",
        "stackstac>=0.5.0",
        "xarray>=0.20.0",
        "shapely>=1.8.0",
        "geopandas>=0.10.0",
    ],
)
