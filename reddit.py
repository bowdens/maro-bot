import praw
import time, logging

from tumblr import get_post, TumblrPostNotFoundException, TumblrNotAQuestionPostException

keyword = "markrosewater.tumblr.com"
subredditToStream = "magicTCG"


replyText = """**Question** by **[{}]({})**: *{}*

**Answer**: {}

---

This transcript was made automatically and is not associated with Mark Rosewater. | [Source](https://www.github.com/bowdens/maro-bot) | Send feedback to /u/rzrkyb"""

replyTextAnonymous = """**Question**: *{}*

**Answer**: {}

---

This transcript was made automatically and is not associated with Mark Rosewater. | [Source](https://www.github.com/bowdens/maro-bot) | Send feedback to /u/rzrkyb"""

def create_reply(submission, tumblrPostId):
    res = get_post(tumblrPostId)
    question = res["question"]
    answer = res["answer"]
    asker = res["asking_name"]
    askerUrl = res["asking_url"]
    url = res["short_url"]
    logging.info("Got question/answer from tumblr post {} ({})".format(tumblrPostId, url))
    comment = submission.reply(replyText.format(asker, askerUrl, question, answer))
    logging.info("comment made with id = {}".format(comment.id))


def main():
    reddit = praw.Reddit("maro-transcriber")
    subreddit = reddit.subreddit(subredditToStream)
    logging.basicConfig(filename='maro-logs/maro.log', level=logging.INFO)


    for post in subreddit.stream.submissions():
        url = post.url
        # check its from markrosewater.tumblr.com
        if keyword in url:
            # get id
            paths = url.split('/')
            if len(paths) < 3:
                # no id
                logging.warn("could not identify id from url {} - not enough segments".format(url))
            else:
                id = None
                for path in paths:
                    if path.isdigit():
                        id = path
                if id is None:
                    logging.warn("Could not identify id from url {} - no matching integer segments".format(url))
                else:
                    try:
                        print("Creating post with id={}".format(id))
                        create_reply(post, id)
                    except TumblrPostNotFoundException as e:
                        logging.warn("Tried looking but could not find post with id {}".format(id))
                    except TumblrNotAQuestionPostException as e:
                        logging.warn("found post with id {} but was not in the form of a question".format(id))

        # hide the post when we're done so we won't see it again
        post.hide()

if __name__ == "__main__":
    main()
