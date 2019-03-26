import praw
import time, logging

from tumblr import get_post, TumblrPostNotFoundException, TumblrNotAQuestionPostException

reddit = praw.Reddit("maro-transcriber")
subreddit = reddit.subreddit("rzrkyb")
logging.basicConfig(filename='maro.log', level=logging.DEBUG)

keyword = "markrosewater.tumblr.com"

lastCheckedPost = 0

while True:
    maxPost = 0
    posts = list(subreddit.new())
    # put newer submissions at the end of the list
    posts.reverse()
    for post in posts:
        if post.created_utc > lastCheckedPost:
            url = post.url
            if keyword in url:
                # get id
                paths = url.split('/')
                if len(paths) < 3:
                    # no id
                    logging.warn("could not identify id from url {}".format(url))
                else:
                    id = paths[2]
                    logging.info("id found - {}".format(id))
                    try:
                        question, answer = get_post(id)
                        logging.info("Got question/answer from tumblr post {}".format(id))
                        comment = post.reply("**Question**: *{}*\n\n**Answer**: {}\n\n---\n\nThis comment was created automatically with [maro-bot](https://www.github.com/bowdens/maro-bot) | Report issues to /u/rzrkyb".format(question, answer))
                        logging.info("comment made with id = {}".format(comment.id))

                    except TumblrPostNotFoundException as e:
                        logging.warn("Tried looking but could not find post with id {}".format(id))
                    except TumblrNotAQuestionPostException as e:
                        logging.warn("found post with id {} but was not in the form of a question".format(id))



            lastCheckedPost = post.created_utc
    time.sleep(30)
    print("\nrestarting")
