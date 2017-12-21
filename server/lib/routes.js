var getClosestNode = require('./utils').getClosestNode;
var getRouteFromDB = require("./utils").route;


function getRoute(fromPoint, toPoint, cost){
  return new Promise((resolve, reject)=>{
    let fromLongitude = +fromPoint[0];
    let fromLatitude = +fromPoint[1];
    let fromNodePromise = getClosestNode(fromLongitude, fromLatitude);
    let toLongitude = +toPoint[0];
    let toLatitude = +toPoint[1];
    let toNodePromise = getClosestNode(toLongitude, toLatitude);
    return Promise.all([fromNodePromise, toNodePromise])
      .then((nodes)=>{
        console.log(nodes)
        var _fromID = +nodes[0].id;
        var _toID = +nodes[1].id;
        return getRouteFromDB(_fromID, _toID, cost)
      })
      .then((route)=>{
        resolve(route);
      })
      .catch((err)=>{
        reject(err);
      })
  })
}

module.exports = getRoute;
