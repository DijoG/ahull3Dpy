from setuptools import setup, Extension
import pybind11
import sys
import os

def get_cgal_include():
    """Find CGAL include path on different platforms"""
    
    # First check environment variable (set by cibuildwheel or user)
    env_path = os.environ.get('CGAL_INCLUDE_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Platform-specific paths
    if sys.platform == 'win32':
        # Windows: vcpkg default paths
        paths = [
            'C:/vcpkg/installed/x64-windows/include',
            'D:/vcpkg/installed/x64-windows/include',
        ]
        # Check GitHub Actions workspace path
        github_workspace = os.environ.get('GITHUB_WORKSPACE')
        if github_workspace:
            paths.insert(0, os.path.join(github_workspace, 'vcpkg/installed/x64-windows/include'))
        
        # Check conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            paths.insert(0, os.path.join(conda_prefix, 'Library/include'))
        
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
                
    elif sys.platform == 'darwin':
        # macOS: Homebrew paths
        paths = [
            '/opt/homebrew/include',  # Apple Silicon
            '/usr/local/include',      # Intel
        ]
        # Check conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            paths.insert(0, os.path.join(conda_prefix, 'include'))
        
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
                
    else:  # Linux
        # Ubuntu/Debian paths
        paths = [
            '/usr/include',
            '/usr/local/include',
            '/usr/include/x86_64-linux-gnu',
        ]
        # Check conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            paths.insert(0, os.path.join(conda_prefix, 'include'))
        
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
    
    # If CGAL not found, print helpful message
    print("=" * 60)
    print("WARNING: CGAL not found!")
    print("Please install CGAL before building:")
    if sys.platform == 'win32':
        print("  Windows: vcpkg install cgal:x64-windows")
        print("  Or: conda install -c conda-forge cgal")
        print("  Set CGAL_INCLUDE_PATH to the include directory")
    elif sys.platform == 'darwin':
        print("  macOS: brew install cgal eigen")
        print("  Or: conda install -c conda-forge cgal")
    else:
        print("  Ubuntu/Debian: sudo apt-get install libcgal-dev eigen3-dev python3-dev")
        print("  RHEL/CentOS: sudo yum install cgal-devel eigen3-devel python3-devel")
        print("  Or: conda install -c conda-forge cgal")
    print("=" * 60)
    return ''

def get_compile_args():
    """Get platform-specific compile arguments"""
    if sys.platform == 'win32':
        return ['/std:c++17', '/O2', '/EHsc']
    else:
        return ['-std=c++17', '-O3', '-Wall']

def get_libraries():
    """Get platform-specific libraries to link"""
    if sys.platform == 'win32':
        # Windows needs GMP and MPFR for CGAL
        # CGAL itself is header-only, but it depends on these
        libraries = ['gmp', 'mpfr']
        
        # Check if we're in a conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            # In conda, the libraries might have different names
            lib_dir = os.path.join(conda_prefix, 'Library/lib')
            if os.path.exists(lib_dir):
                # Check if conda uses different naming
                if os.path.exists(os.path.join(lib_dir, 'libgmp.lib')):
                    return ['libgmp', 'libmpfr']
                elif os.path.exists(os.path.join(lib_dir, 'gmp.lib')):
                    return ['gmp', 'mpfr']
        
        return libraries
    else:
        # Linux/macOS: CGAL is header-only, no linking needed
        return []

def get_library_dirs():
    """Get platform-specific library directories"""
    library_dirs = []
    
    if sys.platform == 'win32':
        # Check environment variable first
        env_path = os.environ.get('GMP_LIBRARY_PATH')
        if env_path and os.path.exists(env_path):
            library_dirs.append(env_path)
        
        # Check vcpkg paths
        paths = [
            'C:/vcpkg/installed/x64-windows/lib',
            'D:/vcpkg/installed/x64-windows/lib',
        ]
        github_workspace = os.environ.get('GITHUB_WORKSPACE')
        if github_workspace:
            paths.insert(0, os.path.join(github_workspace, 'vcpkg/installed/x64-windows/lib'))
        
        for path in paths:
            if os.path.exists(path):
                library_dirs.append(path)
        
        # Check conda environment
        conda_prefix = os.environ.get('CONDA_PREFIX')
        if conda_prefix:
            conda_lib = os.path.join(conda_prefix, 'Library/lib')
            if os.path.exists(conda_lib):
                library_dirs.append(conda_lib)
    
    return library_dirs

# Get CGAL include path
cgal_include = get_cgal_include()
if not cgal_include:
    # Try to find CGAL using pkg-config on Linux
    if sys.platform != 'win32':
        try:
            import subprocess
            result = subprocess.run(
                ['pkg-config', '--cflags-only-I', 'CGAL'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for flag in result.stdout.split():
                    if flag.startswith('-I'):
                        cgal_include = flag[2:]
                        if os.path.exists(os.path.join(cgal_include, 'CGAL')):
                            print(f"Found CGAL via pkg-config: {cgal_include}")
                            break
        except:
            pass

ext_modules = [
    Extension(
        'ahull3Dpy_core',
        sources=['src/ahull3Dpy_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            cgal_include,
        ],
        library_dirs=get_library_dirs(),
        libraries=get_libraries(),
        language='c++',
        extra_compile_args=get_compile_args(),
    ),
]

# Read README for long description
long_description = ""
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = "Fast 3D Alpha Hull with Label Propagation"

setup(
    name='ahull3Dpy',
    version='1.0.0',
    description='Fast 3D Alpha Hull with Label Propagation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Gergo Dioszegi',
    author_email='dijogergo@gmail.com',
    url='https://github.com/DijoG/ahull3Dpy',
    packages=['ahull3Dpy'],
    ext_modules=ext_modules,
    install_requires=[
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'pybind11>=2.10.0',
    ],
    python_requires='>=3.7',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)