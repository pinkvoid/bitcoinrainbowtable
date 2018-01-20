#!/usr/bin/env python
# hammer.py : splits incoming table's pairs to archive and public tables

import binascii, hashlib, base58, secp256k1, threading, MySQLdb, yaml
from dotmap import DotMap

# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

# Confirm @ https://www.bitaddress.org

decode_hex = binascii.unhexlify

def gen_address(public_key,raw=False):
  # perform SHA-256 hashing on the public key
  sha256 = hashlib.sha256()
  sha256.update( decode_hex(public_key) )
  hash = sha256.hexdigest()
  
  # public key hash (for p2pkh) - perform RIPEMD-160 hashing on the result of SHA-256
  # prepend mainnet version byte
  ripemd160 = hashlib.new('ripemd160')
  ripemd160.update( decode_hex(hash) )
  public_key_hash = ripemd160.hexdigest()
  mainnet_public_key_hash = '00' + public_key_hash
  
  # perform SHA-256 hash on the extended RIPEMD-160 result
  sha256 = hashlib.sha256()
  sha256.update( decode_hex(mainnet_public_key_hash) )
  hash = sha256.hexdigest()
  
  # perform SHA-256 on the previous SHA-256 hash
  sha256 = hashlib.sha256()
  sha256.update( decode_hex(hash) )
  hash = sha256.hexdigest()
  
  # create a checksum using the first 4 bytes of the previous SHA-256 hash
  # appedend the 4 checksum bytes to the extended RIPEMD-160 hash
  checksum = hash[:8]
  hash = mainnet_public_key_hash + checksum
  
  # convert RIPEMD-160 + checksum into base58 encoded string
  if(raw):
    return decode_hex(hash)
  else:
    return base58.b58encode( decode_hex(hash) )

# Start:

# Select oldest
conn = MySQLdb.connect(host = conf.db.host,
	user = conf.db.user,
	password = conf.db.pwd,
	database = conf.db.db,
	port = conf.db.port)
	
cursor=conn.cursor()

i = 0
while (True):
	try:
		sql = "SELECT * FROM incoming ORDER BY id ASC LIMIT 1";
		cursor.execute(sql, [])
		data=cursor.fetchall()
		if not data:
			time.sleep(10)
			continue
		address = base58.b58encode(data[0][1])
		
		# was stored and is saved without version bit
		public = [address]
		cursor.execute("INSERT INTO public(address) values(%s)", public)
		
		archive = [cursor.lastrowid, data[0][2]]
		cursor.execute("INSERT INTO archive(public_id, pkey) values(%s,%s)", archive)
		
		cursor.execute("DELETE FROM incoming WHERE id = %s", [data[0][0]])
		conn.commit()
		i += 1
		print(str(i))
	except MySQLdb.Error,e:
	    print e[0], e[1]
	    conn.rollback()
	    cursor.close()
	    conn.close()
	    exit(2)

cursor.close()
conn.close()
    
exit(0)	
