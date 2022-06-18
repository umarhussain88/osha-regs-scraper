# !/bin/sh

export LC_ALL=en_US.utf-8
./local/bin/pipenv run python3 main.py oshaSpider
./local/bin/pipenv run python3 main.py StandardRegsSpider
./local/bin/pipenv run python3 main.py phmsa_RegulationsSpider
./local/bin/pipenv run python3 main.py clean-phmsa-regulations
./local/bin/pipenv run python3 main.py export-azure
