from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from celery.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute='*/1')), name="task_notify", ignore_result=True)
def task_notify():
    """
    Saves latest image from Flickr
    """
    context = [
        ('fieldname', 'Field description'),
        ('fieldname2', 'Field description'),
    ]
    update_template_context("ks001", 'your email subject', context)
    logger.info("Saved ")
