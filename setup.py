from setuptools import setup
from Cython.Build import cythonize

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

setup(
	ext_modules = cythonize(["rulebook/templatetags/*.pyx"], annotate=True)
)