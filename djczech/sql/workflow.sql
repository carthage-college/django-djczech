/* drop temp tables, just in case */
DROP TABLE tmp_voida;
DROP TABLE tmp_voidb;

/* Populate tmp_voida temp table */
/* TMP_VOID_A */
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
WITH NO LOG;

/* TEST: select * from tmp_voida table */
/* SELECT_VOID_A */
SELECT
    *
FROM
    tmp_voida
ORDER BY
    cknodoc_noa, gltr_noa;

/* Populate tmp_voidb temp table */
/* TMP_VOID_B */
SELECT
    gle_rec.doc_id as cknodoc_idb, gltr_rec.gltr_no as gltr_nob, gle_rec.jrnl_ref,
    gle_rec.jrnl_no, gle_rec.descr as GLEdescr, gle_rec.doc_no as cknodoc_nob,
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
WITH NO LOG;

/* select * from tmp_voidb. send_mail() in the view */
/* SELECT_VOID_B */
SELECT
    *
FROM
    tmp_voidb
ORDER BY
    cknodoc_nob, gltr_nob;

/* set reconciliation status to 'v' */
/* UPDATE_RECONCILIATION_STATUS */
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'V'
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_voidb.gltr_nob
        FROM
            tmp_voidb
    )
AND
    gltr_rec.recon_stat = 'O';

/* TEST */
SELECT * FROM gltr_rec WHERE recon_stat = 'V';

/*
TEST the above UPDATE with SELECT statement:

SELECT * FROM
    gltr_rec
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_voidb.gltr_nob
        FROM
            tmp_voidb
    )
AND
    gltr_rec.recon_stat = 'O';
*/

/* Find the duplicate check numbers and update as 's'uspicious */

/* first, drop the temp tables, just in case */
DROP TABLE tmp_maxbtchdate;
DROP TABLE tmp_DupCkNos;
DROP TABLE tmp_4updtstatus;

/* select import_date and stick it in a temp table, for some reason */
/* SELECT_CURRENT_BATCH_DATE */
SELECT
    Min(ccreconjb_rec.jbimprt_date) AS crrntbatchdate
FROM
    ccreconjb_rec
WHERE
    jbimprt_date >= DATE('2015-12-21')
INTO TEMP
    tmp_maxbtchdate
WITH NO LOG;

/* TEST */
SELECT * FROM tmp_maxbtchdate;

/* Select the duplicates cheques */
/* SELECT_DUPLICATES_1 */
SELECT
    ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate,
    Max(ccreconjb_rec.jbimprt_date) AS maxbatchdate,
    Min(ccreconjb_rec.jbimprt_date) AS minbatchdate,
    Count(ccreconjb_rec.jbseqno) AS countofjbseqno
FROM
    ccreconjb_rec, tmp_maxbtchdate
WHERE
    ccreconjb_rec.jbimprt_date >= DATE('2015-12-21')
GROUP BY
    ccreconjb_rec.jbchkno, tmp_maxbtchdate.crrntbatchdate
HAVING
    Count(ccreconjb_rec.jbseqno) > 1
INTO TEMP
    tmp_dupcknos
WITH NO LOG;

/* TEST: selected duplicate cheques */
SELECT * FROM tmp_dupcknos;


/* Select cheques for updating */
/* SELECT_FOR_UPDATING */
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
    ccreconjb_rec.jbimprt_date >= DATE('2015-12-21')
AND
    ccreconjb_rec.jbchkno = tmp_dupcknos.jbchkno
AND
    ccreconjb_rec.jbstatus = 'EYE'
ORDER BY
    ccreconjb_rec.jbchkno, ccreconjb_rec.jbseqno
INTO TEMP
    tmp_4updtstatus
WITH NO LOG;

/* select the records for update. send_mail() in the view */
/* SELECT_RECORDS_FOR_UPDATE */
SELECT
    *
FROM
    tmp_4updtstatus
ORDER BY
    jbchkno, jbseqno;

/* Update cheque status to 's'uspictious */
/* UPDATE_STATUS_SUSPICIOUS */
UPDATE
    ccreconjb_rec
SET
    ccreconjb_rec.jbstatus = 'S'
WHERE
    ccreconjb_rec.jbseqno
IN  (
        SELECT
            tmp_4updtstatus.jbseqno
        FROM
            tmp_4updtstatus
    )
AND
    ccreconjb_rec.jbstatus = 'EYE';

/* TEST */
SELECT * FROM ccreconjb_rec WHERE jbstatus = 'S';
 
/*
TEST the above UPDATE with SELECT statement

SELECT * FROM
    ccreconjb_rec
WHERE
    ccreconjb_rec.jbseqno
IN  (
        SELECT
            tmp_4updtstatus.jbseqno
        FROM
            tmp_4updtstatus
    )
AND
    ccreconjb_rec.jbstatus = 'EYE';
*/

/* Select the duplicates. send_mail() in the view */
/* SELECT_DUPLICATES_2 */
SELECT
    ccreconjb_rec.jbseqno, ccreconjb_rec.jbchkno, ccreconjb_rec.jbchknolnk,
    ccreconjb_rec.jbimprt_date,ccreconjb_rec.jbstatus,
    ccreconjb_rec.jbaction, ccreconjb_rec.jbaccount,
    ccreconjb_rec.jbamount, ccreconjb_rec.jbamountlnk,
    ccreconjb_rec.jbstatus_date, tmp_dupcknos.crrntbatchdate,
    tmp_dupcknos.maxbatchdate, tmp_dupcknos.minbatchdate,
    tmp_dupcknos.countofjbseqno
FROM
    ccreconjb_rec, tmp_dupcknos
WHERE
    ccreconjb_rec.jbimprt_date >= DATE('2015-12-21')
AND
    ccreconjb_rec.jbchkno = tmp_dupcknos.jbchkno
ORDER BY
    ccreconjb_rec.jbchkno, ccreconjb_rec.jbseqno;

/* Find the cleared CheckNos and update gltr_rec as 'r'econciled */
/* and ccreconjb_rec as 'ar' (auto-reconciled) */

/* Drop the temporary table, just in case */
DROP TABLE tmp_reconupdta;

/* Find the cleared Check Numbers */
/* SELECT_CLEARED_CHEQUES */
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
    ccreconjb_rec.jbstatus NOT IN("S","AR","er","mr")
AND
    gltr_rec.recon_stat NOT IN("R","V")
AND
    ccreconjb_rec.jbimprt_date >= DATE('2015-12-21')
ORDER BY
    gle_rec.doc_no
INTO TEMP
    tmp_reconupdta
WITH NO LOG;

/* TEST */
SELECT * FROM tmp_reconupdta;

/* Set gltr_rec as 'r'econciled */
/* UPDATE_RECONCILED */
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'R'
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_reconupdta.gltr_no
        FROM
            tmp_reconupdta
    )
AND
    gltr_rec.recon_stat = 'O';

/* TEST */
SELECT * FROM gltr_rec WHERE recon_stat = 'R'

/*
TEST the above UPDATE with SELECT statement

SELECT * FROM
    gltr_rec
WHERE
    gltr_rec.gltr_no
IN  (
        SELECT
            tmp_reconupdta.gltr_no
        FROM
            tmp_reconupdta
    )
AND
    gltr_rec.recon_stat = 'O';
*/

/* Set ccreconjb_rec as 'ar' (auto-reconciled) */
/* UPDATE_STATUS_AUTO_REC */
UPDATE
    ccreconjb_rec
SET
    ccreconjb_rec.jbstatus = 'AR'
WHERE
    ccreconjb_rec.jbseqno
IN  (
        SELECT
            tmp_reconupdta.jbseqno
        FROM
            tmp_reconupdta    
    )
AND
    ccreconjb_rec.jbstatus = 'EYE';

/* TEST */
SELECT * FROM ccreconjb_rec where jbstatus = 'EYE';

/*
TEST the above UPDATE with SELECT statement

SELECT * FROM
    ccreconjb_rec
WHERE
    ccreconjb_rec.jbseqno
IN  (
        SELECT
            tmp_reconupdta.jbseqno
        FROM
            tmp_reconupdta    
    )
AND
    ccreconjb_rec.jbstatus = 'I';
*/

/* select the reconciled checks. send_mail() in view */
/* SELECT_RECONCILIATED*/
SELECT
    *
FROM
    tmp_reconupdta
ORDER BY
    tmp_reconupdta.cknodoc_no;

/* TEST */
SELECT * FROM gltr_rec WHERE recon_stat = 'O';
SELECT * FROM gltr_rec WHERE recon_stat = 'R';
SELECT * FROM gltr_rec WHERE recon_stat = 'V';
SELECT * FROM gltr_rec WHERE recon_stat = 'v';

SELECT * FROM ccreconjb_rec WHERE jbstatus = 'S';
SELECT * FROM ccreconjb_rec where jbstatus = 'I';
SELECT * FROM ccreconjb_rec where jbstatus = 'EYE';
SELECT * FROM ccreconjb_rec where jbstatus = 'AR';

/* reset */
UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'O'
WHERE
    gltr_rec.recon_stat = 'V';

UPDATE
    ccreconjb_rec
SET
    ccreconjb_rec.jbstatus = 'EYE'
WHERE
    ccreconjb_rec.jbstatus = 'S';

UPDATE
    gltr_rec
SET
    gltr_rec.recon_stat = 'O'
WHERE
    gltr_rec.recon_stat = 'R';

UPDATE
    ccreconjb_rec
SET
    ccreconjb_rec.jbstatus = 'EYE'
WHERE
    ccreconjb_rec.jbstatus = 'AR';


/* start over */
DELETE ccreconjb_rec WHERE jbstatus = 'EYE';
DELETE ccreconjb_rec WHERE jbstatus = 'AR';

/* Fin */
