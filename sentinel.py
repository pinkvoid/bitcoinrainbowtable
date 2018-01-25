#!/usr/bin/env python
# sentinel.py : checks a table agains another

import binascii, hashlib, base58, secp256k1, threading, MySQLdb, yaml
from dotmap import DotMap

# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

decode_hex = binascii.unhexlify

conn = MySQLdb.connect(host = conf.db.host,
	user = conf.db.user,
	password = conf.db.pwd,
	database = conf.db.db,
	port = conf.db.port)
	
cursor=conn.cursor()
step = 50
found_line = True
i = 1
values = []

while (found_line):
	try:
		sql = "SELECT * FROM binarych LIMIT %d, %d" % (i * step, step);
		cursor.execute(sql, [])
		data=cursor.fetchall()
		
		if not data:
			found_line = None
			continue
			
		addresses = []
			
		for row in data:
			#~ print row[0]
			addresses.append([row[0]])
			
		
		#~ addresses.append([[decode_hex('000000982fe094c3a9ce67e8ed1ab5de114c0cf15da7e8fe')]])
		#~ addresses = [[decode_hex('000000982fe094c3a9ce67e8ed1ab5de114c0cf15da7e8fe')]]s
			
		print addresses
		
		i += 1
		
		# reconnect
		cursor.executemany("SELECT * FROM tpublic WHERE address IN (%s)", addresses)
		
		data = cursor.fetchall()
		print data
		
		if(data):
			print "Found"
			print data
			exit(0)
			
		#~ exit(0)
	except MySQLdb.Error,e:
		values = []
		print "Exception"
		print e[0]
		i += 1
		exit(0)
		#conn.rollback()
		#cursor.close()
		#conn.close()
		#~ exit(2)

cursor.close()
conn.close()
    
exit(0)	
