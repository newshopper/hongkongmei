import json
import requests
import pprint
from time import sleep


subscription_key = 'YOUR SUBSCRIPTIION KEY'
endpoint = 'YOUR ENDPOINT HERE'

with open('posts.txt') as f:
    json_data = json.load(f)

def extractFields(topic):
    topic_data = json_data[topic]
    posts = {}
    keywords = ["Mei"]
    preview_index = 0
    prettyPrint = pprint.PrettyPrinter(indent=4)
    for data in topic_data:
        teststring = data['title'] + '' + data['selftext']
        if 'post_hint' in data.keys() and data['post_hint'] == 'image' and any(item in teststring for item in keywords):
            
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
            
            if preview_index <= 20:
                image_dict = {}
                imagePreview = data['preview']['images'][0]
                if 'resolutions' in imagePreview and len(imagePreview['resolutions']) > 0:
                    # get the highest resolution image. It resides in the last element in the resolutions array             
                    image = imagePreview['resolutions'][-1]['url']
                    image = image.replace('amp;', '')
                    image_dict['image_id'] = imagePreview['id']
                    image_dict['url'] = image
                    # get OCR and Read batch data 
                    preview_index += 1
                    readImageData = extractImageText(image)
                    image_dict['ocr'] = readImageData
                    data_dict.update({'image_info': image_dict})
                    # prettyPrint.pprint(data_dict)
            
            prettyPrint.pprint(data_dict)
            posts[author].append(data_dict)
    return posts

def extractImageText(imageUrl):
    full_ocr_dict = {}
    # run the OCR and Read batch algorithm here and return the required JSON
    params = {'language': 'unk', 'detectOrientation':'true'}
    headers = {'Content-type': 'application/json', 'Ocp-Apim-Subscription-Key': subscription_key}
    req = requests.post('https://eastus.api.cognitive.microsoft.com/vision/v2.0/ocr', headers=headers, params=params, data=json.dumps({"url":imageUrl}))
    prettyPrint = pprint.PrettyPrinter(indent=4)
   #prettyPrint.pprint(req.json())
    ocr_dict = req.json()
    lines_list = []
    # get the lines
    if 'regions' in ocr_dict:
        regions = ocr_dict['regions']
        for region in regions:
            if 'lines' in region:
                lines = region['lines'] # this should give an array
                # iterate over lines and collect all words
                line_dict = {}
                for index, line in enumerate(lines):
                    words_in_line = ""
                    # each line is a dictionary containing an array of dictionaries under words
                    words_array = line['words']
                    #iterate over words_array
                    for word in words_array:
                        #each word is a dictionary
                        word_text = word['text']
                        words_in_line = words_in_line + ' ' + word_text
                    line_dict[str(index)] = words_in_line
                lines_list.append(line_dict)
    full_ocr_dict['lines'] = lines_list
    
    return full_ocr_dict


def main():
    topic = ['hearthstone','gaming','HongKong','overwatch','blizzard']
    #topic = ['overwatch']
    for name in topic:
        output = extractFields(name)
        print(name)
        with open(name + '.json', 'w') as reddit_data_file:
            json.dump(output, reddit_data_file, indent=4, sort_keys=False)

if __name__ == '__main__':
    main()