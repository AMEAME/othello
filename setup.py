from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


setup(
  name        = 'othello app',
  cmdclass    = { 'build_ext': build_ext },
  ext_modules = [Extension('othello', ['othello.pyx'])]
)
