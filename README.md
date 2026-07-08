# ahull3Dpy

Fast 3D Alpha Hull with Label Propagation

Python port of the ahull3D R package.

## Installation

```bash
pip install ahull3Dpy
```
## Usage
```python
import numpy as np
from ahull3Dpy import ahull3D

# Generate points
pts = np.random.randn(100, 3)
mesh = ahull3D(pts, alpha=0.5)

# With labels
labels = np.array([1, 2])
labels = np.repeat(labels, 50)
mesh = ahull3D(pts, alpha=0.5, input_truth=labels)
```
