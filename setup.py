import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt") as f:
	install_requires = f.readlines()

# get version
env = {}
with open("pybryt/version.py") as f:
	exec(f.read(), env)
version = env["__version__"]

setuptools.setup(
	name = "pybryt",
	version = version,
	author = "Chris Pyles",
	author_email = "pybryt-support@microsoft.com",
	description = "Python auto-assessment library",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/microsoft/pybryt",
	license = "MIT",
	packages = setuptools.find_packages(exclude=["test"]),
	classifiers = [
		"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	],
	install_requires=install_requires,
	entry_points={
		"console_scripts": ["pybryt=pybryt.cli:cli"]
	},
)
