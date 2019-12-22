# hongkongmei
hongkongmei is a Reddit proliferation analysis tool that allows users to analyze the reach and impact of an idea as it spreads through Reddit. Starting with an initial or "seed" post, it traces proliferation of the content mentioned in the seed by going through the comments, fetching users from those comments, and looking at their activity. It is an iterative process (breadth first search) which begins fetching content posted on or after the the date the seed post appeared and runs till it fetches all relevant content posted on the end date. 

We started out to build this tool after Activision Blizzard, an American gaming company, came under fire from the esports community in early October when it decided to suspend Chung Ng Wai, a Hong Kong based Hearthstone player, for a year and forced him to forfeit $10,000 worth of prize money. (More context [here](https://kotaku.com/blizzard-subreddit-closes-after-devs-suspend-hearthston-1838880136)).
 
While initially meant as an attempt to understand the proliferation of posts and memes that originated on Reddit after the aforementioned incident, we expanded the scope of the tool so that it could be used to study proliferation of ideas, protests and campaigns on Reddit using a seed post and time range specified by the user.

### API endpoints:
We used [pushshift.io](https://pushshift.io "Pushshift") to fetch posts, comments and user activity from Reddit. Pushshift allows users to filter the response by date, a feature that is not available directly in Reddit's API. However, Pushshift has its own deficiencies, eg; the value of `num_crossposts` returned in the response is always zero, and value for `num_comments` is inaccurate, but we managed to work around them. Another advantage of Pushshift is that users don't need to obtain any API keys.

### Post and comment classification:
We used a machine learning classifier to decide if a post is talking about the Hong Kong protests or not. We collected around 400-500 posts from Reddit and manually tagged them as True or False depending on whether they were relevant to the topic. Accuracy of the classifier is around 80%.
You would have to use your own training data to train the model. The training data should be in comma-separated-value(CSV) format and the columns should be as follows:
> type,author,title,text,id,created_utc,link,is_hk

Training data for Hong Kong protests is available in `post_activity_with_tags.csv` and `comment_activity_with_tags.csv`. The predictions for a sample test file are available in `predictions.csv`. You should divide your training data into comments and posts and tag them manually as shown in the files above. Once that step is complete, run the following command to train and save the classification model:
> python3 hkpostfilter_test.py <comments_training_data.csv> <posts_training_data.csv>

### Setup
To run this tool you need to set up your own PostgreSQL database, and store the database credentials in your computer's environment variables. To create a PostgreSQL database on Amazon Web Services(AWS), please create an AWS account and follow the instructions [here](https://aws.amazon.com/rds/postgresql/). 

Windows users can set environment variables using the following comand:
> set [variable_name]=[variable_value]

Mac users need to set the environment variables in .bash_profile. This file is hidden by default. Once un-hidden, it can be found in the Home directory. Use the following format to set the environment variable:
 > export [variable_name]=[variable_value]

You may have to restart the Terminal for changes to take effect.
We understand that it may be cumbersome for lay users to work through these steps, but for now we don't have a frontend for this tool that would allow users to set everything up using an user interface.

#### Requirements checklist
* Python 3.7+
* A blank PostgreSQL database on Amazon Web Services (AWS) RDS. No need to create any tables.
* Save the following information in your environment variables:
    * endpoint 
    * port
    * username
    * password
    * dbname (database name)

### Running the tool
* Once you download the code or clone the repository, you'll find a folder named `proliferation_pipeline` in the root directory. Navigate to this folder from the terminal.
* Run the script seed.py with the following arguments:
    * Database option: `overwrite` or `update`. Depending on whether you want to overwrite the contents of the database, choose one of the above options.
    * Reddit id: the reddit id of the post you want to use as the initial post.
    * Time range (in seconds): time duration after seed post's creation time till which posts should be retrieved. Eg; if we want to get posts starting from 1:00 PM on Dec. 1, 2019 to 2:00PM on the same day,then the range would be 3600 (60 * 60 * 1).

An example call to `seed.py` would look like this:

> python3 seed.py overwrite degek8 3600

Data collection may take from several minutes to hours, depending on the time range. Once the data is collected in the PostgreSQL database, you can retreive it or run queries on it to continue with your analysis.

### Case study: Mei as a symbol of Hong Kong protests 
On Oct. 6, 2019, Hong Kong-based professional Hearthstone player Ng "Blitzchung" Wai Chung, expressed solidarity with anti-government protestors on a live Esports tournament stream. The video was quickly removed by organizers. However, early the next morning, links to Blitzchung's statement began appearing in posts around Reddit's various subcommunities.

Blizzard, Hearthstone's developer announced the next day that they had suspended Blitzchung from competitive play for a year and would deduct his tournament winnings. Protest posts against the company quickly appeared and spread far throughout the Reddit ecosystem. The Blizzard/Hong Kong controversy dominated various large subreddits for several days and quickly evolved from simple text and links to elaborate memes.

In one notable case, users adopted "Mei," a playable cannonically chinese character from Blizzard's Overwatch game, as a symbol of the Hong Kong protesters. The "Pro-Hong Kong Mei" meme was iterated upon many times and posts featuring her were among the most upvoted of all posts related to the controversy. The speed at which Mei was adopted is a quintessential example of internet subcultures responding to world events in real time.

Using the hongkongmei tool, we developed a better understanding of the driving forces behind the propagation of the protests in Hong Kong. We were able to trace conversation about the protests to hundreds of subreddits and thousands of users. A visualization of related subreddits and the timeline of the proliferation can be found here:
[Hong Kong, Blizzard, gamers and a fight waged on Reddit](https://observablehq.com/@aaronbrezel/hong-kong-blizzard-gamers-and-a-fight-waged-on-reddit, "HongKong").


