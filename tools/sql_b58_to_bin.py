#!/usr/bin/env python
# sql_b58_to_bin.py : copy base58 table to binary one

import binascii, hashlib, base58, secp256k1, threading, MySQLdb, yaml, time
from dotmap import DotMap

# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

decode_hex = binascii.unhexlify

# Select oldest
conn = MySQLdb.connect(host = conf.db.host,
	user = conf.db.user,
	password = conf.db.pwd,
	database = conf.db.db)
	
cursor=conn.cursor()
step = 100
found_line = True
i = 1
values = []
while (found_line):
	try:
		sql = "SELECT * FROM copyrichest LIMIT %d, %d" % (i * step, step - 1);
		cursor.execute(sql, [])
		data=cursor.fetchall()
		
		if not data:
			found_line = None
			continue
			
		for row in data:
			address = row[0]
			print address
			
			# 24 bytes only needed
			decoded = base58.b58decode(address)[1:]
			values.append(decoded)
			print decoded
		#~ exit(0)
		i += 1
		
		# reconnect
		#~ if(i % 100 == 0):
		print "cooldown reconnect"
		cursor.executemany("INSERT INTO binarych values(%s)", values)
		conn.commit()
		values = []
		#~ exit(1)
			#~ cursor.close()
			#~ conn.close()
			#~ sleep(1)
			#~ conn = MySQLdb.connect(host = conf.db.host,
			#~ user = conf.db.user,
			#~ password = conf.db.pwd,
			#~ database = conf.db.db)
			#~ cursor=conn.cursor()
	except MySQLdb.Error,e:
		values = []
		print "Exception"
		print e[0], e[1]
		i += 1
		#conn.rollback()
		#cursor.close()
		#conn.close()
		#~ exit(2)

cursor.close()
conn.close()
    
exit(0)	
