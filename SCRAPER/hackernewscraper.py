import pprint #make things preety print
import requests
from bs4 import BeautifulSoup
#think of this as the browser,
#this is also what chrome does to load the browser
res = requests.get(f'https://news.ycombinator.com/')
#gets an envelope that includes all the contents of 
#the html file on the website

"""to work on a while loop and generator that 
keeps pulling data from the site for practice"""

'''pipeline: to learn: scrapy framework (just like a language)'''

#parse it - convert it from a string to something we can use
soup = BeautifulSoup(res.text, 'html.parser')
#(beautifulsoup also works with xml)
#using css selector (to learn)

#will return a list for both the link and votes 
#in the order that they are in
#got timeline and score from inspecting webpage
#.select uses css selectors to instanciate object from the class on html
# The '>' means "find the 'a' tag that is a direct child of 'titleline'"
links = soup.select('.titleline > a')
subtext = soup.select('.subtext')

#sorting the list
def sort_by_votes(hnlist):
    return sorted(hnlist, key = lambda k: k['votes'], reverse=True)

def custom_news(links, subtext):
    hn = []
    # enumerate gives (index, item)
    # we use it to grab title and link at same index
    for idx, item in enumerate(links):

        title = links[idx].getText() #links is an object of beautifulsoup 
        #Now that you have the object, getText() is the tool that 
        #reaches inside and pulls out only the human-readable string
        #.get to get the attribute
        href = links[idx].get('href', None)
        #can use item instead of links[idx] in the for loop
        #as it just returns the item at index as links is a list
        
        #select score class in subtext
        vote = subtext[idx].select('.score')
        #if len of vote is > 0 - it is a list
        #skips number if .score doesn't exist
        if len(vote):
            #get the readable text, replace points with nothing 
            #and convert to int so we can use it
            points = int(vote[0].getText().replace(' points', ''))

            #create a list of dicts if points 99+
            if points > 99:
                hn.append({'Title': title, "Link": href, 'votes': points})
    return sort_by_votes(hn)

pprint.pprint(custom_news(links, subtext))



