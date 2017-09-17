#!usr/bin/python3

"""
Created on Mon Sep  4 15:06:35 2017

@author: Michy
"""

import os
import praw
import logging
import argparse
import config_data
from datetime import datetime
from prawcore import NotFound

VERSION = '1.0'

def find_relevant_posts(reddit_obj, subreddit_name, keyword, limit=50, flag='new'):
    
    # This function looks for relevant posts in a given subreddit using the supplied
    # keywords.
    #
    # Params:
    # @reddit_obj: a Reddit instance.
    # @subreddit_name: name of the subreddit to be searched (string)
    # @keyword: keyword to be used for the search (string)
    # @limit: maximum number of posts searched (integer).
    # @flag: Reddit's posts flag (string).
    #
    # Returns a tuple of two lists, titles and urls containing the titles and
    # the urls of the relevant posts, respectively.
    #
    
    subreddit = reddit.subreddit(subreddit_name)
    
    if flag == 'new':
        new_submissions = subreddit.new(limit=limit)
    elif flag == 'rising':
        new_submissions = subreddit.rising(limit=limit)
    elif flag == 'controversial':
        new_submissions = subreddit.controversial(limit=limit)
    elif flag == 'top':
        new_submissions = subreddit.top(limit=limit)
    else:
        new_submissions = subreddit.new(limit=limit)
    
    urls = []
    titles = []
    
    for submission in new_submissions:
        if not submission.stickied:
            if keyword in submission.title.lower() or keyword in submission.selftext.lower():
                urls.append(submission.url)
                titles.append(submission.title)
    
    return titles, urls

def find_relevant_posts_wider(reddit_obj, subreddit_names, keywords, limit=50, flag='new'):
    
    # This function looks for relevant posts in each subreddit supplied using the
    # keywords supplied in the keywords argument.
    #
    # Params:
    # @reddit_obj: a Reddit instance.
    # @subreddit_names: names of the subreddit to be searched (list of strings)
    # @keywords: keywords to be used for the search (list of string)
    # @limit: maximum number of posts searched (integer).
    # @flag: Reddit's posts flag (string).
    #
    # Returns a tuple of two lists, titles_wider and urls_wider containing the
    # titles and the urls of the relevant posts, respectively.
    #
    
    titles_wider = []
    urls_wider = []
    
    for subreddit in subreddit_names:
        for keyword in keywords:
            titles, urls = find_relevant_posts(reddit_obj, subreddit, keyword, limit, flag)
            for t, u in zip(titles, urls):
                titles_wider.append(t)
                urls_wider.append(u)

    return titles_wider, urls_wider

def save_findings(titles, urls, filename):
    
    # This function saves the results of the search.
    #
    # Params:
    # @titles: titles of the posts (list of strings).
    # @urls: urls of the posts (list of strings).
    # @filename: name of the file to save (string).
    #
    # Returns void.
    #
    
    filename = os.path.join(os.getcwd(), filename)
    
    if os.path.exists(filename):
        mode = 'a'
    else:
        mode = 'w'
    
    with open(filename, mode) as f:
        for t, u in zip(titles, urls):
            f.write('\n'.join([t, u]))
            f.write('\n\n')
    
    print("Search results saved in {}".format(filename))


def check_subreddit_exists(reddit, subreddit):
    
    # This function checks if a subreddit exists.
    #
    # Params:
    # @reddit: a Reddit instance.
    # @subreddit: subreddit to be checked (string).
    #
    # Returns: True if the subreddit exists, false otherwise.
    #
    
    exists = True
    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
    except NotFound:
        exists = False
    return exists

def check_limit_range(limit):
    
    # This function checks that the limit parameter is in the 1-500 range.
    # If limit is not within the selected range, an ArgumentTypeError is raised.
    #
    # Params:
    # @limit: limit to be checked (integer)
    #
    # Returns: limit
    #
        
    limit = int(limit)
    if limit <= 0 or limit > 500:
         raise argparse.ArgumentTypeError("{} is not a valid value".format(limit))
    return limit

def setup_argparser():
    
    # This function sets up the argument parser.
    #
    # Returns the arguments
    #
    
    parser = argparse.ArgumentParser(description='Reddit Browsing Bot version {}'.format(VERSION))
    parser.add_argument('-s','--subreddits', type=str, required=True, help='Subreddits to look into.')
    parser.add_argument('-k', '--keywords', type=str, required=True, help='Keywords to search for.')
    parser.add_argument('-l', '--limit', type=check_limit_range, default=50, help='Maximum number of searches. Must be included in the range 1 - 500')
    parser.add_argument('-f', '--flag', type=str, default='new', choices=['new', 'rising', 'controversial', 'top'], help='Reddit flags.')
    parser.add_argument('-o', '--output', type=str, help='Output file name.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Be verbose? Prints output if flag is set.')
    
    args = parser.parse_args()
    
    return args

def setup_logger():
    
    # This function sets up the logger.
    #
    # Returns logger.
    #
    
    logging.basicConfig(filename='reddit_bot_log.log', level=logging.DEBUG)
    logger = logging.getLogger(name='Reddit Browsing Bot V. {}'.format(VERSION))
    
    return logger

# Main
if __name__ == '__main__':
    
    # Setup argument parser
    args = setup_argparser()
    # Initialize logger
    logger = setup_logger()
    
    # Retrieve arguments
    subreddits = args.subreddits
    keywords = args.keywords
    limit = args.limit
    flag = args.flag
    filename = args.output
    verbose = args.verbose

    # Initialize reddit instance
    reddit = praw.Reddit(client_id = config_data.client_id,
                         client_secret = config_data.client_secret,
                         username = config_data.username,
                         password = config_data.password,
                         user_agent = 'Reading bot looking for hot topics')
    logger.log(logging.INFO, "Reddit instance initiated.")
    
    # Check if every subreddits exist. Ignore those that do not exist
    subreddits = [sub.lower() for sub in subreddits if check_subreddit_exists(reddit, sub.lower())]
    # Check that length of keywords is > 1. Ignore keywords whose length is < 1
    keywords = [key.lower() for key in keywords if len(key) > 1]
    
    print("Subreddits searched: {} \nKeywords used {}\n\n".format(subreddits, keywords))
    
    # Start search
    logger.log(logging.INFO,
               "Started search for {} in {} at {}".format(keywords,
                                                          subreddits,
                                                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    titles, urls = find_relevant_posts_wider(reddit, subreddits, keywords, limit, flag)
    logger.log(logging.INFO, "Search ended.")
    
    # Save findings if a filename has been provided.
    if filename is not None:
        logger.log(logging.INFO, "Saving data.")
        save_findings(titles, urls, filename)
    
    # If the program needs to be verbose or if filename has not been provided,
    # print output to the console
    if verbose or filename is None:
        for t, u in zip(titles, urls):
            print(t, u, sep='\n', end='\n\n')
    
    # Main ended
    logger.log(logging.INFO, "Main executon ended successfully.")
    print("\n\nExiting....")
    
