
#-*- encoding: utf-8 -*-
from distutils.core import setup

# Load in babel support, if available.
try:
    from babel.messages import frontend as babel

    cmdclass = {"compile_catalog": babel.compile_catalog,
                "extract_messages": babel.extract_messages,
                "init_catalog": babel.init_catalog,
                "update_catalog": babel.update_catalog, }
except ImportError:
    cmdclass = {}

setup(name="django-money",
      version="0.3.3.1",
      description="Adds support for using money and currency fields in django models and forms. Uses py-moneyed as the money implementation.",
      url="https://github.com/jakewins/django-money",
      maintainer='Greg Reinbach',
      maintainer_email='greg@reinbach.com', 
      packages=["djmoney",
                "djmoney.forms",
                "djmoney.models"],
      install_requires=['setuptools',
                        'Django >= 1.5.1',
                        'py-moneyed > 0.4'],
      package_dir={"": ""},
      cmdclass=cmdclass,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django", ])
