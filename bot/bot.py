import re
import praw

r = praw.Reddit(user_agent="Kevin Cianfarini's reddit bot that sends different prices of items from different sites")
r.login(username='kmatthewc', password='Scc102795*')
already_answered_comments = []
link_regex = re.compile(r'\bAmazonIt![\s]*(.*?)(?:\.|;|$)', re.M | re.I)

# TODO loop for checking


def remove_formatting(comment):
    return comment.replace("*", "").replace("~", "").replace("^", "").replace(">", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")


def get_amazon_link(item):
    pass


def already_answered(comment):
    return comment.id in already_answered_comments


def generate_reply(requests):
    links = []
    for request in requests:
        cleaned_request = '' #TODO strip down to item and call get_amazon_link()
        links.append(get_amazon_link(cleaned_request))
    return links.join('\n\n')


def post_reply(comment, reply):
    comment.reply(reply)
    already_answered_comments.append(comment.id)


def check_comments():
    for comment in praw.helpers.comment_stream(r, 'all', limit=10):
        clean_comment = remove_formatting(comment.body)
        requests = link_regex.findall(clean_comment)
        if len(requests) > 0:
            if not already_answered(comment):
                reply = generate_reply(requests)
                post_reply(comment, reply)
