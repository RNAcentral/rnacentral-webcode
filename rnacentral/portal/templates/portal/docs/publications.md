
# Methodology

RNAcentral has developed a system to import articles from [Europe PMC](https://europepmc.org) in order to keep the 
list of publications as up-to-date as possible. 

## How it works

A list of Ids, provided by a collaborating group of [Expert Databases](/expert-databases), is exported and used to 
search for articles. The search is performed in two distinct steps. 
Exploring [Europe PMC's RESTful WebService](https://europepmc.org/RestfulWebService), the first step looks for articles 
that contain the Id anywhere in the text. Despite the use of quotes to try to retrieve publications that contain the 
exact string, Ids that contain special characters may return articles unrelated to the search term. This is because 
Europe PMC uses [standard Solr tokenizer](https://solr.apache.org/guide/6_6/tokenizers.html#Tokenizers-StandardTokenizer), 
treating whitespaces and some characters as delimiters. The second step of this process takes article by article and 
checks the content. Using a [regex](https://en.wikipedia.org/wiki/Regular_expression), the string is again fetched 
within the article, but this time within the article's title, abstract, and body. The article will be displayed in the 
results if the Id is found.

### Example

The Id [aae-miR-1000](https://www.mirbase.org/cgi-bin/mature.pl?acc=MIMAT0014297) returns three results in the first 
step of the search, as seen [here](https://europepmc.org/search?query=%22aae-miR-1000%22%20AND%20%22rna%22%20AND%20IN_EPMC%3AY%20AND%20OPEN_ACCESS%3AY%20AND%20NOT%20SRC%3APPR).
The second step of the search verifies that only one of the articles has the exact string aae-miR-1000, the other two 
articles mention the Stem-Loop aae-mir-1000-1 and aae-mir-1000-2. From the article that contains the exact Id, the 
system will extract a sentence and other relevant information, such as title, authors, journal, etc.

## How often are publications updated?

Publications will be constantly updated, with no predefined time.

## Why is my article not on RNAcentral?

If your article is on Europe PMC but not on RNAcentral, this could be because:

* Your article was recently published and has not yet been imported into our database. 
* Your article does not have any exact Id used in our searches.

In the first case, it is only a matter of time before your article is listed on RNAcentral. For the second case, 
you can see the list of Ids or check if a certain Id was used by exploring an API, as explained below.

## How can I know if a certain Id was used to search for articles?

Using RF00001 as an example, one can check this by accessing a url like 
> [https://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=entry_type:metadata AND job_id:rf00001&fields=number_of_articles](https://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral?query=entry_type:metadata%20AND%20job_id:rf00001&fields=number_of_articles)

## How can I know which Ids of a given database were used?

The list of Ids can be accessed programmatically. An example of a Python script to get a list of ids is available 
below.
