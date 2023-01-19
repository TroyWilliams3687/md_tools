# md_tools

## Introduction


## Installation and Configuration


### SCONS

Using scons to build the virtual environment and set everything up:

```bash
scons
```

Remove the virtual environment:

```bash
scons remove
```

> For more information on SCONS, see [scons.md](scons.md).


### Files

- `.gitignore`
    - basic boilerplate for `.gitignore` cobbled together from other sources with some things removed. A good starting point.

- `dev-requirements.txt`
    - The requirements file template for development dependencies. The makefiles are setup to read any `*requirements.txt` at the root of the repo. This gives you the ability to organize the dependencies any way you see fit. The basics in this repo divides items your project needs (i.e. `requirements.txt`) from development dependencies like linters.
    - NOTE: This isn't required if you are not creating a package where the required modules can be different.

- `requirements.txt`
    - Same as the `dev-requirements.txt`, just for things your project/package needs.

- `pyproject.toml`
    - a basic template TOML file used in the package build process. This is only required if you project is a package or will be treated like a package. It is boilerplate and doesn't require any changes or modifications.
    - NOTE: This isn't required if you are not creating a package.

- `setup.py`
    - The `setup.py` is modified to work with `pyproject.toml`. As such, it is a boilerplate file that only requires to be in the root folder. Nothing in this file needs to be modified.
    - NOTE: This isn't required if you are not creating a package.

- `setup.cfg`
    - The new way to build python packages. The `setup.cfg` is an excellent template and can easily be adapted to various projects.
    - NOTE: This isn't required if you are not creating a package.

- `.sconstruct.ini`
    - The ini file should be created from the `sample.sconstruct.ini` and contains the path to the main python binary to use for this project. It is not the path to the binary located in the virtual environment.


>NOTE: For a basic project, only the `.gitignore` and `requirements.txt` files should be used.


## Usage

## License

[MIT](https://choosealicense.com/licenses/mit/)

