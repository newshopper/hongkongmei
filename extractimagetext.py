import json

PREVIEW_KEY = 'preview'
with open('posts.txt') as posts:
    posts_dict = json.load(posts)
posts.close()

with open('HongKong.json') as hk:
    hk_dict = json.load(hk)

with open('overwatch.json') as overwatch:
    overwatch_dict = json.load(overwatch)

with open('hearthstone.json') as hs:
    hs_dict = json.load(hs)

with open('blizzard.json') as bliz:
    bliz_dict = json.load(bliz)

with open('gaming.json') as gaming:
    gaming_dict = json.load(gaming)

def get_subreddit_dict(subreddit):
   if subreddit == 'blizzard':
       return bliz_dict
   elif subreddit == 'gaming':
        return gaming_dict
   elif subreddit == 'hearthstone':
        return hs_dict
   elif subreddit == 'overwatch':
        return overwatch_dict
   else:
        return hk_dict


def extractImageInfoFrom(subreddit):
    subreddit_dict = posts_dict[subreddit]
    for data in subreddit_dict:
        if PREVIEW_KEY in data:
            # read the postid of the image
            author = data['author']
            post_id = data['id']
            # read the image URL
            imagePreview = data['preview']['images'][0]
            if 'resolutions' in imagePreview and len(imagePreview['resolutions']) > 0:
                # get the highest resolution image. It resides in the last element in the resolutions array             
                image = imagePreview['resolutions'][-1]['url']
                image = image.replace('amp;', '')
                # run OCR and batch read and collect English and Chinese characters
            
            # search for user in the given subreddit file
            subreddit_dict = get_subreddit_dict(subreddit)
            if author in subreddit_dict:
                # search for post id for that user
                posts_author = subreddit_dict[author]
                if not any(d['post_id'] == post_id for d in posts_author):
                    # add new entry under that author and add image information
                else:
                    # append in the entry of that post_id


    # dump back into respective JSON files