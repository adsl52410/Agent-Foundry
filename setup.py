from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="afm",
    version="0.1.0",
    description="Agent Foundry Manager: LLM Agent toolkit manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Agent Foundry Contributors",
    url="https://github.com/neillu/Agent-Foundry",
    project_urls={
        "Source": "https://github.com/neillu/Agent-Foundry",
        "Issues": "https://github.com/neillu/Agent-Foundry/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["click", "requests", "importlib_metadata", "rich"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": ["afm=afm.cli:main"]},
)
