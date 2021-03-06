^[![Build status](https://github.com/sanskrit-coders/dict_curation/workflows/Python%20package/badge.svg)](https://github.com/sanskrit-coders/dict_curation/actions)
[![Build Status](https://travis-ci.org/sanskrit-coders/dict_curation.svg?branch=master)](https://travis-ci.org/sanskrit-coders/dict_curation)
[![Documentation Status](https://readthedocs.org/projects/dict_curation/badge/?version=latest)](http://dict_curation.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/dict_curation.svg)](https://badge.fury.io/py/dict_curation)

## dict curation

A package for curating doc file collections. Prominent features:

- Scrape texts off various sites, such as Wikisource. See example [here](https://github.com/sanskrit-coders/dict_curation/blob/master/curation_projects/misc/wikisource.py). (PS: Consider contributing to [raw_etexts repo](https://github.com/sanskrit/raw_etexts). )
- OCR some pdf with google drive. Automatically splits into 25 page bits and ocrs them individually. See usage example [here](https://github.com/sanskrit-coders/dict_curation/blob/master/curation_projects/pdf_tasks.py), function [here](https://github.com/sanskrit-coders/dict_curation/blob/master/dict_curation/pdf.py#L13).

## For users
* [Autogenerated Docs on readthedocs (might be broken)](http://dict_curation.readthedocs.io/en/latest/).
* Manually and periodically generated docs [here](https://sanskrit-coders.github.io/dict_curation/build/html/)
* For detailed examples and help, please see individual module files in this package.


## Installation or upgrade:
* `sudo pip install dict_curation -U`
* `sudo pip install git+https://github.com/sanskrit-coders/dict_curation/@master -U`
* [Web](https://pypi.python.org/pypi/dict_curation).


# For contributors

## Contact

Have a problem or question? Please head to [github](https://github.com/sanskrit-coders/dict_curation).

## Packaging

* ~/.pypirc should have your pypi login credentials.
```
python setup.py bdist_wheel
twine upload dist/* --skip-existing
```

## Build documentation
- sphinx html docs can be generated with `cd docs; make html`

## Testing
Run `pytest` in the root directory.

## Auxiliary tools
- [![Build Status](https://travis-ci.org/sanskrit-coders/dict_curation.svg?branch=master)](https://travis-ci.org/sanskrit-coders/dict_curation)
- [![Documentation Status](https://readthedocs.org/projects/dict_curation/badge/?version=latest)](http://dict_curation.readthedocs.io/en/latest/?badge=latest)
- [pyup](https://pyup.io/account/repos/github/sanskrit-coders/dict_curation/)