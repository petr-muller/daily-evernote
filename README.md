# daily-evernote
A simple utility showing a random Evernote note each day.

## Usage
```
# For today
$ python dailynote.py

# For a different date
$ python dailynote.py --date 2016-01-16
```

## Config file
The script authenticates against Evernote using developer tokens, read from a ```.daily-evernote``` file in the user's $HOME:
```
$ cat ~/.daily-evernote 
[account]
token = S=s17:U=1dce0a:E=15932d1732e:C=151db204580:P=1cd:A=en-devtoken:V=2:H=a594e48e84b33b16ad73077cec286863
```

## Travis CI Health
[![Build Status](https://travis-ci.org/petr-muller/daily-evernote.svg?branch=master)](https://travis-ci.org/petr-muller/daily-evernote)
