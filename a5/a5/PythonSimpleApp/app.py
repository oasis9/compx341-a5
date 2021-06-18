import time
import math
import json

import redis
from flask import Flask

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379, decode_responses=True)


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def storePrime(number):
    if (cache.exists('data')):
        data = cache.get('data')
    else:
        data = '[]'
    primes = json.loads(data)
    primes.append(number)
    cache.set('data', json.dumps(primes))

def checkPrime(number):
    if (cache.exists('data')):
        data = cache.get('data')
        primes = json.loads(data)
        if (number in primes):
            return True

    if (number < 2):
        return False
    if (number == 2):
        storePrime(number)
        return True
    if (number % 2 == 0):
        return False

    i = 3
    to = math.sqrt(number)
    while i <= to:
        if (number % i == 0):
            return False
        i += 2

    storePrime(number)
    return True

@app.route('/isPrime/<int:number>')
def isPrime(number):
    result = checkPrime(number)
    if (result == True):
        return '{}'.format(number) + " is prime\n"
    else:
        return '{}'.format(number) + " is not prime\n"

@app.route('/primesStored')
def primesStored():
    if (not cache.exists('data')):
        return '[]'

    data = cache.get('data')
    primes = json.loads(data)
    return str(primes) + '\n'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
