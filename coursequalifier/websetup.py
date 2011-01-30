"""Setup the coursequalifier application"""
import logging

from coursequalifier.config.environment import load_environment
from coursequalifier.model import meta

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup coursequalifier here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    meta.metadata.create_all(bind=meta.engine)
