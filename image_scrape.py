import praw
import pprint
import datetime
import requests
# User-Agent: android:com.example.myredditapp:v1.2.3 (by /u/kemitche)

clientId = 'v7f2THUITIen3w'
clientSecret = 'c9_FiE0sv2F1pDnIricnAhd7Qq0'
userAgent = 'script:com.example.Crawler:v1.0 (by /u/bhsgsh)'

reddit = praw.Reddit(client_id=clientId,
                     client_secret=clientSecret,
                     user_agent=userAgent,
                     username='bhsgsh',
                     password='ka01bhs#X8389')


# for submission in reddit.subreddit('blizzard').hot(limit=10):
#     print(submission.title)

# subreddit = reddit.subreddit('blizzard')
# # print(subreddit.display_name)  # Output: redditdev
# # print(subreddit.title)         # Output: reddit Development
# # print(subreddit.description)
pp = pprint.PrettyPrinter(indent=4)
# #pprint(vars(subreddit.controversial[0]))
# epoch1 = 1570723200
# epoch2 = 1570496400
# #allSubmissions = list(reddit.search('timestamp:{}..{}'.format(epoch2, epoch1), subreddit=subreddit, syntax='cloudsearch'))
# for index, submission in enumerate(subreddit.new(limit=100)):
    
#     print(submission.title)
#     print(datetime.datetime.fromtimestamp(submission.created))

#submission = reddit.submission(id='dfvs09')

api_endpoint = 'https://api.pushshift.io/reddit/search/submission/'
params = {
    'subreddit':'blizzard',
    'before':1570496400,
    'count':100
}
request = requests.get(url=api_endpoint,params=params)
if request.status_code == 200:

    response = request.json()
    for submission in response['data']:
        # print(submission['selftext'])
        if 'preview' in submission:
            image = submission['preview']['images'][0]['resolutions'][0]['url']
            image = image.replace('amp;', '')
            pp.pprint(image)

else:
    print('Something went wrong')
    print(request.status_code)
