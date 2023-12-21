## namafilenya.wsgi ##
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/FlaskApp/")

from __init__final import app as application
application.secret_key = "secret_key"
