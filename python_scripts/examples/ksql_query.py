from ksql import KSQLAPI

client = KSQLAPI('http://merf.egs.anl.gov:8088')
query = client.query('SELECT * FROM t1 EMIT CHANGES;')
#query = client.query('SELECT * FROM riderLocations EMIT CHANGES;')
for item in query:
    print(item)
