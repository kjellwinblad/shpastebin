# ShPasteBin

This is a pastebin like web app consisting of a single Python 3
script without any other dependencies than Python 3.

## Usage

1. Run `python3 shpastebin.py --address 0.0.0.0 --port 8701`
2. Point your browser to http://localhost:8701

Create a new paste or access an existing one by changing the
location part of the URL (e.g. http://localhost:8701/this_is_the_name_of_my_new_paste).
Only English letters, numbers and underscores are accepted in paste names.

Run `python3 shpastebin.py -h` to see additional configuration options.

## License

MIT License