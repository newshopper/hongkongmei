import json
import operator
import csv
topic = ['hearthstone','gaming','HongKong','overwatch','blizzard']

author = {}
for name in topic:
    with open(name + '.json') as f:
        json_data = json.load(f) 

    for k in sorted(json_data, key=lambda k: len(json_data[k]), reverse=True):
        if k not in author.keys():
            author[k] = len(json_data[k])
        else:
            author[k] += len(json_data[k])

author = sorted(author.items(), key=operator.itemgetter(1), reverse=True)
# print(author)
with open('author.csv', 'w', newline='\n', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['author_id','num_of_post'])
    for row in author:
        writer.writerow(row)