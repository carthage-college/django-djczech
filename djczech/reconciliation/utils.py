from django.conf import settings

from djczech.reconciliation.sql import *
from djtools.utils.mail import send_mail
from djtools.fields import NOW


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
    session.execute(TMP_VOID_A)
    # Populate void temp table B
    session.execute(TMP_VOID_B)

    # select * from temp table B and send the data to the business office
    select_voidb = session.execute(SELECT_VOID_B)

    if not settings.DEBUG:
        send_mail(
            request, TO_LIST,
            "[DJ Cheque] Voided checks", settings.ADMINS[0][1],
            "reconciliation/cheque/email.html",
            {"title":"Voided checks","objs":select_voidb}, settings.MANAGERS
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
    session.execute(SELECT_CURRENT_BATCH_DATE(import_date=import_date))

    # Select the duplicates
    duplicate_check_numbers = session.execute(
        SELECT_DUPLICATES_1(import_date=import_date)
    )
    # Selected for updating
    for_update_status = session.execute(
        SELECT_FOR_UPDATING(
            import_date=import_date,
            status=settings.IMPORT_STATUS
        )
    )

    # Send the records selected to be updated to the business office
    select_records_for_update = session.execute(SELECT_RECORDS_FOR_UPDATE)

    if not settings.DEBUG:
        send_mail(
            request, TO_LIST,
            "[DJ Cheque] Checks selected for update", settings.ADMINS[0][1],
            "reconciliation/cheque/email.html",
            {"title":"Voided checks","objs":select_records_for_update},
            settings.MANAGERS
        )
    # Update cheque status to 's'uspictious
    session.execute(UPDATE_STATUS_SUSPICIOUS)

    # Send duplicate records to the business office
    select_duplicates_2 = session.execute(
        SELECT_DUPLICATES_2(import_date=import_date)
    )

    if not settings.DEBUG:
        send_mail(
            request, TO_LIST,
            "[DJ Cheque] Duplicate checks", settings.ADMINS[0][1],
            "reconciliation/cheque/email.html",
            {"title":"Duplicate checks","objs":select_duplicates_2},
            settings.MANAGERS
        )

    # Find the cleared CheckNos and update gltr_rec as 'r'econciled
    # and ccreconjb_rec as 'ar' (auto-reconciled)

    # Drop the temporary table, just in case
    try:
        session.execute("DROP TABLE tmp_reconupdta")
    except:
        pass

    # Find the cleared Check Numbers
    session.execute(
        SELECT_CLEARED_CHEQUES(
            import_date=import_date,
            suspicious=settings.SUSPICIOUS,
            auto_rec=settings.AUTO_REC,
            requi_rich=settings.REQUI_RICH,
            requi_vich=settings.REQUI_VICH
        )
    )
    # Set gltr_rec as 'r'econciled
    update_reconciled = session.execute(UPDATE_RECONCILED)
    # Set ccreconjb_rec as 'ar' (auto-reconciled)
    update_status = session.execute(UPDATE_STATUS_AUTO_REC)
    # Send the results to business office
    select_reconciled = session.execute(SELECT_RECONCILIATED)

    if not settings.DEBUG:
        send_mail(
            request, TO_LIST,
            "[DJ Cheque] Reconciled checks", settings.ADMINS[0][1],
            "reconciliation/cheque/email.html",
            {"title":"Reconciled checks","objs":select_reconciled},
            settings.MANAGERS
        )

    return {
        "select_voidb":select_voidb,
        "select_records_for_update":select_records_for_update,
        "select_duplicates_2": select_duplicates_2,
        "select_reconciled":select_reconciled
    }
