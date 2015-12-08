from django.conf import settings

from djczech.reconciliation.sql import *
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

    # Display temp table B data
    select_voidb = session.execute(SELECT_VOID_B).fetchall()

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

    # Display the records selected to be updated
    select_records_for_update = session.execute(
        SELECT_RECORDS_FOR_UPDATE
    ).fetchall()

    # Update cheque status to 's'uspictious
    session.execute(UPDATE_STATUS_SUSPICIOUS)

    # Display duplicate records
    select_duplicates_2 = session.execute(
        SELECT_DUPLICATES_2(import_date=import_date)
    ).fetchall()

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
    # Display the checks that have been reconciled
    select_reconciled = session.execute(SELECT_RECONCILIATED).fetchall()
    # Display any left over imported checks whose status has not changed
    select_remaining_eye = session.execute(SELECT_REMAINING_EYE).fetchall()

    return {
        "select_voidb":select_voidb,
        "select_records_for_update":select_records_for_update,
        "select_duplicates_2": select_duplicates_2,
        "select_reconciled":select_reconciled,
        "select_remaining_eye":select_remaining_eye
    }
