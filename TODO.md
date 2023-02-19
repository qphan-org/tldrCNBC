# To-do List

[X] Check if the color scheme is appropriate

[X] Create a way to store db json files temporary in tldrcnbc server, instead of having to request from the MongoDB database --> cut down cost. (Note that there are some programings out there keep requesting response (aka scraping) from tldrcnbc.com, causing a spike in cost to run the website to $5 per day)

[ ] Create a log function that log all the DB request for analytics, and maybe log the ip address of requests too.

[ ] MongoDB Database API limits the maximum number of article per request up to 1000. Need to write a code to deal with this issue.
