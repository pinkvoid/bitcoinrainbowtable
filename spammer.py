#!/usr/bin/env python
import binascii, hashlib, base58, secp256k1, threading, MySQLdb,os,time, yaml, time
from dotmap import DotMap
import signal, sys

conf = DotMap(yaml.safe_load(open("./brt.yml")))

decode_hex = binascii.unhexlify

class myThread (threading.Thread):
    conn = None
    conf = None
    cursor = None
    thread_id = 0
    rows = []

    def __init__(self, conf, thread_id):
        self.conf = conf
        threading.Thread.__init__(self)
        self.list = []
        self.thread_id = thread_id

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
	self.rows.append(values);

    def connect(self):
        if(not self.conf.db.pwd):
            self.conn = MySQLdb.connect(host = self.conf.db.host,
                user = self.conf.db.user,
                database = self.conf.db.db)
        else:
            self.conn = MySQLdb.connect(host = self.conf.db.host,
                user = self.conf.db.user,
                password = self.conf.db.pwd,
                database = self.conf.db.db,
                port = self.conf.db.port)
        self.cursor = self.conn.cursor()

    def closeConnection(self):
        self.close()
        self.conn.close()
    
    def savegen(self):
        saved = None
        while( not saved):
            try:
                self.cursor.executemany("INSERT INTO incoming(private, address) values(%s, %s);", self.rows)
                self.conn.commit()
                saved = True
            except (MySQLdb.Error, MySQLdb.Warning) as e:
                print(e)
                print("Reconnecting...")
                self.connect()


    def run(self):
        self.connect()
        print('Thread %s started' % self.thread_id)
        max_range = self.conf.worker.batch_and_insert_size
        i = 0
        while (self.conf.worker.lifetime == 0 or i < self.conf.worker.lifetime):
                self.rows=[]
                listdir_time = self.timereps(max_range, lambda: self.gen())
                print("Thread %d : %d keypairs/s" % (self.thread_id, 1 / listdir_time))
                self.savegen()
                i += 1
        self.closeConnection()

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
        return decode_hex(hash)

# Main :
        
def signal_handler(signal, frame):
        print('Manual exit')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    threads = []
    for x in range(0, conf.worker.threads):
        thread = myThread(conf, x + 1)
        thread.daemon = True
        time.sleep(conf.worker.thread_start_delay)
        thread.start()
        threads.append(thread)

except:
    print("Error: unable to start thread")

for thread in threads:
    thread.join(600)
