# Confirm @ https://www.bitaddress.org
import binascii, hashlib, base58, secp256k1, threading, MySQLdb
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

lookingfor='1Lgk7vMxqJrxh7FP5gKfFSY3T3oPZTt6Wr'
print("Looking for : "+ lookingfor)

decoded = base58.b58decode(lookingfor)
print("Hex address: " + binascii.hexlify(decoded))

conn = MySQLdb.connect(host= ":3", port=0, user=",",passwd=".",db="rbt")
cursor=conn.cursor()
sql = "SELECT * FROM incoming WHERE address = %s";
args = [decoded]
cursor.execute(sql,args)
data=cursor.fetchall()

print(data)
