# Foobar

python_logrotate is a script for rotating logs with basic set of functions.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Usage
For now you can specify next options in config.json file (they a similar to Linux logrotate script):
* path - full path to the file.
* file_size : 100KB, 1MB, 1GB - rotate only if log file is bigger then size. Accepts human-friendly numbers.
* rotation : integer - rotate log file count times before remove.
* compress : true/false - compress olg files with gzip.
* copytruncate : true/false - truncate the original log file in place after creating a copy.

```bash
python3 logrotate.py -c config.json
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
