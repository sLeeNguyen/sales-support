import json

with open('local.json') as json_file:
    data = json.load(json_file)
    print(data[0])
    for p in data:
        print('province: %s - %d' % (p['name'], len(p['districts'])))

