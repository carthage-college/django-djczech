SELECT
    jbchkno,
    jbchknolnk,
    jbimprt_date,
    jbstatus,
    jbstatus_date,
    jbaction,
    jbaccount,
    jbamount,
    jbamountlnk,
    jbissue_date,
    jbpostd_dat,
    jbpayee,
    jbseqno
FROM
    train:ccreconjb_rec
WHERE
    jbaction != ""
ORDER BY
    jbimprt_date DESC
LIMIT 10;
