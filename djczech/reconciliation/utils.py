from django.conf import settings

from djczech.reconciliation.sql import *
from djtools.utils.mail import send_mail
from djtools.fields import NOW

STATUS=settings.IMPORT_STATUS

# move this to djtools
def handle_uploaded_file(f):
    ts = NOW.strftime("%Y%m%d%H%M%S%f")
    phile = "{}{}.csv".format(settings.CHEQUE_DATA_DIR, ts)
    destination = open(phile, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    return phile

def recce_cheques(request, session, import_date):
    # email distribution
    if settings.DEBUG:
        TO_LIST = [settings.ADMINS[0][1],]
    else:
        TO_LIST = [request.user.email,]
    # Drop the temporary tables, just in case
    try:
        session.execute("DROP TABLE tmp_voida")
    except:
        pass
    try:
        session.execute("DROP TABLE tmp_voidb")
    except:
        pass

    # Populate void temp table A
    voida = session.execute(TMP_VOID_A)
    # Populate void temp table B
    voidb = session.execute(TMP_VOID_B)

    # select * from temp table B and send the data to the business office
    objs = session.execute(SELECT_VOID_B)

    send_mail(
        request, TO_LIST,
        "[DJ Cheque] Voided checks", settings.ADMINS[0][1],
        "reconciliation/cheque/email.html",
        {"title":"Voided checks","objs":objs}, settings.MANAGERS
    )

    # set reconciliation status to 'v'
    session.execute(UPDATE_RECONCILIATION_STATUS)

    # Find the duplicate check numbers and update those as 's'uspicious

    # Drop the temporary tables, just in case
    try:
        session.execute("DROP TABLE tmp_maxbtchdate")
    except:
        pass
    try:
        session.execute("DROP TABLE tmp_DupCkNos")
    except:
        pass
    try:
        session.execute("DROP TABLE tmp_4updtstatus")
    except:
        pass

    # select import_date and stick it in a temp table, for some reason
    session.execute(SELECT_CURRENT_BATCH_DATE)

    # Select the duplicates
    duplicate_check_numbers = session.execute(
        SELECT_DUPLICATES_1(import_date=import_date)
    )
    # Selected for updating
    for_update_status = session.execute(
        SELECT_FOR_UPDATING(import_date=import_date, status=STATUS)
    )
    # Update cheque status to 's'uspictious
    update_status = session.execute(UPDATE_STATUS)

    # Send the records selected to be updated to the business office
    objs = session.execute(SELECT_RECORDS_FOR_UPDATE)

    send_mail(
        request, TO_LIST,
        "[DJ Cheque] Updated checks", settings.ADMINS[0][1],
        "reconciliation/cheque/email.html",
        request, settings.MANAGERS
    )

    # Send duplicate records to the business office
    objs = session.execute(
        SELECT_DUPLICATES_2(import_date=import_date)
    )

    send_mail(
        request, TO_LIST,
        "[DJ Cheque] Duplicate checks", settings.ADMINS[0][1],
        "reconciliation/cheque/email.html",
        {"title":"Duplicate checks","objs":objs}, settings.MANAGERS
    )

    # Find the cleared CheckNos and update gltr_rec as 'r'econciled
    # and ccreconjb_rec as 'ar' (auto-reconciled)

    # Drop the temporary table, just in case
    try:
        session.execute("DROP TABLE tmp_reconupdta")
    except:
        pass

    # Find the cleared Check Numbers
    select_reconciled = session.execute(
        SELECT_CLEARED_CHEQUES(import_date=import_date)
    )
    # Set gltr_rec as 'r'econciled
    update_reconciled = session.execute(UPDATE_RECONCILED)
    # Set ccreconjb_rec as 'ar' (auto-reconciled)
    update_status = session.execute(UPDATE_STATUS)
    # Send the results to business office
    objs = session.execute(SELECT_RECONCILIATED)

    send_mail(
        request, TO_LIST,
        "[DJ Cheque] Reconciled checks", settings.ADMINS[0][1],
        "reconciliation/cheque/email.html",
        {"title":"Reconciled checks","objs":objs}, settings.MANAGERS
    )
