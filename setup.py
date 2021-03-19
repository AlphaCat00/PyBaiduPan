import setuptools
import pyBaiduPan

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyBaiduPan",
    version=pyBaiduPan.__version__,
    author="AlphaCat",
    author_email="00.alpha.cat@gmail.com",
    description="A python client for Baidu Pan",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlphaCat00/PyBaiduPan",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'BdPan = pyBaiduPan.bdpan:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['baidu pcs', 'baidu yun', 'baidu pan', 'baidu netdisk',
              'baidu cloud storage', 'baidu personal cloud storage'],
    python_requires='>=3.6',
    install_requires=['Flask>=1.0', 'requests>=2.22.0']
)
