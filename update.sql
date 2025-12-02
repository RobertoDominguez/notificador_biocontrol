-- BioApp
ALTER TABLE acc.AccessLog add mostrado bit default 0;
ALTER TABLE acc.AccessLog add abierto bit default 0;


update acc.AccessLog set mostrado = 1;
update acc.AccessLog set abierto = 1;



-- Access
ALTER TABLE acc_monitor_log add mostrado bit default 0;
ALTER TABLE acc_monitor_log add abierto bit default 0;


update acc_monitor_log set mostrado = 1;
update acc_monitor_log set abierto = 1;



-- MINI SQL
ALTER TABLE TEvent add mostrado bit default 0;
ALTER TABLE TEvent add abierto bit default 0;


update TEvent set mostrado = 1;
update TEvent set abierto = 1;

-- para ordenar en la consulta (de menor a mayor)
ALTER TABLE TControl add orden int default 0;
