import json

PREVIEW_KEY = 'preview'
SUBRED_BLIZZARD = 'blizzard'
SUBRED_GAMING = 'gaming'
SUBRED_HONGKONG = 'HongKong'
SUBRED_OVERWATCH = 'overwatch'
SUBRED_HEARTHSTONE = 'hearthstone'

with open('posts.txt') as posts:
    posts_dict = json.load(posts)
posts.close()

with open(SUBRED_HONGKONG + '.json') as hk:
    hk_dict = json.load(hk)

with open(SUBRED_OVERWATCH + '.json') as overwatch:
    overwatch_dict = json.load(overwatch)

with open(SUBRED_HEARTHSTONE + '.json') as hs:
    hs_dict = json.load(hs)

with open(SUBRED_BLIZZARD + '.json') as bliz:
    bliz_dict = json.load(bliz)

with open(SUBRED_GAMING + '.json') as gaming:
    gaming_dict = json.load(gaming)

def get_subreddit_dict(subreddit):
   if subreddit == SUBRED_BLIZZARD:
       return bliz_dict
   elif subreddit == SUBRED_GAMING:
        return gaming_dict
   elif subreddit == SUBRED_HEARTHSTONE:
        return hs_dict
   elif subreddit == SUBRED_OVERWATCH:
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