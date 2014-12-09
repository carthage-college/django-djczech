SELECT
    gltr_no,
    jrnl_ref,
    jrnl_no,
    ent_no,
    amt,
    fund,
    func,
    obj,
    proj,
    subs,
    stat,
    recon_stat
FROM
    gltr_rec
WHERE
    amt > 0;
