"""Use to launch side celery app using wsgi."""

import os

from . import create_app

# Create an application instance that auxiliary processes such as Celery
# workers can use
app = create_app(os.environ.get('NEFARIO_CONFIG', 'production'), main=False)
