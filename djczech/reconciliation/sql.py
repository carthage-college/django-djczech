from django.conf import settings

STATUS=settings.IMPORT_STATUS

# Populate temporary table A
TMP_VOID_A = """
    SELECT
        gltr_rec.gltr_no as gltr_noa, gle_rec.jrnl_ref, gle_rec.doc_id as
        cknodoc_ida, gle_rec.doc_no as cknodoc_noa, gltr_rec.subs, gltr_rec.stat,
        gltr_rec.recon_stat
    FROM
        vch_rec, gle_rec, gltr_rec
    WHERE
        gle_rec.jrnl_ref = 'CK'
    AND
        vch_rec.amt_type = 'ACT'
    AND
        gle_rec.ctgry = 'VOID'
    AND
        gle_rec.jrnl_ref = vch_rec.vch_ref
    AND
        gle_rec.jrnl_no = vch_rec.jrnl_no
    AND
        gle_rec.jrnl_ref = gltr_rec.jrnl_ref
    AND
        gle_rec.jrnl_no = gltr_rec.jrnl_no
    AND
        gle_rec.gle_no = gltr_rec.ent_no
    AND
        gltr_rec.stat IN('P','xV')
    AND
        gltr_rec.recon_stat = 'O'
    ORDER BY
        cknodoc_noa
    INTO TEMP
        tmp_voida
    WITH NO LOG
"""

# select * from temporary table A for testing
SELECT_VOID_A = """
    SELECT
        *
    FROM
        tmp_voida
    ORDER BY
        cknodoc_noa, gltr_noa
"""

# Populate temporary table B
TMP_VOID_B = """
    SELECT
        gle_rec.doc_id as cknodoc_idb, gltr_rec.gltr_no as gltr_nob,
        gle_rec.jrnl_ref, gle_rec.jrnl_no, gle_rec.descr as GLEdescr,
        gle_rec.doc_no as cknodoc_nob, gle_rec.ctgry, gltr_rec.amt,
        gltr_rec.recon_stat
    FROM
        vch_rec, gle_rec, gltr_rec, tmp_voida
    WHERE gle_rec.jrnl_ref = 'CK'
        AND vch_rec.amt_type = 'ACT'
        AND gle_rec.jrnl_ref = vch_rec.vch_ref
        AND gle_rec.jrnl_no = vch_rec.jrnl_no
        AND gle_rec.jrnl_ref = gltr_rec.jrnl_ref
        AND gle_rec.jrnl_no = gltr_rec.jrnl_no
        AND gle_rec.gle_no = gltr_rec.ent_no
        AND gltr_rec.stat IN('P','xV')
        AND gltr_rec.recon_stat = 'O'
        AND tmp_voida.cknodoc_noa = gle_rec.doc_no
        AND tmp_voida.cknodoc_ida = gle_rec.doc_id
        AND tmp_voida.subs = gltr_rec.subs
        AND tmp_voida.stat = gltr_rec.stat
        AND tmp_voida.recon_stat = gltr_rec.recon_stat
    ORDER BY
        cknodoc_nob
    INTO TEMP
        tmp_voidb
    WITH NO LOG
"""

# select * from temporary table B and send the data to the business office
SELECT_VOID_B = """
    SELECT
        *
    FROM
        tmp_voidb
    ORDER BY
        cknodoc_nob, gltr_nob
"""

# Set reconciliation status to 'v'
UPDATE_RECONCILIATION_STATUS = """
    UPDATE
        gltr_rec
    SET
        gltr_rec.recon_stat = '{}'
    WHERE
        gltr_rec.gltr_no
    IN  (
            SELECT
                tmp_voidb.gltr_nob
            FROM
                tmp_voidb
        )
    AND
        gltr_rec.recon_stat = 'O'
""".format(settings.REQUI_VICH)

# Find the duplicate cheque numbers and update those as 's'uspicious

# select import_date and stick it in a temp table, for some reason
SELECT_CURRENT_BATCH_DATE = """
    SELECT
        Min(ccreconjb_rec.jbimprt_date) AS crrntbatchdate
    FROM
        ccreconjb_rec
    WHERE
        jbimprt_date >= '{import_date}'
    INTO TEMP
        tmp_maxbtchdate
    WITH NO LOG
""".format

# select the duplicate cheques
SELECT_DUPLICATES_1 = """
    SELECT
        ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate,
        Max(ccreconjb_rec.jbimprt_date) AS maxbatchdate,
        Min(ccreconjb_rec.jbimprt_date) AS minbatchdate,
        Count(ccreconjb_rec.jbseqno) AS countofjbseqno
    FROM
        ccreconjb_rec, tmp_maxbtchdate
    WHERE
        ccreconjb_rec.jbimprt_date >= '{import_date}'
    GROUP BY
        ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate
    HAVING
        Count(ccreconjb_rec.jbseqno) > 1
    INTO TEMP
        tmp_dupcknos
    WITH NO LOG
""".format

# select cheques for updating
SELECT_FOR_UPDATING = """
    SELECT
        ccreconjb_rec.jbseqno, ccreconjb_rec.jbchkno,
        ccreconjb_rec.jbchknolnk, ccreconjb_rec.jbimprt_date,
        ccreconjb_rec.jbstatus, ccreconjb_rec.jbaction,
        ccreconjb_rec.jbaccount, ccreconjb_rec.jbamount,
        ccreconjb_rec.jbamountlnk, ccreconjb_rec.jbstatus_date,
        tmp_dupcknos.crrntbatchdate, tmp_dupcknos.maxbatchdate,
        tmp_dupcknos.minbatchdate, tmp_dupcknos.countofjbseqno
    FROM
        ccreconjb_rec, tmp_dupcknos
    WHERE
        ccreconjb_rec.jbimprt_date >= '{import_date}'
    AND
        ccreconjb_rec.jbchkno = tmp_dupcknos.jbchkno
    AND
        ccreconjb_rec.jbstatus = '{status}'
    ORDER BY
        ccreconjb_rec.jbchkno, ccreconjb_rec.jbseqno
    INTO TEMP
        tmp_4updtstatus
    WITH NO LOG
""".format

# select the records to be updated and send to the business office
SELECT_RECORDS_FOR_UPDATE = """
    SELECT
        *
    FROM
        tmp_4updtstatus
    ORDER BY
        jbchkno, jbseqno
"""

# update cheque status to 's'uspicious
UPDATE_STATUS_SUSPICIOUS = """
    UPDATE
        ccreconjb_rec
    SET
        ccreconjb_rec.jbstatus = '{}'
    WHERE
        ccreconjb_rec.jbseqno
    IN  (
            SELECT
                tmp_4updtstatus.jbseqno
            FROM
                tmp_4updtstatus
        )
    AND
        ccreconjb_rec.jbstatus = '{}'
""".format(settings.SUSPICIOUS, STATUS)

# send the results to the business office
SELECT_DUPLICATES_2 = """
    SELECT
        ccreconjb_rec.jbseqno, ccreconjb_rec.jbchkno, ccreconjb_rec.jbchknolnk,
        ccreconjb_rec.jbimprt_date, ccreconjb_rec.jbstatus,
        ccreconjb_rec.jbaction, ccreconjb_rec.jbaccount,
        ccreconjb_rec.jbamount, ccreconjb_rec.jbamountlnk,
        ccreconjb_rec.jbstatus_date, tmp_dupcknos.crrntbatchdate,
        tmp_dupcknos.maxbatchdate, tmp_dupcknos.minbatchdate,
        tmp_dupcknos.countofjbseqno
    FROM
        ccreconjb_rec, tmp_dupcknos
    WHERE
        ccreconjb_rec.jbimprt_date >= '{import_date}'
    AND
        ccreconjb_rec.jbchkno = tmp_dupcknos.jbchkno
    ORDER BY
        ccreconjb_rec.jbchkno, ccreconjb_rec.jbseqno
""".format

# Find the cleared CheckNos and update gltr_rec as 'r'econciled
# and ccreconjb_rec as 'ar' (auto-reconciled)

SELECT_CLEARED_CHEQUES = """
    SELECT
        ccreconjb_rec.jbimprt_date, ccreconjb_rec.jbseqno,
        ccreconjb_rec.jbchkno, ccreconjb_rec.jbchknolnk,
        ccreconjb_rec.jbstatus, ccreconjb_rec.jbaction,
        ccreconjb_rec.jbamount, ccreconjb_rec.jbamountlnk,
        ccreconjb_rec.jbaccount, ccreconjb_rec.jbstatus_date,
        ccreconjb_rec.jbpayee, gltr_rec.gltr_no, gle_rec.jrnl_ref,
        gle_rec.jrnl_no, gle_rec.doc_id as cknodoc_id, gltr_rec.amt,
        gle_rec.doc_no as cknodoc_no, gltr_rec.subs, gltr_rec.stat,
        gltr_rec.recon_stat
    FROM
        vch_rec, gle_rec, gltr_rec, ccreconjb_rec
    WHERE
        gle_rec.jrnl_ref = 'CK'
    AND
        vch_rec.amt_type = 'ACT'
    AND
        gle_rec.ctgry = 'CHK'
    AND
        gle_rec.jrnl_ref = vch_rec.vch_ref
    AND
        gle_rec.jrnl_no = vch_rec.jrnl_no
    AND
        gle_rec.jrnl_ref = gltr_rec.jrnl_ref
    AND
        gle_rec.jrnl_no = gltr_rec.jrnl_no
    AND
        gle_rec.gle_no = gltr_rec.ent_no
    AND
        gltr_rec.stat IN('P','xV')
    AND
        ccreconjb_rec.jbchknolnk = gle_rec.doc_no
    AND
        ccreconjb_rec.jbamountlnk = gltr_rec.amt
    AND
        ccreconjb_rec.jbstatus NOT IN("{suspicious}","s","{auto_rec}","ar","er","mr")
    AND
        gltr_rec.recon_stat NOT IN("{requi_rich}","{requi_vich}","r","v")
    AND
        ccreconjb_rec.jbimprt_date >= '{import_date}'
    ORDER BY
        gle_rec.doc_no
    INTO TEMP
        tmp_reconupdta
    WITH NO LOG
""".format

UPDATE_RECONCILED = """
    UPDATE
        gltr_rec
    SET
        gltr_rec.recon_stat = '{}'
    WHERE
        gltr_rec.gltr_no
    IN  (
            SELECT
                tmp_reconupdta.gltr_no
            FROM
                tmp_reconupdta
        )
    AND
        gltr_rec.recon_stat = 'O'
""".format(settings.REQUI_RICH)

UPDATE_STATUS_AUTO_REC = """
    UPDATE
        ccreconjb_rec
    SET
        ccreconjb_rec.jbstatus = '{}'
    WHERE
        ccreconjb_rec.jbseqno
    IN  (
            SELECT
                tmp_reconupdta.jbseqno
            FROM
                tmp_reconupdta
        )
    AND
        ccreconjb_rec.jbstatus = '{}'
""".format(settings.AUTO_REC, STATUS)

# Display reconciled checks
SELECT_RECONCILIATED = """
    SELECT
        *
    FROM
        tmp_reconupdta
    ORDER BY
        tmp_reconupdta.cknodoc_no
"""

# Display any left over imported checks whose status has not changed
SELECT_REMAINING_EYE = """
    SELECT * FROM ccreconjb_rec where jbstatus = '{}'
""".format(STATUS)

"""
Check Matching SQL incantations
"""

MATCHING_CARTHAGE_CHEQUES = """
    SELECT gle_rec.doc_no as check_number, gltr_rec.amt as amount,
        trim(id_rec.fullname) as fullname,
        TO_CHAR(vch_rec.pst_date,'%Y-%m-%d') as post_date
    FROM
        vch_rec, gle_rec, gltr_rec, id_rec
    WHERE
        vch_rec.vch_ref = gle_rec.jrnl_ref
    AND vch_rec.jrnl_no = gle_rec.jrnl_no
    AND vch_rec.vch_ref = "CK"
    AND gle_rec.doc_id = id_rec.id
    AND gle_rec.jrnl_ref = gltr_rec.jrnl_ref
    AND gle_rec.jrnl_no = gltr_rec.jrnl_no
    AND gle_rec.gle_no = gltr_rec.ent_no
    AND (gltr_rec.recon_stat != "r" AND gltr_rec.recon_stat != "v")
    AND gltr_rec.stat = "P"
    ORDER BY
        check_number DESC
"""

MATCHING_JOHNSON_CHEQUES = """
   SELECT
        jbchkno as check_number, jbamount as amount, jbaction,
        jbstatus, TO_CHAR(jbstatus_date,'%Y-%m-%d') as cleared_date,
        jbpayee, jbaccount, jbseqno
   FROM
        ccreconjb_rec
   WHERE
        (jbstatus = "I" OR jbstatus = "s")
   AND
        jbimprt_date > "{}"
   ORDER BY check_number DESC
""".format(settings.IMPORT_DATE_FIRST)

MATCHING_UPDATE_GLTR_REC = """
    UPDATE
        gltr_rec
    SET
        recon_stat = "r"
    WHERE gltr_no in (
        SELECT gltr_rec.gltr_no
        FROM vch_rec, gle_rec, gltr_rec
        WHERE vch_rec.vch_ref = gle_rec.jrnl_ref
          AND vch_rec.jrnl_no = gle_rec.jrnl_no
          AND vch_rec.vch_ref = "CK"
          AND gle_rec.jrnl_ref = gltr_rec.jrnl_ref
          AND gle_rec.jrnl_no = gltr_rec.jrnl_no
          AND gle_rec.gle_no = gltr_rec.ent_no
          AND gltr_rec.stat = "P"
          AND gle_rec.doc_no = {CarthageNumber}
    )
""".format

