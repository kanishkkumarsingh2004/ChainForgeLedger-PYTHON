"""
ChainForgeLedger Setup

A complete blockchain platform library with PoW/PoS consensus, smart contracts, and DeFi applications.
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

# Get long description from README.md
long_description = read_file('README.md')

setup(
    name='ChainForgeLedger',
    version='1.0.0',
    description='A complete blockchain platform library with PoW/PoS consensus, smart contracts, and DeFi applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kanishk Kumar Singh',
    author_email='kanishkkumar2004@gmail.com',
    url='https://github.com/kanishk/ChainForgeLedger',
    license='MIT',
    
    # Packages to include
    packages=find_packages(),
    
    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'chainforgeledger = chainforgeledger.__main__:main',
        ],
    },
    
    # Package data
    package_data={
        'chainforgeledger': [
            '*.py',
        ],
    },
    
    # Requirements
    python_requires='>=3.8',
    install_requires=[],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'flake8>=3.0',
            'black>=21.0',
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Security :: Cryptography',
    ],
    
    keywords='blockchain cryptocurrency pow pos smart-contracts defi',
    zip_safe=False,
)
