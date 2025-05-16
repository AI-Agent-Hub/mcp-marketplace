# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    "requests>=2.17.0"
]

setup(
    name="mcp_marketplace",   # Required
    version="0.0.2",    # Required
    description="MCP Marketplace Utils and API to Search MCP Tools and Registry of your MCP ModelContextProtocol Servers",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email="aihubadmin@126.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="MCP Marketplace,AI Agent Marketplace,API,AI Agent",
    packages=find_packages(where="src"),  # Required
    install_requires=install_requires,    # Required        
    package_dir={'': 'src'},
    package_data={'mcp_marketplace': ['*.txt', '*.json']
        , 'mcp_marketplace.data': ['*.txt', '*.json']
    },    
    python_requires=">=3.4",
    project_urls={
        "homepage": "http://www.deepnlp.org/store/ai-agent/mcp-server",
        "repository": "https://github.com/AI-Agent-Hub/mcp-Marketplace"
    },
)
