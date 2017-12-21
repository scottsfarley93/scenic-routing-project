var pgp = require('pg-promise')
/**
  Return the nodeid closest to the given x y coordinates
*/
function getClosestNode(longitude, latitude, next){
  var db = require('./db-connection');
  return new Promise((resolve, reject)=>{
  var sql = `SELECT id, st_asgeojson(the_geom) FROM edges_noded_vertices_pgr
    ORDER BY the_geom <-> ST_GeometryFromText('POINT($1 $2)',4326)
    LIMIT 1;`

    return db.oneOrNone(sql, [longitude, latitude])
      .then((data)=>{
        return resolve(data)
      })
      .catch((err)=>{
        reject(err)
      })

  })
}


function route(fromNodeID, toNodeID, costColumn){
  var db = require('./db-connection');
  return new Promise((resolve, reject)=>{
  var sql = `  SELECT
    min(r.seq) AS seq,
    e.old_id AS id,
    e.fullName,
    sum(e.meanScore) AS cost,
    sum(e.distance) AS distance,
    ST_AsGeoJSON(ST_Collect(e.geom)) AS geom
  FROM
  pgr_dijkstra(
    'SELECT id,
         source,
         target,
         ${costColumn} as cost
        FROM edges_noded',
    $1, $2,
    directed := false) AS r,
    edges_noded AS e
  WHERE
    r.edge = e.id
  GROUP BY
    e.old_id, e.fullName;
    `
    return db.any(sql, [fromNodeID, toNodeID])
      .then((route)=>{
        console.log("FINDING ROUTE FROM " + fromNodeID + " TO " + toNodeID + " USING " + costColumn)
        return resolve(route)
      })
      .catch((err)=>{
        reject(err)
      })

  })
}

module.exports = {getClosestNode, route}
