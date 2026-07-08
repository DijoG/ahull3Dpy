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
        
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
                
    elif sys.platform == 'darwin':
        # macOS: Homebrew paths
        paths = [
            '/opt/homebrew/include',  # Apple Silicon
            '/usr/local/include',      # Intel
        ]
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
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
    
    # If CGAL not found, print helpful message
    print("=" * 60)
    print("WARNING: CGAL not found!")
    print("Please install CGAL before building:")
    if sys.platform == 'win32':
        print("  Windows: vcpkg install cgal:x64-windows")
        print("  Set CGAL_INCLUDE_PATH to the include directory")
    elif sys.platform == 'darwin':
        print("  macOS: brew install cgal eigen")
    else:
        print("  Ubuntu/Debian: sudo apt-get install libcgal-dev eigen3-dev")
        print("  RHEL/CentOS: sudo yum install cgal-devel eigen3-devel")
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
    # CGAL is header-only on Linux and macOS
    if sys.platform == 'win32':
        # Windows might need CGAL libraries
        return ['CGAL']
    else:
        # Linux/macOS: CGAL is header-only
        return []

# Get CGAL include path
cgal_include = get_cgal_include()

ext_modules = [
    Extension(
        'ahull3Dpy_core',
        sources=['src/ahull3Dpy_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            cgal_include,
        ],
        language='c++',
        extra_compile_args=get_compile_args(),
        libraries=get_libraries(),
    ),
]

setup(
    name='ahull3Dpy',
    version='1.0.0',
    description='Fast 3D Alpha Hull with Label Propagation',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
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