#!/bin/sh

python3.6 -m aida.api.textloader --users /opt/AIDA/python/test/data/users.txt --config config.json
python3.6 -m aida.ldcrepo.textloader --dirs /opt/AIDACorpora --config config.json
