import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort

from coursequalifier.lib.base import BaseController, render

log = logging.getLogger(__name__)

class WelcomeController(BaseController):
    def index(self):
        return render('/welcome.mako')
