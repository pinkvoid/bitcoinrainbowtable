#!/usr/bin/env python
# hammer.py : splits incoming table's pairs to archive and public tables

import MySQLdb, yaml
from dotmap import DotMap

# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

# Select oldest
conn = MySQLdb.connect(host = conf.db.host,
	user = conf.db.user,
	database = conf.db.db)
	
cursor=conn.cursor()

tableIncoming = "incoming_2018023"
tableArchive = "tarchive"
tablePublic = "tpublic"

try:
	#"insert into tarchive(pkey) select private from incoming order by id"
	#"insert into tpublic(address) select address from incoming order by id"
	#"select count(*) from tpublic"
	#"select count(*) from tarchive"
	#"insert into tpublic(address) select address from incoming order by id"
	queryPrivkey = "insert into %s(pkey) select private from %s order by id" % (tableArchive, tableIncoming)
	queryAddress = "insert into %s(address) select address from %s order by id" % (tablePublic, tableIncoming)

	print("Archiving private keys")
	cursor.execute(queryPrivkey, [])

	print("Publishing addresses")
	cursor.execute(queryAddress, [])

	queryCountPublic = "select count(*) from %s" % tablePublic
	queryCountArchive = "select count(*) from %s" % tableArchive

	cursor.execute(queryCountPublic, [])
	pubCount = cursor.fetchone()[0]
	cursor.execute(queryCountArchive, [])
	privCount = cursor.fetchone()[0]

	print "pub. count: %d" % pubCount
	print "pri. count: %d" % privCount

	if(privCount != pubCount):
		print "Different count error"
		exit(2)

	# Check first of incoming
	cursor.execute("select * from %s ORDER BY id ASC LIMIT 1" % tableIncoming)
	#print cursor.fetchone()
	first = cursor.fetchone()

	cursor.execute("select * from "+tablePublic+" WHERE address = %s", [first[1]] )
	firstPublic = cursor.fetchone()

	cursor.execute("select * from "+tableArchive+" WHERE public_id = %s", [firstPublic[0]] )
	firstArchive = cursor.fetchone()

	if(firstArchive[1] != first[2]):
		print "First entry does not match between incoming and public-archive"
		exit(2)

	# Check last of incoming
	cursor.execute("select * from %s ORDER BY id DESC LIMIT 1" % tableIncoming)
	first = cursor.fetchone()

	cursor.execute("select * from "+tablePublic+" WHERE address = %s", [first[1]] )
	firstPublic = cursor.fetchone()

	cursor.execute("select * from "+tableArchive+" WHERE public_id = %s", [firstPublic[0]] )
	firstArchive = cursor.fetchone()

	if(firstArchive[1] != first[2]):
		print "LAST entry does not match between incoming and public-archive"
		exit(2)

	print "Checks OK, truncating incoming..."
	cursor.execute("TRUNCATE table %s" % tableIncoming)

	conn.commit()
except MySQLdb.Error,e:
    print("Exception")
    print e[0], e[1]
    conn.rollback()
    cursor.close()
    conn.close()
	
exit(0)
