# Doctors in KW

Finding doctors in a specific area is hard even though the data is publicly available as part of their licensing.

This aims to list all doctors in a specific region ranked by the location.

TODO:
1. Scrape CPSO for doctors in Kitchener, save to file

    I attempted using an existing scraper. It gave me a good head-start but didn't work out of the box. Crawling the site proved to be very difficult.
    I ended up manually downloading the 35 pages.
    Much of the struggle was working with response and beautiful soup for navigating and clicking on boxes. In the future I would use puppeteer for crawling

2. parse files to make tabular data from html listing

3. rank by distance using location
