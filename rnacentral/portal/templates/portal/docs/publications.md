
# LitScan

RNAcentral **LitScan** has been developed to import articles from [Europe PMC](https://europepmc.org) in order to keep 
the list of publications as up-to-date as possible.

This widget is also an **embeddable component**, which means it can be used by any [Expert Database](/expert-databases).
Find out more about [how to use this widget on your website](https://github.com/RNAcentral/rnacentral-references-embed).

## How it works

A list of Ids, provided by a collaborating group of [Expert Databases](/expert-databases), is exported and used to 
search for articles. The search is performed in **two distinct steps**. 
Exploring [Europe PMC's RESTful WebService](https://europepmc.org/RestfulWebService), the first step looks for articles 
that contain the Id anywhere in the text. The query used is the following:

<img src="/static/img/query-europe-pmc.png">

Where:

- **"id"** is the id used in the search
- **"rna"** is a term used to filter out possible false positives
- **IN_EPMC:Y** means the article must be in the Europe PMC
- **OPEN_ACCESS:Y** it must be an Open Access article to allow access to the full content
- **NOT SRC:PPR** cannot be a Preprint, as they are articles which have not been peer-reviewed from various preprint 
servers and open research platforms such as bioRxiv

Despite the use of quotes to try to retrieve publications that contain the 
exact string, Ids that contain special characters may return articles unrelated to the search term. This is because 
Europe PMC uses [standard Solr tokenizer](https://solr.apache.org/guide/6_6/tokenizers.html#Tokenizers-StandardTokenizer), 
treating whitespaces and some characters as delimiters. The second step of this process takes article by article and 
checks the content. Using a [regex](https://en.wikipedia.org/wiki/Regular_expression), the string is again fetched 
within the article, but this time within the article's title, abstract, and body. **The article will be displayed in the 
results if the Id is found in both steps**.

### Example

The [dme-bantam](/rna/URS00002F21DA/7227) Id returns nine results in the first 
step of the search, as seen [here](https://europepmc.org/search?query=%22dme-bantam%22%20AND%20%22rna%22%20AND%20IN_EPMC%3AY%20AND%20OPEN_ACCESS%3AY%20AND%20NOT%20SRC%3APPR).
The **second step of the search finds the exact string in just three articles**, the other six mention 
[dme-bantam-3p](/rna/URS00004E9E38/7227) and/or [dme-bantam-5p](/rna/URS000055786A/7227). From the article that contains
the exact Id, the system will extract a sentence and other relevant information, such as title, authors, journal, etc.

<img src="/static/img/litscan-dme-bantam.png">

## How often are publications updated?

Publications will be constantly updated, with no predefined time.

## Why is this widget's citation count different from Google Scholar, Web of Science or Scopus?

The citation counts per paper shown by the widget may differ from the counts displayed in Google Scholar, Web of 
Science or Scopus, as Europe PMC does not have access to the same content as these resources. However, highly cited 
articles in Europe PMC correlate with highly cited papers on other platforms. Find out more about the 
[Europe PMC citation network](https://europepmc.org/Help#citationsnetwork).

## Why is my article not on RNAcentral?

If your article is on Europe PMC but not on RNAcentral, this could be because:

* **Your article was recently published and has not yet been imported into our database**
  
  in this case, it may only be a matter of time before your article is listed on RNAcentral

* **Your article does not have any exact Id used in our searches**
  
  new ids will be scanned in the near future and therefore your article can be included

* **Your article is not Open Access in Europe PMC**
  
  unfortunately there's nothing we can do in this case as we don't have access to the article

## How can I know which Ids of a given database were used?

The list of Ids can be accessed programmatically. An example of a Python script to get a list of ids is available 
below.
