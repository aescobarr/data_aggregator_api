copy
(
select especie as species,null as url,null as picture_url, data as observation_string, data as observation_time,'exocat' as origin,
st_x(geom_4326) as _x, st_y(geom_4326) as _y from citacions where geom_4326 is not NULL order by random() limit 200)
to '/tmp/citacions_exocat' CSV DELIMITER ',' HEADER;
