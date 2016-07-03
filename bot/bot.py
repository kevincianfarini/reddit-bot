import re
import praw

r = praw.Reddit(user_agent="Kevin Cianfarini's reddit bot that sends different prices of items from different sites")
r.login(username='kmatthewc', password='Scc102795*')
checked = []
link_regex = re.compile(r'\bAmazonIt![\s]*(.*?)(?:\.|;|$)', re.M | re.I)

# TODO loop for checking


def get_amazon_link(link):
    pass


def check_comments():
    for comment in praw.helpers.comment_stream(r, 'all', limit=10):
        link_requests = link_regex.findall(comment.body)

