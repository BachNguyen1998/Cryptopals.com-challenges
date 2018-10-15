### Secure Remote Password (SRP)
## A form of authentication in which the client does not need to reveal password
## Server: - stores a verifier for a client that wants to authenticate, 
## 		  v = g ^ x, x = H(salt, password)
##		   - A salt is a random value used to safeguard the password hash from being easily identifiable in a hash lookup rainbow table
##		   - Generate a session key K with verifier
## Client: - After exchaing some parameters with server, generate a session key K with password
## => The server checks client's K == server's K => If true, successfully authenticates the client


import web
import requests
import sys
import time
import thread


sys.path.insert(0, './lib')
from my_crypto_lib import *
from random import randint
from hashlib import sha256

# Server & Client agree on:
N = int("ffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024"
            "e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd"
            "3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec"
            "6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f"
            "24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361"
            "c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552"
            "bb9ed529077096966d670c354e4abc9804f1746c08ca237327fff"
            "fffffffffffff",16) # taken from Diffie-Helman's p
g = 2
k = 3
#I = "ngb1998@gmail.com"
password = "p4$$vv0rd"

# Server's private info:
salt = str(randint(0, 2**32 - 1))
xH = int(ascii_to_hex(sha256(salt+password).digest()), 16)
V = modexp(g, xH, N)
b = randint(0, N-1)
B = (k*V + modexp(g, b, N)) % N
hm = ""
# Retrieve from client:
I = ""
A = 0


# WEB SERVER

urls = (
    '/', 'handle'
)

class handle:
	def POST(self):
		#global hm
		data = web.input(email = "", A = "", hmac = "")
		if len(data.email) != 0 and len(data.A) != 0:
			I = data.email
			A = int(data.A)
			# Compute string uH = SHA256(A|B), u = integer of uH
			uH = sha256(str(A)+str(B)).digest()
			u = int(ascii_to_hex(uH), 16)
			# Generate S = (A * v**u) ** b % N
			S = modexp(A * modexp(V, u, N), b, N)
			# Generate K = SHA256(S)
			K = sha256(str(S).encode()).digest()
			global hm
			hm = hmac_sha256(K, salt)
			# S->C || Send salt, B=kv + g**b % N
			queries = "?salt=" + salt + "&B=" + str(B)
			request = requests.post("http://localhost:8080/" + queries)
		if len(data.hmac) != 0:
			print "Server's key (generated by verifier): " + str(hm) + "\n" + "Client's key (generated with password): " + data.hmac
			if str(hm) == data.hmac:
				# send back OK
				print "ACCEPTED!"
				queries = "?message=Password%20ACCEPTED!"
			else:
				# send back NOT OK
				print "NOT ACCEPTED!"
				queries = "?message=Password%20NOT%20ACCEPTED"
			request = requests.post("http://localhost:8080/" + queries)

        

class MyApplication(web.application):
    def run(self, port = 8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

def run_server():
	app = MyApplication(urls, globals())
	app.run(port = 8888)
	print "Exit thread!"

if __name__ == "__main__":
	thread.start_new_thread(run_server, ())
	#time.sleep(7)
	# S->C || Send salt, B=kv + g**b % N
	# queries = "?salt=" + salt + "&B=" + str(B)
	# request = requests.post("http://localhost:8080/" + queries)
	#time.sleep(2)

	# message = "Hello Client!"
	# request = requests.post("http://localhost:8080/"+"?message="+message)
	# time.sleep(2)
	# message = "Checking Client..."
	# request = requests.post("http://localhost:8080/"+"?message="+message)
	# time.sleep(2)
	# message = "Client Accepted!"
	# request = requests.post("http://localhost:8080/"+"?message="+message)
	time.sleep(20)
	thread.exit()