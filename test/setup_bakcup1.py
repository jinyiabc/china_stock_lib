# from setuptools import setup
#
# setup(
#     name = 'stock_data',
#     version = '0.0.10',
#     author = 'Alex JIN YI',
#     author_email = 'jinyiabc@gmail.com',
#     packages=['helper'],
#     url = 'https://github.com/jinyiabc/china_stock_lib.git',
#     py_modules = ['get_data', 'upload_github'],
#     description = 'install data in jupyter notebook',
#     install_requires = ['backtrader'],
# )

# pip  install setup_bakcup1.py
"""
from setuptools import setup

setup(
    name='mypackage',
    version='0.0.1',
    packages=['mypackage'],
    install_requires=[
        'requests',
        'importlib; python_version == "2.6"',
    ],
)

~/mypackage/
    pyproject.toml
    setup.cfg # or setup_bakcup1.py
    mypackage/__init__.py
    
Then, you need a builder, such as PyPA build which you can obtain via pip install build. After downloading it, invoke the builder:
python -m build
"""