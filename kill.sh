kill -9 `ps -ef | grep app.py | grep -v grep | awk '{print $2}'`

