from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger
from requests import request

from membership_manager.admin import filter_queryset, q_generator
from membership_manager.models import Membership

logger = get_task_logger(__name__)

@periodic_task(run_every=(crontab(minute='*/1')), name="task_notify", ignore_result=True)
def task_notify():
    """
    Saves latest image from Flickr
    """
    options = ['60','30','15','7','0']
    q = q_generator()
    logger.info(q)
    logger.info("Saved ")
