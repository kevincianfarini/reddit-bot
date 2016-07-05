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
    reply = ''
    for request in requests:
        link = (get_amazon_link(request))
        if link is not None:
            reply += 'Amazon: [%s](%s)' % (request, link)
            reply += '\n\n'
        else:
            reply += "I couldn't find anything matching %s. Sorry!" % request
            reply += '\n\n'
    reply += 'I am a bot. If you have any feedback that might improve me, send a message!.'
    return reply


def post_reply(comment, reply):
    comment.reply(reply)
    already_answered_comments.append(comment.id)


def check_comments():
    for comment in praw.helpers.comment_stream(r, 'test', limit=10):
        clean_comment = remove_formatting(comment.body)
        requests = link_regex.findall(clean_comment)
        if len(requests) > 0:
            if not already_answered(comment):
                reply = generate_reply(requests)
                post_reply(comment, reply)

check_comments() #TODO: remove this ater testing