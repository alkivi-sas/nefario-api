from flask import Flask
from redis import Redis
from pepper import Pepper

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


@app.route('/')
def hello():
    count = redis.incr('hits')
    api = Pepper('http://master:8080')
    api.login('test', 'test', 'pam')
    test = api.local('*', 'grains.items')
    return 'Hello Docker! I have been seen {0} times.\n'.format(count) + \
           'test: {0}'.format(test)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
