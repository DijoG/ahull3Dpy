import numpy as np
from scipy.spatial import KDTree

# Import the compiled C++ module
try:
    import ahull3Dpy_core as core
except ImportError:
    raise ImportError(
        "Could not import ahull3Dpy_core. Please compile the C++ extension first.\n"
        "Run: python setup.py build_ext --inplace"
    )

def ahull3D(points, alpha, input_truth=None, volume=False):
    """
    Fast 3D Alpha Hull with Label Propagation
    """
    # Input validation
    if not isinstance(points, np.ndarray):
        points = np.array(points, dtype=np.float64)
    
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("Points must be Nx3 matrix")
    
    if alpha < 0:
        raise ValueError("Alpha must be non-negative")
    
    if input_truth is None:
        input_truth = np.ones(points.shape[0], dtype=np.float64)
        return_labels = False
    else:
        if len(input_truth) != points.shape[0]:
            raise ValueError("input_truth length must match points")
        input_truth = np.array(input_truth, dtype=np.float64)
        return_labels = True
    
    # Call C++ function
    vertices, vertex_labels, volume_data = core.fas_cpp_with_labels(
        points.astype(np.float64), 
        alpha, 
        input_truth, 
        volume
    )
    
    nvertices = vertices.shape[0]
    if nvertices == 0:
        print("The alpha shape is empty.")
        return None
    
    # Create faces
    faces = np.arange(nvertices).reshape(-1, 3)
    
    # Create mesh structure
    mesh = {
        'vertices': vertices,
        'faces': faces,
        'alpha': alpha
    }
    
    # Add labels if provided
    if return_labels:
        tree = KDTree(points)
        distances, indices = tree.query(vertices)
        final_labels = input_truth[indices]
        
        mesh['input_truth'] = final_labels
        mesh['face_truth'] = final_labels[faces]
    
    if volume:
        mesh['volume'] = volume_data
    
    return mesh

def plot_ahull3D(mesh, color='lightblue', opacity=0.7):
    """Plot the alpha hull using matplotlib"""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        vertices = mesh['vertices']
        faces = mesh['faces']
        
        tri = Poly3DCollection([vertices[face] for face in faces], 
                               alpha=opacity, facecolor=color)
        ax.add_collection3d(tri)
        
        ax.set_xlim(vertices[:, 0].min(), vertices[:, 0].max())
        ax.set_ylim(vertices[:, 1].min(), vertices[:, 1].max())
        ax.set_zlim(vertices[:, 2].min(), vertices[:, 2].max())
        
        plt.show()
        
    except ImportError:
        print("matplotlib not available for visualization")