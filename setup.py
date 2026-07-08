from setuptools import setup, Extension
import pybind11
import sys
import os

def get_cgal_include():
    """Find CGAL include path"""
    if sys.platform == 'linux':
        paths = [
            '/usr/include',
            '/usr/include/x86_64-linux-gnu',
            '/usr/local/include',
        ]
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
    elif sys.platform == 'darwin':
        paths = ['/opt/homebrew/include', '/usr/local/include']
        for path in paths:
            if os.path.exists(os.path.join(path, 'CGAL')):
                return path
    elif sys.platform == 'win32':
        return os.environ.get('CGAL_INCLUDE_PATH', 'C:/vcpkg/installed/x64-windows/include')
    return ''

ext_modules = [
    Extension(
        'ahull3Dpy_core',
        sources=['src/ahull3Dpy_core.cpp'],
        include_dirs=[
            pybind11.get_include(),
            get_cgal_include(),
        ],
        language='c++',
        extra_compile_args=['-std=c++17', '-O3', '-Wall'],
        # CGAL is header-only on Linux
        libraries=[] if sys.platform == 'linux' else ['CGAL'],
    ),
]

setup(
    name='ahull3Dpy',
    version='1.0.0',
    description='Fast 3D Alpha Hull with Label Propagation',
    author='Gergo Dioszegi',
    author_email='dijogergo@gmail.com',
    packages=['ahull3Dpy'],
    ext_modules=ext_modules,
    install_requires=[
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'pybind11>=2.10.0',
    ],
    python_requires='>=3.7',
)