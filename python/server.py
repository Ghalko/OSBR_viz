import json
import requests

from flask import Flask
from flask import request


HEADERS = {
    'Content-type': 'application/json'
}
URL = 'https://osf.io/api/v1/search/'

app = Flask(__name__)


@app.route('/')
def index():
    with open('../js/example.html') as f:
        return f.read()

@app.route('/contributor/')
def search_contributor():
    guid = request.args.get('guid')
    data = json.dumps({
        'query': {
            'query_string': {
                'default_field': '_all',
                'query': 'contributors_url{} AND (category:project OR category:component OR category:registration)'.format(guid),
                'analyze_wildcard': True,
                'lenient': True  # TODO, may not want to do this
            }
        }
    })

    results = requests.post(URL, headers=HEADERS, data=data).json()

    val = []

    for x in results['results']:
        contributors = []
        for idx,y in enumerate(x['contributors']):
            #Not all contributors have URLs associated with them? How does this affect correlation?
            contributors.append({ 'name': y['fullname'], 'url': y['url'], 'top': False })
        val.append({
            'name': x['title'],
            'children': contributors,
            'url': x['url'],
            'top': True
        })
    return json.dumps({'children': val})

    #return json.dumps({'children':[{
    #    'name': x['title'],
    #    'children': [{'name': x['contributors'],
    #    'url': x['contributors_url']}],
    #    'url': x['url']
    #} for x in results['results']]})


@app.route('/node/')
def search_node():
    guid = request.args.get('guid')
    data = json.dumps({
        'query': {
            'match': {
                'url': guid
            }
        }
    })

    results = requests.post(URL, headers=HEADERS, data=data).json()

    return json.dumps([{
        'children': x['contributors'],
        'contributors_url': x['contributors_url']
    } for x in results['results']])


if __name__ == '__main__':
    app.run()
