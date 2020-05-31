import praw
import time, logging
from sys import argv, stdout
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
    u_answer = res["answer"]
    r = praw.models.Redditor(reddit, name="rzrkyb").message("New Post!", "raw q: {}\n\n raw a: {}\n\n q: {}\n\n a: {}\n".format(res["raw_question"], res["raw_answer"], res["question"], res["answer"]))
    answer = u_answer.replace("\n", "  \n")   # replace newlines with two spaces before the newline for reddit markup
    asker = res["asking_name"]
    askerUrl = res["asking_url"]
    url = res["short_url"]
    logging.info("Got question/answer from tumblr post {} ({})".format(tumblrPostId, url))
    try:
        print("creating comment - q: {} a: {}".format(question, answer))
        comment = submission.reply(replyText.format(asker, askerUrl, question, answer))
        logging.info("comment made with id = {}".format(comment.id))
    except praw.exceptions.APIException as e:
        print("comment failed! {}".format(e))
        logging.warn("Could not make comment in response to {} due to api limit: {}".format(submission.id, e))



def main(debug=False):
    reddit = praw.Reddit("maro-transcriber")
    subreddit = reddit.subreddit(subredditToStream)
    logging.basicConfig(stream=stdout, level=logging.INFO)

    while True:
        print("beginning to stream /r/{}".format(subreddit.display_name))
        try:
            for post in subreddit.stream.submissions():
                url = post.url
                print("post found - {} {}".format(post.title, url))
                # check its from markrosewater.tumblr.com
                if keyword in url:
                    # hide the post done so we won't see it again
                    # we're happy to keep seeing repeats of old posts though
                    post.hide()
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
                                print("Creating post with tumblr id={}".format(id))
                                if debug == False:
                                    create_reply(post, id)
                                else:
                                    print("creating fake response to tumblr {}, reddit {}".format(id, post.url))
                            except TumblrPostNotFoundException as e:
                                logging.warn("Tried looking but could not find post with id {}".format(id))
                            except TumblrNotAQuestionPostException as e:
                                logging.warn("found post with id {} but was not in the form of a question".format(id))
        except Exception as e:
            logging.error("Submission streaming broke with error: {}".format(e))
            print("Streaming broke, sleeping then trying again (check logs for error)")
            time.sleep(30)
            logging.info("Restarting streaming...")

if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == "--debug":
            print("running in debug mode (no posts made)")
            main(debug=True)
            exit(0)
    print("running for real")
    main()
