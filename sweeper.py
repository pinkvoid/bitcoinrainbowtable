#!/usr/bin/env python
# sweeper.py : outputs WIF and bitcoin address for a hex bitcoin key

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

hexpk='5362c1ee5dcd82f45c1a24bfb649a5f35186131d8938df9f4a5dcc128fc8d51f'
print('Len: ',len(hexpk))
print(decode_hex(hexpk))
pk=secp256k1.PrivateKey(decode_hex(hexpk))
pkhex = '80' + pk.serialize()
#print pkhex
hash = hashlib.sha256(decode_hex(pkhex)).hexdigest()
#print hash
hash2 = hashlib.sha256(decode_hex(hash)).hexdigest()
#print hash2
#print hash2[:8]
finalhash = pkhex + hash2[:8]
#print finalhash
wif = base58.b58encode(decode_hex(finalhash))
print(wif)
#exit(0)
#print binascii.hexlify(pk.private_key)

pubbin=pk.pubkey.serialize(False)
#print("Clef: "+pk.pubkey.serialize(False))
pubkey = binascii.hexlify(pubbin)
#print("Pubkey: "+pubkey)
print(binascii.hexlify(gen_address(pubkey, True)))
print (wif + ',' + gen_address(pubkey,False)+'|')
