from setuptools import setup, Extension
import pybind11
import os
import sys

def get_cgal_include():
    """Get CGAL include path for different platforms"""
    if sys.platform == 'win32':
        return os.environ.get('CGAL_INCLUDE_PATH', 'C:/vcpkg/installed/x64-windows/include')
    elif sys.platform == 'darwin':
        # macOS: try Homebrew paths
        paths = ['/opt/homebrew/include', '/usr/local/include']
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
        return '/opt/homebrew/include'  # default
    else:  # Linux
        return '/usr/include'

ext_modules = [
    Extension(
        'ahull3Dpy_core',
        sources=['src/ahull3Dpy_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            get_cgal_include(),
        ],
        language='c++',
        extra_compile_args=['-std=c++17', '-O3'],
        libraries=['CGAL'] if sys.platform != 'win32' else [],
    ),
]

setup(
    name='ahull3Dpy',
    version='1.0.0',
    description='Fast 3D Alpha Hull with Label Propagation',
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
)