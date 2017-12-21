create table IF NOT EXISTS edges (
  id serial,
  featureid bigint,
  fullName text,
  MTFCC text,
  RTTYP char,
  meanScore double precision,
  scoreVariance double precision
);

SELECT AddGeometryColumn ('edges','geom',4326,'LINESTRING',2);


ALTER TABLE edges_noded
  ADD COLUMN fullName VARCHAR,
  ADD COLUMN MTFCC VARCHAR,
  ADD COLUMN meanScore double precision,
  ADD COLUMN scoreVariance double precision;


UPDATE edges_noded AS new
  SET
    fullName = old.fullName,
    MTFCC = old.MTFCC,
    meanScore = old.meanScore,
    scoreVariance = old.scoreVariance
  FROM edges AS old
  WHERE new.old_id = old.id;

SELECT
  cost
FROM pgr_aStar ('SELECT id, source::INT4, target::INT4, cost FROM edges_noded', 1000, 757)
ORDER BY seq;


SELECT * FROM pgr_astar('SELECT id, source, target, cost FROM edges_noded', 2, 12);



SELECT
  e.old_id,
  e.fullName,
  e.meanScore AS meanScore
FROM
  pgr_dijkstra('SELECT id, source::INT4, target::INT4, meanScore AS cost FROM edges_noded', 753, 756) AS r,
  edges_noded AS e
WHERE r.id = e.id;




  SELECT
    v.id,
    ST_AsGeoJSON(v.the_geom),
    string_agg(distinct(e.fullName),',') AS name,
    count(distinct(e.id))
  FROM
    edges_noded_vertices_pgr AS v,
    edges_noded AS e
  WHERE
    v.id = (SELECT
              id
            FROM edges_noded_vertices_pgr
            ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(37.5, -121), 4326) LIMIT 1)
    AND (e.source = v.id OR e.target = v.id)
  GROUP BY v.id, v.the_geom;




  SELECT * FROM pgr_dijkstra(
    'SELECT id,
         source,
         target,
         meanScore as cost
        FROM edges_noded',
    1, 5,
    directed := false);




SELECT id, st_asgeojson(the_geom) FROM edges_noded_vertices_pgr
    ORDER BY the_geom <-> ST_GeometryFromText('POINT(-122.7 30.5)',4326)
    LIMIT 1;


  SELECT
    min(r.seq) AS seq,
    e.old_id AS id,
    e.fullName,
    sum(e.cost) AS cost,
    sum(e.distance) AS distance,
    ST_AsGeoJSON(ST_Collect(e.geom)) AS geom
  FROM
  pgr_dijkstra(
    'SELECT id,
         source,
         target,
         meanScore as cost
        FROM edges_noded',
    1, 5,
    directed := false) AS r,
    edges_noded AS e
  WHERE
    r.edge = e.id
  GROUP BY
    e.old_id, e.fullName;



    SELECT
  min(r.seq) AS seq,
  e.old_id AS id,
  e.name,
  e.type,
  e.oneway,
  sum(e.time) AS time,
  sum(e.distance) AS distance,
  ST_Collect(e.the_geom) AS geom
FROM
  pgr_dijkstra(
   'SELECT
    id,
    source::INT4,
    target::INT4,
    %cost% AS cost,
    CASE oneway
      WHEN ''yes'' THEN -1
      ELSE %cost%
    END AS reverse_cost
  FROM edges_noded', %source%, %target%, true, true) AS r,
  edges_noded AS e
WHERE
  r.id2 = e.id
GROUP BY
  e.old_id, e.name, e.type, e.oneway





SELECT ST_AsGeoJSON(ST_UNION(b.geom)) AS geojson
    FROM pgr_dijkstra(
      'SELECT id,
           source,
           target,
           meanScore as cost
          FROM edges_noded',
      1, 5,
      directed := false) a,
         edges b
    WHERE a.old_id = b.id;
