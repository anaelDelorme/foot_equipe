from setuptools import setup, find_packages

setup(
    name="st_draggable_teams",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.10.0",
    ],
)