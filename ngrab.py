import newspaper
from newspaper import Article
from argparse import ArgumentParser
from sys import stdin,stderr
import articleDateExtractor
import time
import urllib

def gen_iso_8601():
    """Generate an ISO 8601 date+time stamp for the current time in UTC."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def gen_publish_date(datetime):
    """Generate the date of publish from a datetime object, of the form 
    YYYY-MM-DD."""
    month = "0" + str(datetime.month) if datetime.month < 10 else str(datetime.month)
    day = "0" + str(datetime.day) if datetime.day < 10 else str(datetime.day)
    return "{}-{}-{}".format(str(datetime.year), month, day)
    
man = """Grab news article metadata and format it into one of the following:

markdown - [title](url)
json-rss - title, url, id, category, updated"""

parser = ArgumentParser(description=man)

parser.add_argument("type", help="The type of output to give. (eg. markdown)")
parser.add_argument("-f", "--file",
                    help="The filepath to read from. If not given read from " + 
                    "stdout.")

arguments = parser.parse_args()

if arguments.file:
    links_file = open(arguments.file)
    links = links_file.readlines()
else:
    links = stdin.readlines()
    
articles = [newspaper.Article(url=link, language="en") if link != "\n" else None for link in links]
for article in articles:
    if not article:
        next
    article.download()
    try:
        article.parse()
    except newspaper.article.ArticleException:
        stderr.write("Couldn't grab {}!".format(article.url))

if arguments.type == "markdown":
    for article in articles:
        print("[{}]({})".format(article.title,
                                article.url))
elif arguments.type == "json-rss":
    # Generate the id for the article using the procedure described
    # http://web.archive.org/web/20110514113830/http://diveintomark.org/archives/2004/05/28/howto-atom-id
    template = """{{"title":"{}", "link":"{}", "id":"{}", "category":"news","updated":"{}"}}"""
    for article in articles:
        title = article.title
        url = article.url
        pound_url = url.replace("#","/")
        date = articleDateExtractor.extractArticlePublishedDate(url)
        if date:
            date_of_publish = gen_publish_date(date)
        else:
            date_of_publish = "FILL"
        website = "".join(url.split("/")[2].split("www."))
        atom_id = ("tag:" + website
                   + "," + date_of_publish
                   + ":" + pound_url.split(website)[1])
        print(template.format(title, url, atom_id, gen_iso_8601()) + ",")
        
