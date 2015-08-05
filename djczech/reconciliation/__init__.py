# Populate temp table A
TMP_VOID_A = """
SELECT
    gltr_rec.gltr_no gltr_noa, gle_rec.jrnl_ref, gle_rec.doc_id cknodoc_ida,
    gle_rec.doc_no cknodoc_noa, gltr_rec.subs, gltr_rec.stat,
    gltr_rec.recon_stat
FROM vch_rec, gle_rec, gltr_rec
WHERE gle_rec.jrnl_ref = 'CK'
  AND vch_rec.amt_type = 'ACT'
  AND gle_rec.ctgry = 'VOID'
  AND gle_rec.jrnl_ref = vch_rec.vch_ref
  AND gle_rec.jrnl_no = vch_rec.jrnl_no
  AND gle_rec.jrnl_ref = gltr_rec.jrnl_ref
  AND gle_rec.jrnl_no = gltr_rec.jrnl_no
  AND gle_rec.gle_no = gltr_rec.ent_no
  AND gltr_rec.stat IN('P','xV')
  AND gltr_rec.recon_stat = 'O'
ORDER BY
    cknodoc_noa
INTO TEMP
    tmp_voida
WITH NO LOG
"""

# Populate temp table B
TMP_VOID_B = """
SELECT
    gle_rec.doc_id cknodoc_idb, gltr_rec.gltr_no gltr_nob, gle_rec.jrnl_ref,
    gle_rec.jrnl_no, gle_rec.descr GLEdescr, gle_rec.doc_no cknodoc_nob,
    gle_rec.ctgry, gltr_rec.amt, gltr_rec.recon_stat
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

# select * from temp table A for testing
SELECT_VOID_A = """
SELECT
    *
FROM
    tmp_voida
ORDER BY
    cknodoc_noa, gltr_noa
"""

# select * from temp table B and send the data to the business office
SELECT_VOID_B = """
SELECT
    *
FROM
    tmp_voidb
ORDER BY
    cknodoc_nob, gltr_nob
"""

# Set reconciliation status to 'r'
SET_RECONCILIATION_STATUS = """
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'r'
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_voidb.gltr_nob
        FROM
            tmp_voidb
        WHERE
            tmp_voidb.gltr_nob = 1869496
    )
AND
    gltr_rec.gltr_no = 1869496
AND
    gltr_rec.recon_stat = 'O'
"""

# Set reconciliation status to 'r'
SET_STATUS = """
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'r'
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
"""
# Set reconciliation status to 'r' with test clause
SET_STATUS_TEST = """
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'r'
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_voidb.gltr_nob
        FROM
            tmp_voidb
        WHERE
            tmp_voidb.gltr_nob = 1869496
    )
AND
    gltr_rec.gltr_no = 1869496
AND
    gltr_rec.recon_stat = 'O'
"""

UPDATE_STATUS = """
UPDATE
    ccreconjb_rec
SET
    ccreconjb_rec.jbstatus = 's'
WHERE
    ccreconjb_rec.jbseqno
IN  (
        SELECT
            tmp_4updtstatus.jbseqno
        FROM
            tmp_4updtstatus
    )
AND
    ccreconjb_rec.jbstatus = 'I'
"""
SELECT_RECORDS_FOR_UPDATE = """
SELECT
    *
FROM
    tmp_4updtstatus
ORDER BY
    jbchkno, jbseqno
"""

