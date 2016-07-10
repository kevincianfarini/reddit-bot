import re
import praw
import sqlite3
from config import AWS, REDDIT_AUTH
from amazon.api import AmazonAPI, AmazonException

r = praw.Reddit(user_agent="Kevin Cianfarini's reddit bot that sends different prices of items from different sites")
r.login(username=REDDIT_AUTH['USERNAME'], password=REDDIT_AUTH['PASSWORD']) #TODO do oath and put in config file
link_regex = re.compile(r'\bAmazonIt![\s]*(.*?)(?:\.|;|$)', re.M | re.I)
connection = sqlite3.connect('comments.db')
cursor = connection.cursor()


def create_database():
    connection.execute('''CREATE TABLE IF NOT EXISTS COMMENTS(COMMENT_ID TEXT NOT NULL)''')
    print 'database created'


def remove_formatting(comment):
    return comment.replace("*", "").replace("~", "").replace("^", "").replace(">", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")


def get_amazon_order(item): #TODO config file to hide this
    amazon = AmazonAPI(AWS['AMAZON_KEY'], AWS['SECRET_KEY'], AWS['ASSOCIATE_TAG'])
    try:
        products = amazon.search_n(1, Keywords=item, SearchIndex='All')
    except AmazonException as e:
        return None
    return products[0]


def already_answered(comment):
    cursor.execute('select COMMENT_ID from COMMENTS where COMMENT_ID=%s' % comment.id)
    data = cursor.fetchall()
    return len(data) > 0


def generate_reply(requests):
    reply = ''
    for request in requests:
        product = get_amazon_order(request)
        if product is not None:
            product_info = product.title[:50] + '... ' + str(product.price_and_currency[0]) + ' ' + \
                           product.price_and_currency[1]
            reply += '* Amazon: [%s](%s)' % (product_info, product.offer_url)
            reply += '\n\n'
        else:
            reply += "* I couldn't find anything matching %s. Sorry!" % request
            reply += '\n\n'
    reply += '**I am a bot. If you have any feedback that might improve me, send a message!**'
    return reply


def post_reply(comment, reply):
    comment.reply(reply)
    cursor.execute('INSERT INTO COMMENTS VALUES %s' % comment.id)
    connection.commit()


def check_comments():
    for comment in praw.helpers.comment_stream(r, 'test'):
        clean_comment = remove_formatting(comment.body)
        requests = link_regex.findall(clean_comment)
        if len(requests) > 0:
            if not already_answered(comment):
                reply = generate_reply(requests)
                post_reply(comment, reply)

create_database()
check_comments()