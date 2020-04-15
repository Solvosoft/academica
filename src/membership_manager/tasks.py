from django.utils import timezone

from membership_manager.task_utils import notify_invoice_expiration, invoice_creation, \
    membership_deactivating, membership_deactivating_membership, create_invoice_tool, generate_renew, inactive_renew, \
    update_last_daterenew
from membresias_codigosur.celery import app


@app.task
def task_invoice_creation():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=timezone.localtime(timezone.now())

    # Genero las facturas que están por vencerse
    invoice_creation(now)
    # genero las renovaciones de membresias gratuitas y envío el correo
    # genero las renovaciones de las membresias no gratuitas
    generate_renew(now)


@app.task
def task_notify_invoice_expiration():
    """
    For all pending invoice calc if notification needs to be send
    :return:
    """
    now=timezone.localtime(timezone.now())
    notify_invoice_expiration(now)

@app.task
def task_membership_deactivating_or_graceperiod():
    now=timezone.localtime(timezone.now())
    membership_deactivating(now)
    inactive_renew(now)

@app.task
def task_membership_deactivating_membership(id_membership, email):
    membership_deactivating_membership(id_membership, email)

@app.task
def task_create_invoice(id_renew):
    create_invoice_tool(id_renew)


@app.task
def update_last_daterenew_task():
    update_last_daterenew()
