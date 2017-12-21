const express = require('express');
var cors = require('cors');
const app = express();
app.use(cors());

const allowedCostFunctions = ["meanScore", "invMeanScore", "distance"];

const getRoute = require("./lib/routes");

app.get('/', (req, res) => res.send('Hello World!'))

app.get("/routes", (req, res)=>{
  //comma separated
  var fromPoint = req.query.A.split(",");
  var toPoint = req.query.B.split(",");
  var cost = req.query.cost;

  if (!cost){
    cost = "distance";
  }

  if (allowedCostFunctions.indexOf(cost) == -1) throw new Error("unknown cost function");


  if (fromPoint.length != 2) throw new Error();
  if (toPoint.length != 2) throw new Error();


  return getRoute(fromPoint, toPoint, cost)
    .then((data)=>{
      console.log(data);
      res.json(data);
    })
    .catch((err)=>{
      throw err;
    })
})

app.listen(8080, () => console.log('Now serving...'))
