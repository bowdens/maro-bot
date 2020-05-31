from secret import TUMBLR_CONSUMER as CONSUMER
import requests
from bs4 import BeautifulSoup
url = "https://api.tumblr.com/v2/blog/markrosewater.tumblr.com/posts?api_key={}&id={}"

class TumblrPostNotFoundException(Exception):
    pass

class TumblrNotAQuestionPostException(Exception):
    pass

def get_post(post_id):
    r = requests.get(url.format(CONSUMER, post_id))
    if r.status_code != 200:
        raise TumblrPostNotFoundException("Post not found - error code: {}".format(r.status_code))
    res = r.json()["response"]["posts"][0]
    if "question" not in res.keys() or "answer" not in res.keys():
        raise TumblrNotAQuestionPostException("Error: the post was not in the question format")
    question = BeautifulSoup(res["question"],features="lxml").get_text()
    answer = BeautifulSoup(res["answer"], features="lxml").get_text()
    asking_name = res["asking_name"]
    asking_url = res["asking_url"]
    short_url = res["short_url"]
    return {
            "question": question,
            "raw_question": res["question"],
            "answer": answer,
            "raw_answer": res["answer"],
            "asking_name": asking_name,
            "asking_url": asking_url,
            "short_url": short_url
            }


