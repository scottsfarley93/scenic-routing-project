import psycopg2
import json
import os
import geojson
from shapely.geometry import shape

_dir =  os.path.dirname(__file__)


  # id serial,
  # featureid bigint,
  # fullName text,
  # MTFCC text,
  # RTTYP char,
  # meanScore double precision,
  # scoreVariance double precision

#       Column     |           Type            | Collation | Nullable |              Default              | Storage  | Stats target | Description
# ---------------+---------------------------+-----------+----------+-----------------------------------+----------+--------------+-------------
#  id            | integer                   |           | not null | nextval('edges_id_seq'::regclass) | plain    |              |
#  featureid     | bigint                    |           |          |                                   | plain    |              |
#  fullname      | text                      |           |          |                                   | extended |              |
#  mtfcc         | text                      |           |          |                                   | extended |              |
#  rttyp         | character(1)              |           |          |                                   | extended |              |
#  meanscore     | double precision          |           |          |                                   | plain    |              |
#  scorevariance | double precision          |           |          |                                   | plain    |              |
#  geom          | geometry(LineString,4326) |           |          |                                   | main     |              |
# scorecount    | integer                   |           |          |                                   | plain    |              |


conn = psycopg2.connect("dbname=scenerouting user=scottfarley")
cursor = conn.cursor()

sql = "TRUNCATE TABLE edges";
cursor.execute(sql);
conn.commit()

targetFile = os.path.join(_dir, "./../data/scenic_graph.json")
idx = 0
for line in open(targetFile, 'r'):
    feature = json.loads(line)
    _id = "DEFAULT"
    featureID = feature['properties']['LINEARID']
    fullName = feature['properties']['FULLNAME'].replace("'", "")
    MTFCC = feature['properties']['MTFCC']
    RTTYP = feature['properties']['RTTYP']
    meanScore = feature['properties']['meanScore']
    scoreVariance = feature['properties']['scoreVariance']
    scoreCount = feature['properties']['scoreCount']
    geoFeature = shape(geojson.loads(line)['geometry'])
    geom = geoFeature.wkt
    sql = "INSERT INTO edges values (%(_id)s, %(featureID)s, '%(fullName)s', '%(mtfcc)s', '%(rttype)s', %(meanScore)s, %(scoreVariance)s, ST_SetSRID(ST_GeomFromText('%(geom)s'), 4326), %(scoreCount)s);" % {
        '_id': _id,
        'featureID': featureID,
        'fullName': fullName,
        'mtfcc': MTFCC,
        'rttype': RTTYP,
        'meanScore': meanScore,
        'scoreVariance': scoreVariance,
        'geom': geom,
        'scoreCount': scoreCount
    }
    cursor.execute(sql)
    idx += 1
    print "Processed " + str(idx) + " features into database."
conn.commit()
cursor.close()
conn.close()
