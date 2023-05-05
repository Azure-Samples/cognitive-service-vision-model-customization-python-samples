import setuptools
from os import path

VERSION = '0.0.3'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()


setuptools.setup(name='cognitive-service-vision-model-customization-python-samples',
                 author='Ping Jin',
                 description='A sample code repo for model customization using Python for Cognitive Service for Vision.',
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 url='',
                 version=VERSION,
                 python_requires='>=3.7',
                 license='MIT',
                 keywords='vision datasets classification detection',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'requests',
                     'tqdm',
                     'azure-storage-blob',
                     'azure-cognitiveservices-vision-customvision',
                     'cffi'
                 ],
                 classifiers=[
                     'Development Status :: 4 - Beta',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                 ],
                 )
