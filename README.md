# Reddit Browsing Bot
A bot for quickly searching through your favourite subreddits directly from the command line

# Setup
Create a py file named config_data.py with the following content:

    client_id = 'xxxx'
    client_secret = 'yyyy'
    username = 'user'
    password = 'password'

save config_data.py in the same folder as reddit_browsing_bot_main.py.

Now you're set to go.

# Example of usage
Search for the newest 50 posts mentioning PyCon on the Python subreddit (be verbose)

    reddit_browsing_bot_main.py -s python -k pycon -l 80 -f new -o output.txt -v

Note that the program is not case sensitive. The output is saved in output.txt.
If a file output is not required by the user, the posts and their web addresses will be printed to the console.
If using more than one keyword or subreddit, separate each keyword/subreddit with a comma.

For help on usage, type:

    reddit_browsing_bot_main.py -h
    
or

    reddit_browsing_bot_main.py --help
    
Available flags are 'new', 'rising', 'controversial' and 'top'.
