#!/usr/bin/env python3
"""
Setup script for CRM Automation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='crm-automation',
    version='0.1.0',
    description='CRM data extraction and report generation automation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pierre Bisiaux',
    author_email='bisiaux.pierre@outlook.fr',
    url='https://github.com/yourusername/rs_crm_automation',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.11',
    install_requires=[
        'selenium>=4.35.0',
        'python-pptx>=1.0.2',
        'beautifulsoup4>=4.12.3',
        'lxml>=5.3.0',
        'requests>=2.32.3',
        'python-dotenv>=1.0.1',
        'python-dateutil>=2.9.0',
        'colorlog>=6.9.0',
        'typing-extensions>=4.12.2',
    ],
    extras_require={
        'dev': [
            'pytest>=8.3.5',
            'pytest-cov>=6.0.0',
            'flake8>=7.1.1',
        ],
    },
    entry_points={
        'console_scripts': [
            'crm-automation=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='crm automation selenium web-scraping reporting',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/rs_crm_automation/issues',
        'Source': 'https://github.com/yourusername/rs_crm_automation',
    },
)
