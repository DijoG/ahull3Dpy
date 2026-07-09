# ahull3Dpy

Fast 3D Alpha Hull with Label Propagation

[![PyPI version](https://badge.fury.io/py/ahull3Dpy.svg)](https://badge.fury.io/py/ahull3Dpy)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/Windows-passing-brightgreen.svg)]()
[![Linux](https://img.shields.io/badge/Linux-passing-brightgreen.svg)]()
[![macOS](https://img.shields.io/badge/macOS-passing-brightgreen.svg)]()

Python port of the [ahull3D](https://github.com/DijoG/ahull3D) R package. Computes 3D alpha shapes with **label propagation** from input point IDs to hull vertices and faces. Optimized for tree segmentation and LiDAR point cloud processing.

## Features

- 🚀 Fast C++ core using CGAL
- 🏷️ Label propagation: Input point IDs → hull vertices → faces
- 📦 Easy installation with pre-compiled wheels
- 🔄 Drop-in replacement for ahull3D R package functionality

## Installation

### From PyPI (Recommended)
```bash
pip install ahull3Dpy
```
### From GitHub (Development Version)
```bash
pip install git+https://github.com/DijoG/ahull3Dpy.git
```
## Usage

### Basic Usage (No Labels)
```python
import numpy as np
from ahull3Dpy import ahull3D

# Generate random 3D points on a sphere
pts = np.random.randn(100, 3)
pts = pts / np.linalg.norm(pts, axis=1)[:, np.newaxis]

# Compute alpha hull
mesh = ahull3D(pts, alpha=0.5)

print(f"Vertices: {mesh['vertices'].shape}")  # (M, 3)
print(f"Faces: {mesh['faces'].shape}")        # (F, 3)
print(f"Alpha: {mesh['alpha']}")              # 0.5
```
### With Point IDs (Labels)

This is the main feature of ahull3Dpy! The input_truth parameter takes point IDs (e.g., tree IDs from LiDAR data) and propagates them from input points to hull vertices and faces.

```python
import numpy as np
from ahull3Dpy import ahull3D

# Generate points with point IDs (e.g., tree IDs from LAS files)
pts = np.random.randn(100, 3)
pts = pts / np.linalg.norm(pts, axis=1)[:, np.newaxis]

# Point IDs from your data (e.g., 'pid' or 'treeID' field in LAS)
# In real LiDAR data, this would be read from the LAS file
point_ids = np.array([1, 2, 3])  # Tree IDs
point_ids = np.repeat(point_ids, [33, 33, 34])  # Assign to points

# Compute alpha hull with label propagation
# The point IDs are propagated from input points → hull vertices → faces
mesh = ahull3D(pts, alpha=0.5, input_truth=point_ids)

# Access propagated labels
print(f"Vertex labels: {mesh['input_truth']}")     # Point IDs for each hull vertex
print(f"Face labels: {mesh['face_truth']}")        # Point IDs for each face vertex
print(f"Unique point IDs: {np.unique(mesh['input_truth'])}")  # Should be [1, 2, 3]
```
### WIth Volume Computation
```python
# Compute hull with volume
mesh = ahull3D(pts, alpha=0.8, volume=True)
print(f"Volume: {mesh['volume']}")  
# Output: {'exterior': 27.87, 'interior': 16.46}
```
### Visualize
```python
from ahull3Dpy import plot_ahull3D

plot_ahull3D(mesh, color='lightblue', opacity=0.7)
```
## Building From Source

### Ubuntu/Debian
```bash
sudo apt-get install libcgal-dev libeigen3-dev libgmp-dev libmpfr-dev python3-dev
pip install -e .
```
### macOS
```bash
brew install cgal eigen gmp mpfr
pip install -e .
```
### Windows
```bash
vcpkg install cgal:x64-windows gmp:x64-windows mpfr:x64-windows
pip install -e .
```
