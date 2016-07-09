import re
import praw
from amazon.api import AmazonAPI, AmazonException

r = praw.Reddit(user_agent="Kevin Cianfarini's reddit bot that sends different prices of items from different sites")
r.login(username='AmazonItBot', password='Scc1122445102795*') #TODO do oath and put in config file
already_answered_comments = []
link_regex = re.compile(r'\bAmazonIt![\s]*(.*?)(?:\.|;|$)', re.M | re.I)

# TODO loop for checking


def remove_formatting(comment):
    return comment.replace("*", "").replace("~", "").replace("^", "").replace(">", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")


def get_amazon_order(item):
    amazon = AmazonAPI('AKIAJ2GNCUSCN4HAJXEA', 'hH5W7wg9gUtpPjroI8Y+7jdCIL4yr/lwEJhjEdmm', 'redditbotli03-20')
    try:
        products = amazon.search_n(1, Keywords=item, SearchIndex='All')
    except AmazonException as e:
        return None
    return products[0]


def already_answered(comment):
    return comment.id in already_answered_comments


def generate_reply(requests):
    reply = ''
    for request in requests:
        product = get_amazon_order(request)
        if product is not None:
            product_info = product.title[:50] + '... ' + str(product.price_and_currency[0]) + ' ' + product.price_and_currency[1]
            reply += 'Amazon: [%s](%s)' % (product_info, product.offer_url)
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
    for comment in praw.helpers.comment_stream(r, 'test'):
        clean_comment = remove_formatting(comment.body)
        requests = link_regex.findall(clean_comment)
        if len(requests) > 0:
            if not already_answered(comment) and comment.author.name != 'kmatthewc':
                reply = generate_reply(requests)
                post_reply(comment, reply)

check_comments()