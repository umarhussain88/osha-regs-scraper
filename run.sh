#!/bin/sh

export LC_ALL=en_US.utf-8
/usr/local/bin/pipenv run python3 main.py oshaSpider
/usr/local/bin/pipenv run python3 main.py StandardRegsSpider
/usr/local/bin/pipenv run python3 main.py export-azure