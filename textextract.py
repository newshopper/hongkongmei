import json

with open('posts.txt') as f:
    json_data = json.load(f)

def extractFields(topic):
    topic_data = json_data[topic]
    posts = {}
    keywords = ["Mei", "China", "hearthstone", "overwatch", "Chinese", "blitzching", "Hong Kong", "democracy",
                "freedom", "revolution", "liberate", "Xi Jinping", "winnie"]
    for data in topic_data:
        if 'preview' in data:
            author = data['author']
            if author not in posts.keys():
                posts[author] = []
            data_dict = {}
            data_dict['post_id'] = data['id']
            data_dict['timestamp'] = data['created_utc']
            data_dict['full_link'] = data['full_link']
            data_dict['gildings'] = data['gildings']
            data_dict['num_crossposts'] = data['num_crossposts']
            data_dict['num_comments'] = data['num_comments']
            data_dict['score'] = data['score']
            data_dict['selftext'] = data['selftext']
            data_dict['title'] = data['title']
            teststring = data['title'] + '' + data['selftext']
            if any(item in teststring for item in keywords):
                posts[author].append(data_dict)


    return posts

def main():
    topic = ['hearthstone','gaming','HongKong','overwatch','blizzard']
    for name in topic:
        output = extractFields(name)
        with open(name + '.json', 'w') as fp:
            json.dump(output, fp)

if __name__ == '__main__':
    main()