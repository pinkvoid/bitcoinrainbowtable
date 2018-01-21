#!/usr/bin/env python
import binascii, hashlib, base58, secp256k1, threading,MySQLdb as mariadb,os,time, yaml, time
from dotmap import DotMap
import signal 
import sys

# load config
conf = DotMap(yaml.safe_load(open("./brt.yml")))

# alias method
decode_hex = binascii.unhexlify

class myThread (threading.Thread):
    def __init__(self, conf):
        self.conf = conf
        threading.Thread.__init__(self)
        self.list = []
    def timereps(self, reps, func):
        from time import time
        start = time()
        for i in range(0, reps):
            func()
        end = time()
        return (end - start) / reps
    def gen(self):
		values=[]
		pk=secp256k1.PrivateKey()

		pubbin=pk.pubkey.serialize(False)
		pubkey = binascii.hexlify(pubbin)

		address=self.gen_address(pubkey)
		values.append(pk.private_key)
		values.append(address)
		self.list.append(values);
    def run(self):
        print('Process started pid:'+str(threading.current_thread()))
        max_range = self.conf.worker.batch_and_insert_size
        i = 0
        print self.conf.worker.lifetime
        conn = mariadb.connect(host = self.conf.db.host,
							 user = self.conf.db.user,
							 password = self.conf.db.pwd,
							 database = self.conf.db.db,
							 port = self.conf.db.port)
        cursor = conn.cursor()
        while (self.conf.worker.lifetime == 0 or i < self.conf.worker.lifetime):
            self.list=[]
            #for x in range(0, max_range):
            listdir_time = self.timereps(max_range, lambda: self.gen())
            print("%d generations per second using urandom" % (1 / listdir_time))
            try:
                cursor.executemany("INSERT INTO incoming(private, address) values(%s,%s);", self.list)
                print "committing"
                conn.commit()
                print "commited"
            except MySQLdb.Error,e:
                print "error"
                print e[0], e[1]
                # reconnect
                conn = mariadb.connect(host = self.conf.db.host,
                    user = self.conf.db.user,
                    password = self.conf.db.pwd,
                    database = self.conf.db.db,
                    port = self.conf.db.port)
                cursor = conn.cursor()
            #~ print('Process pid:'+str(threading.current_thread())+' round: '+str(i)+' processed : +'+str(max_range))
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
        
def signal_handler(signal, frame):
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

try:
    threads = []
    for x in range(0, conf.worker.threads):
        thread = myThread(conf)
        thread.daemon = True
        time.sleep(conf.worker.thread_start_delay)
        thread.start()
        threads.append(thread)

except:
    print("Error: unable to start thread")

for thread in threads:
    thread.join(600)

#~ while True:
    #~ time.sleep(1)
