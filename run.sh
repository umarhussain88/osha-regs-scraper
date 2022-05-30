#!/bin/sh

export LC_ALL=en_US.utf-8
pipenv run python3 main.py oshaSpider
pipenv run python3 main.py StandardRegsSpider
pipenv run python3 main.py export-azure
pipenv run python3 main.py clean-phmsa-regulations