# ahull3Dpy

Fast 3D Alpha Hull with Label Propagation

Python port of the [ahull3D](https://github.com/DijoG/ahull3D) R package. Computes 3D alpha shapes with label propagation from input points to hull vertices and faces. Optimized for tree segmentation and LiDAR point cloud processing.

## Features

- 🚀 Fast C++ core using CGAL
- 🏷️ Label propagation: Input point IDs → hull vertices → faces
- 📦 Easy installation with pre-compiled wheels
- 🔄 Drop-in replacement for ahull3D R package functionality

## Installation

```bash
pip install ahull3Dpy
```
## Usage

### Basic Usage
```python
import numpy as np
from ahull3Dpy import ahull3D

# Generate random 3D points
pts = np.random.randn(100, 3)
pts = pts / np.linalg.norm(pts, axis=1)[:, np.newaxis]

# Compute alpha hull
mesh = ahull3D(pts, alpha=0.5)

print(f"Vertices: {mesh['vertices'].shape}")  # (M, 3)
print(f"Faces: {mesh['faces'].shape}")        # (F, 3)
```
### With Labels (point IDs)

The input_truth parameter propagates labels (e.g., tree IDs from LAS files) from input points to the hull vertices and faces:

```python
import numpy as np
from ahull3Dpy import ahull3D

# Generate points with labels (e.g., tree IDs from LiDAR data)
pts = np.random.randn(100, 3)
pts = pts / np.linalg.norm(pts, axis=1)[:, np.newaxis]

# Point IDs (e.g., tree IDs from LAS file)
# In real LiDAR data, this would be the 'pid' or 'treeID' field
labels = np.array([1, 2, 3])  # Tree IDs
labels = np.repeat(labels, [33, 33, 34])  # Assign to points

# Compute alpha hull with label propagation
mesh = ahull3D(pts, alpha=0.5, input_truth=labels)

# Access propagated labels
print(f"Vertex labels: {mesh['input_truth']}")     # Labels for each hull vertex
print(f"Face labels: {mesh['face_truth']}")        # Labels for each face (3 labels per face)
print(f"Unique labels: {np.unique(mesh['input_truth'])}")  # Should be [1, 2, 3]
```
## Visualize

```python
from ahull3Dpy import plot_ahull3D

plot_ahull3D(mesh, color='lightblue', opacity=0.7)
```