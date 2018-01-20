#!/usr/bin/env python
import binascii, hashlib, base58, secp256k1, threading,MySQLdb as mariadb,os,time, yaml
from dotmap import DotMap

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
        print self.conf.worker.lifetime
        while (self.conf.worker.lifetime == 0 or i < self.conf.worker.lifetime):
            print("round ",i)
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
            conn = mariadb.connect(host = self.conf.db.host,
                                 user = self.conf.db.user,
                                 password = self.conf.db.pwd,
                                 database = self.conf.db.db,
                                 port = self.conf.db.port)
            cursor = conn.cursor()

            # try:
            cursor.executemany("INSERT INTO incoming(private,address) values(%s,%s)",list)
            conn.commit()
            print('Process pid:'+str(threading.current_thread())+' processed : +'+str(max_range))
            i += 1
            # except:
            #    conn.rollback()



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
        hash = mainnet_public_key_hash + checksum

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
