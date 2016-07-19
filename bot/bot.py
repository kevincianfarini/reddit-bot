import re
import praw
import sqlite3
import difflib
import time
from config import AWS, REDDIT_AUTH
from amazon.api import AmazonAPI, AmazonException

r = praw.Reddit(user_agent="Kevin Cianfarini's reddit bot that sends different prices of items from different sites")
r.login(username=REDDIT_AUTH['USERNAME'], password=REDDIT_AUTH['PASSWORD']) #TODO do oath
link_regex = re.compile(r'\bAmazonIt![\s]*(.*?)(?:\.|;|$)', re.M | re.I)
connection = sqlite3.connect('../comments.db')
cursor = connection.cursor()


def create_database():
    connection.execute('''CREATE TABLE IF NOT EXISTS COMMENTS(COMMENT_ID TEXT NOT NULL)''')
    print 'database created'


def remove_formatting(comment):
    return comment.replace("*", "").replace("~", "").replace("^", "").replace(">", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "")


def get_amazon_order(item):
    amazon = AmazonAPI(AWS['AMAZON_KEY'], AWS['SECRET_KEY'], AWS['ASSOCIATE_TAG'])
    try:
        products = amazon.search_n(20, Keywords=item, SearchIndex='All')
        titles = [product.title for product in products]
        matches = difflib.get_close_matches(item, titles)
        if len(matches) > 0:
            return next(product for product in products if product.title == matches[0])
        else:
            return None
    except AmazonException:
        return None


def already_answered(comment):
    cursor.execute("select COMMENT_ID from COMMENTS where COMMENT_ID='%s'" % comment.id)
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
    reply += '**Bleep bloop, I am a bot. I am pretty new so send a message on how to improve!**'
    return reply


def post_reply(comment, reply):
    comment.reply(reply)
    cursor.execute("INSERT INTO COMMENTS (COMMENT_ID) VALUES ('%s')" % comment.id)
    connection.commit()


def handle_rate_limit_reply(comment, reply):
    while True:
        try:
            post_reply(comment, reply)
            break
        except praw.errors.RateLimitExceeded as e:
            print 'sleeping for %d seconds' % e.sleep_time
            time.sleep(e.sleep_time)


def check_comments():
    for comment in praw.helpers.comment_stream(r, 'test'):
        clean_comment = remove_formatting(comment.body)
        requests = link_regex.findall(clean_comment)
        if len(requests) > 0:
            if not already_answered(comment):
                reply = generate_reply(requests)
                handle_rate_limit_reply(comment, reply)

create_database()
check_comments()
