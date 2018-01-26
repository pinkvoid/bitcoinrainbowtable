#!/usr/bin/env python
import binascii, hashlib, threading,os,time, os, random
#~ from dotmap import DotMap
#~ from Crypto.Cipher import AES
#~ from Crypto.Util import Counter
#~ import secrets
from random import randint
import base58, secp256k1, MySQLdb as mariadb, yaml, numpy

#max key 0xFFFF FFFF FFFF FFFF FFFF FFFF FFFF FFFE BAAE DCE6 AF48 A03B BFD2 5E8C D036 4140
#max key 
from Crypto import Random
import BrtSecp
import fastrand
decode_hex = binascii.hexlify

def gen_address(public_key):
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
        
        # strip first 0x00 version byte
        # https://en.bitcoin.it/wiki/Base58Check_encoding#Encoding_a_Bitcoin_address
        hash = mainnet_public_key_hash[2:] + checksum

        # convert RIPEMD-160 + checksum into base58 encoded string

        return decode_hex(hash)



a = "0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140";
#~ rand = binascii.hexlify(os.urandom(32))
#~ print("Rand : "+rand)
#~ print BrtSecp.pubkeyy(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140)
#~ print "Hex: "
#~ print 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140

print BrtSecp.pubkeyy(randint(1, 115792089237316195423570985008687907852837564279074904382605163141518161494336))
#~ print BrtSecp.pubkeyy(binascii.unhexlify(rand))
#~ print(int(a, 16))
#~ print(randint(1, 115792089237316195423570985008687907852837564279074904382605163141518161494336))
#~ print(int(os.urandom(32), 2))
#~ exit(0)

def customgen():
	#~ i = randint(1, 115792089237316195423570985008687907852837564279074904382605163141518161494336)
	#~ BrtSecp.pubkeyy(i)
	pk=secp256k1.PrivateKey()
	pubbin=pk.pubkey.serialize(False)
	pubkey = binascii.hexlify(pubbin)
	address= gen_address(pubkey)

def timereps(reps, func):
    from time import time
    start = time()
    for i in range(0, reps):
        func()
    end = time()
    return (end - start) / reps

def random_with_check():
	maximum = binascii.unhexlify("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364140")
	key = os.urandom(32)


#~ listdir_time = timereps(1000000, lambda: binascii.hexlify(os.urandom(32)))
listdir_time = timereps(1000000, lambda: os.urandom(32))

print("python can do %d private keys per second using urandom" % (1 / listdir_time))

listdir_time = timereps(100000, lambda: randint(1, 115792089237316195423570985008687907852837564279074904382605163141518161494336))
print("python can do %d private keys per second with randint" % (1 / listdir_time))

listdir_time = timereps(100000, lambda: randint(1, 115792089237316195423570985008687907852837564279074904382605163141518161494336))
print("python can do %d private keys per second with randint" % (1 / listdir_time))

listdir_time = timereps(500, lambda: customgen())
print("python can do %d priv+pub+address per second with randint" % (1 / listdir_time))

#~ listdir_time = timereps(100000, lambda: secrets.token_bytes(16))

#~ print("python can do %d private keys per second with secrets" % (1 / listdir_time))

#~ listdir_time = timereps(100000, lambda: Random.get_random_bytes(5))

#~ print("python can do %d private keys per second with Crypto Random" % (1 / listdir_time))


listdir_time = timereps(300, lambda: secp256k1.PrivateKey())
print("python can do %d private keys per second with secp256k1" % (1 / listdir_time))

listdir_time = timereps(300, lambda: secp256k1.PrivateKey(os.urandom(32)))
print("python can do %d private keys per second with secp256k1 urandom" % (1 / listdir_time))

#~ listdir_time = timereps(1000000, lambda: numpy.random.bytes(32))

#~ print("python can do %d private keys per second using numpy" % (1 / listdir_time))
exit(0)


# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

# alias method
decode_hex = binascii.unhexlify

class myThread (threading.Thread):
    def __init__(self, conf):
        self.conf= conf
        threading.Thread.__init__(self)
    def run(self):
        print('Process started pid:'+str(threading.current_thread()))
        max_range = self.conf.worker.batch_and_insert_size
        i = 0
        conn = mariadb.connect(host = self.conf.db.host,
							 user = self.conf.db.user,
							 password = self.conf.db.pwd,
							 database = self.conf.db.db,
							 port = self.conf.db.port)
        cursor = conn.cursor()
        while (self.conf.worker.lifetime == 0 or i < self.conf.worker.lifetime):
            list=[]
            for x in range(0, max_range):
                values=[]
                pk=secp256k1.PrivateKey()

                pubbin=pk.pubkey.serialize(False)
                pubkey = binascii.hexlify(pubbin)

                address=self.gen_address(pubkey)
                values.append(pk.private_key)
                values.append(address)
                list.append(values);

            # try:
            cursor.executemany("INSERT INTO incoming(private,address) values(%s,%s)",list)
            conn.commit()
            print('Process pid:'+str(threading.current_thread())+' round: '+str(i)+' processed : +'+str(max_range))
            i += 1
            # except:
            #    conn.rollback()
        cursor.close()
        conn.close()



    def gen_address(self,public_key):
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
        
        # strip first 0x00 version byte
        # https://en.bitcoin.it/wiki/Base58Check_encoding#Encoding_a_Bitcoin_address
        hash = mainnet_public_key_hash[2:] + checksum

        # convert RIPEMD-160 + checksum into base58 encoded string

        return decode_hex(hash)

try:
    threads = []
    for x in range(0, conf.worker.threads):
        thread = myThread(conf)
        time.sleep(conf.worker.thread_start_delay)
        thread.start()
        threads.append(thread)

except:
    print("Error: unable to start thread")
for thread in threads:
    thread.join()

