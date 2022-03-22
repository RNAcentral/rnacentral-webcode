
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
results if the Id is found in both steps.

### Example

The [dme-bantam](/rna/URS00002F21DA/7227) Id returns nine results in the first 
step of the search, as seen [here](https://europepmc.org/search?query=%22dme-bantam%22%20AND%20%22rna%22%20AND%20IN_EPMC%3AY%20AND%20OPEN_ACCESS%3AY%20AND%20NOT%20SRC%3APPR).
The second step of the search finds the exact string in only three articles, the other six mention 
[dme-bantam-3p](/rna/URS00004E9E38/7227) and/or [dme-bantam-5p](/rna/URS000055786A/7227). From the article that contains
the exact Id, the system will extract a sentence and other relevant information, such as title, authors, journal, etc.

## How often are publications updated?

Publications will be constantly updated, with no predefined time.

## Why is my article not on RNAcentral?

If your article is on Europe PMC but not on RNAcentral, this could be because:

* Your article was recently published and has not yet been imported into our database
  * in this case, it is only a matter of time before your article is listed on RNAcentral
* Your article does not have any exact Id used in our searches
  * new ids will be scanned in the near future and therefore your article can be included 
* Your article is not Open Access in Europe PMC
  * unfortunately, there's nothing we can do as we don't have access to the article

## How can I know which Ids of a given database were used?

The list of Ids can be accessed programmatically. An example of a Python script to get a list of ids is available 
below.
