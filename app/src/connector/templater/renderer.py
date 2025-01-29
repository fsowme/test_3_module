import logging

from jinja2 import Template

logger = logging.getLogger(__name__)


def render(pattern, **kwargs):
    tmpl = Template(pattern)
    try:
        rendered = tmpl.render(**kwargs)
    except Exception as error:
        logger.error('Template render error: %s', error)
        raise
    return rendered
