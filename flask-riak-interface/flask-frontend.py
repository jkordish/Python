__author__ = 'jkordish'

import riak
from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = True

client = riak.RiakClient(host='10.120.10.237', port=8098)

@app.route('/')
def hello_world():

    return 'Hello World!'


@app.route('/cve/')
def cve_world():
    return 'try /cve/cve-number such as /cve/CVE-2012-5301'


@app.route('/cve/<id>')
def cve_get(id):

    id = id
    cve_bucket = client.bucket('cve')

    cve = cve_bucket.get(id)

    links = cve.get_links()


    return render_template('cve_get.html', cve=cve.get_data(), data=links, id=id)

if __name__ == '__main__':
    app.run()
    cve_world()
    cve_get()
