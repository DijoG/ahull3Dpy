from setuptools import setup, Extension
import pybind11
import os
import sys
import subprocess

def get_cgal_include():
    """Find CGAL include path on different platforms"""
    # Try environment variable first
    env_path = os.environ.get('CGAL_INCLUDE_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Common paths
    paths = [
        '/usr/include',
        '/usr/local/include',
        '/opt/homebrew/include',
        '/usr/include/x86_64-linux-gnu',
    ]
    
    for path in paths:
        cgal_path = os.path.join(path, 'CGAL')
        if os.path.exists(cgal_path):
            return path
    
    # Try pkg-config
    try:
        result = subprocess.run(
            ['pkg-config', '--cflags-only-I', 'CGAL'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for flag in result.stdout.split():
                if flag.startswith('-I'):
                    return flag[2:]
    except:
        pass
    
    # Fallback: let the compiler find it
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