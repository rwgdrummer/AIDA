from setuptools import setup,find_packages
import os

setup(name='aida_media',
      version='0.1',
      description='media tools',
      url='http://gitlab/IADA',
      author='PAR Team',
      author_email='eric_robertson@partech.com',
      license='APL',
      packages=find_packages(exclude=["test"]),
      install_requires=['flask','flask_restful','matplotlib','nearpy','image-match','pillow==5.0.0','flask_sqlalchemy',
                        'scikit-image','scipy','Werkzeug','Flask-JWT','pycryptodome','passlib','pytesseract','urllib3',
                        'pymysql','sklearn','pikepdf','flask-cors','flask_jwt_extended','sqlalchemy_schemadisplay'],
      zip_safe=False)
