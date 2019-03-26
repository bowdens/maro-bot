from secret import TUMBLR_CONSUMER
import requests
from bs4 import BeautifulSoup
url = "https://api.tumblr.com/v2/blog/markrosewater.tumblr.com/posts?api_key={}&id={}"

class TumblrPostNotFoundException(Exception):
    pass

class TumblrNotAQuestionPostException(Exception):
    pass

def get_post(post_id):
    r = requests.get(url.format(CONSUMER, post_id))
    if r.status != 200:
        raise TumblrPostNotFoundException("Post not found - error code: {}".format(r.status))
    res = r.json()["request"]["posts"][0]
    if "question" not in res.keys() or "answer" not in res.keys():
        raise TumblrNotAQuestionPostException("Error: the post was not in the question format")
    question = BeautifulSoup(res["question"]).get_text()
    answer = BeautifulSoup(res["answer"]).get_text()
    return question, answer


