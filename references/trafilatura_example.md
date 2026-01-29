Trafilatura: Overview and main functions
1. Installation
pip install trafilatura

Updating
pip install -U trafilatura

For more info see Installation.

2. Downloads
from trafilatura import fetch_url

document = fetch_url('https://www.example.org')
For parallel and mass downloads see Downloads page.

3. Function extract()
from trafilatura import extract

text = extract(document)
print(text)
This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.
More information...
Several output formats
xml_text = extract(document, output_format='xml')
print(xml_text)
<doc title="Example Domain" categories="" tags="" fingerprint="FYMpE8PW9rnzogCzwvwGlIXzkHw=">
  <main>
    <p>This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.</p>
    <p>More information...</p>
  </main>
  <comments/>
</doc>
Further extraction functions
Documentation pages:

extract
bare_extraction
baseline
extract_metadata
Input formats
Option 1: Unicode strings
# filename = 'myfile.html'
# with open(filename, encoding='utf-8') as f:
#    document = f.read()
# extract(document)
Option 2: Parsed trees (LXML objects)
from lxml import html

tree = html.fromstring(document)
#extract(tree)
Output comparison: Baseline vs. Full extract
from trafilatura import baseline

lxml_object, text, length = baseline(document)
print(text)
text = extract(document)
print(text)
Work with Python objects using bare_extraction()
from trafilatura import bare_extraction

doc_dict = bare_extraction(document)
print(doc_dict.keys())
print(doc_dict['sitename'])
Focus on metadata with extract_metadata()
from trafilatura import extract_metadata

extract_metadata(document)
Text discovery
For more info see documentation page on Python functions.

Feeds
Link discovery over Web Feeds:

from trafilatura.feeds import find_feed_urls

links = find_feed_urls('https://www.nzz.ch')
# 5 first links in the feed
print('\n'.join(links[:5]))
Sitemaps
Link discovery over Sitemaps:

from trafilatura.sitemaps import sitemap_search

links = sitemap_search('https://www.sitemaps.org', target_lang='de')
# 5 first links found in the sitemap
print('\n'.join(links[:5]))
Web crawling
Link discovery over Web Crawling, i.e. exploratory process to find internal links and potential text-based web pages.

Such tools are often called crawler or spider. The pages that are still to visit are often called crawl frontier.

from trafilatura.spider import focused_crawler

to_visit, known_urls = focused_crawler('https://www.telebasel.ch/', max_seen_urls=3)
print(len(to_visit), len(known_urls))
# has to be converted to a list in order to select such slices
print('\n'.join(list(to_visit)[:5]))
print('---')
print('\n'.join(list(known_urls)[:5]))
Pages of the type "author", "category", "page", etc. are visited first.

Limits of web crawling:

to_visit, known_urls = focused_crawler('https://www.zhdk.ch/', max_seen_urls=3)
print(len(to_visit), len(known_urls))
# nothing is found as the content is dynamic in nature
print('\n'.join(list(to_visit)[:5]))
print('---')
print('\n'.join(list(known_urls)[:5]))
For more info see documentation page on Web crawling.

Mass downloads
For "politeness rules" see Downloads
Using already existing web archives:
Internet Archive, CommonCrawl and others sources pour corpus web
Methods, e.g. prefix search with https://index.commoncrawl.org
Tools, e.g. cdx_toolkit
Validation of XML-TEI documents
Validation of output
from trafilatura import bare_extraction
from trafilatura.xml import validate_tei

doc_dict = bare_extraction(document, output_format='xmltei')
tei_tree = doc_dict['body']
# not valid (happens frequently)
validate_tei(tei_tree)
Opening and validating files
from lxml import etree
from trafilatura.xml import validate_tei

# Example: file named "document.xml"
# mytree = etree.parse('document.xml')
# validate_tei(mytree)
# Output: True or False & error message
