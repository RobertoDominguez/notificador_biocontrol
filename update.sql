ALTER TABLE acc.AccessLog add mostrado bit default 0;
ALTER TABLE acc.AccessLog add abierto bit default 0;


update acc.AccessLog set mostrado = 1;
update acc.AccessLog set abierto = 1;