
<h1 id="overview">
  <i class="fa fa-book"></i> API overview
</h1>

Most data in RNAcentral can be accessed programmatically using a RESTful API
allowing for integration with other resources.
The API implementation is based on the [Django Rest Framework](http://www.django-rest-framework.org/).

<h2 id="web-browsable-api">Web browsable API</h2>

The RNAcentral API is **web browsable**, which means that:

* the data is served in either **human- or computer-friendly formats** depending on whether
a URL is viewed in a browser or is retrieved programmatically

* many resources are **hyperlinked** so that it's possible to navigate the API in the browser.

As a result, developers can familiarise themselves with the API and get a better sense of the RNAcentral data.

<a href="/api/v1" class="btn btn-primary" role="button" target="_blank">Browse the API</a>

<h2 id="versioning">Versioning</h2>

To ensure that changes in the RNAcentral API don't break the applications
relying on it, the API is versioned, and **the version is included in the API's URL**.

For example, the **current API is at Version 1** and is available at [{{ BASE_URL }}/api/v1](/api/v1),
and the next version will be available at {{ BASE_URL }}/api/v2.

The **latest version** of the API can be accessed at [{{ BASE_URL }}/api/current](/api/current),
but it's not recommended to use this endpoint for long-term
development as the underlying data model may change.

No **backward-incompatible changes** are made to each version after it's been made public.
More specifically, it's guaranteed that within one version there will be no:

* changing urls
* deleting or renaming data fields
* changing data field types

The following **non-disruptive changes** may be implemented to a public API:

* adding new endpoints
* adding new data fields
* adding new filtering methods

An advance notice will be given before obsoleting an API version. To stay up to date,
please consider signing up for the [RNAcentral updates](http://blog.rnacentral.org).

<h2 id="throttling">Throttling</h2>

The maximum number of requests from the same IP address is limited to **20 requests per second**.
Currently there is no limit on the total number of requests from the same IP.

The limit can be lifted for registered users, so please get in touch if you require a higher request rate.

<hr>

<h1 id="v1">API v1 documentation</h1>

<h2 id="v1-example-responses">Example responses</h2>

Responses containing **multiple entries** have the following fields:

* *count* is the number of entries in the matching set
* *next* and *previous* are urls to the corresponding results page
* *results* is an array of entries.

#### Example

```
{{ BASE_URL }}/api/v1/rna/
{
    "count": 6493837,
    "next": "{{ BASE_URL }}/api/v1/rna/?page=2",
    "previous": null,
    "results": [
        {
            "url": "{{ BASE_URL }}/api/v1/rna/URS0000000001",
            "rnacentral_id": "URS0000000001",
            "md5": "06808191a979cc0b933265d9a9c213fd",
            "sequence": "CUGAAUAAAUAAGGUAUCUUAUAUCUUUUAAUUAACAGUUAAACGCUUCCAUAAAGCUUUUAUCCA",
            "length": 66,
            "xrefs": "{{ BASE_URL }}/api/v1/rna/URS0000000001/xrefs"
        },

        // 9 more entries
    ]
}
```

Responses containing just a **single entry** don't have the extra navigation fields:

```
{{ BASE_URL }}api/v1/rna/URS0000000001
{
    "url": "{{ BASE_URL }}/api/v1/rna/URS0000000001",
    "rnacentral_id": "URS0000000001",
    "md5": "06808191a979cc0b933265d9a9c213fd",
    "sequence": "CUGAAUAAAUAAGGUAUCUUAUAUCUUUUAAUUAACAGUUAAACGCUUCCAUAAAGCUUUUAUCCA",
    "length": 66,
    "xrefs": "{{ BASE_URL }}/api/v1/rna/URS0000000001/xrefs"
}
```

<h3 id="v1-hyperlinked-vs-flat-responses">Hyperlinked vs flat responses</h3>

Some objects are represented by hyperlinks, for example in the default RNA object cross-references are represented by a hyperlink:

```
"xrefs": "{{ BASE_URL }}/api/v1/rna/URS0000000001/xrefs/"
```

Sometimes it is desirable to retrieve all nested objects in a single request,
which can be done using the `flat=true` url parameter.
Note that such requests may take longer.

#### Examples

* [{{ BASE_URL }}/api/v1/rna/](/api/v1/rna/) (hyperlinked)
* [{{ BASE_URL }}/api/v1/rna/?flat=true](/api/v1/rna/?flat=true) (flat)
* [{{ BASE_URL }}/api/v1/rna/URS0000000001](/api/v1/rna/URS0000000001) (hyperlinked)
* [{{ BASE_URL }}/api/v1/rna/URS0000000001/?flat=true](/api/v1/rna/URS0000000001/?flat=true) (flat)

<h2 id="v1-pagination">Pagination</h2>

Responses containing multuple entries are paginated to prevent accidental downloads of large amounts of data and to speed up the API.

To navigate between pages, specify the `page` parameter.

The page size is controlled by the `page_size` parameter. Its default value is
**10 entries per page**, and the maximum number of entries per page is **100**.

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?page_size=5](/api/v1/rna/?page_size=5)
* [{{ BASE_URL }}/api/v1/rna/?page=2&page_size=5](/api/v1/rna/?page_size=5&page=2)

<h2 id="v1-output-formats">Output formats</h2>

The following output formats are supported for all endpoints:
**JSON**, **JSONP** (for cross-origin Javascript requests), **YAML**, **HTML**.

In addition, the data for individual RNA sequences can be downloaded in **FASTA** format.
For those sequences that have genomic coordinates
**[GFF2](http://www.sanger.ac.uk/resources/software/gff/spec.html)**, **[GFF3](http://www.sequenceontology.org/gff3.shtml)**, and **[BED](http://genome.ucsc.edu/FAQ/FAQformat.html)** formats are available.

There are three ways of specifying the format:

1. `format` url parameter
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=json](/api/v1/rna/URS0000000001/?format=json)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=fasta](/api/v1/rna/URS0000000001/?format=fasta)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=yaml](/api/v1/rna/URS0000000001/?format=yaml)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=api](/api/v1/rna/URS0000000001/?format=api)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371/?format=bed](/api/v1/rna/URS000063A371/?format=bed)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371/?format=gff](/api/v1/rna/URS000063A371/?format=gff)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371/?format=gff3](/api/v1/rna/URS000063A371/?format=gff3)

2. format suffix
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.json](/api/v1/rna/URS0000000001.json)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.fasta](/api/v1/rna/URS0000000001.fasta)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.yaml](/api/v1/rna/URS0000000001.yaml)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.api](/api/v1/rna/URS0000000001.api)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371.bed](/api/v1/rna/URS000063A371.bed)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371.gff](/api/v1/rna/URS000063A371.gff)
  * [{{ BASE_URL }}/api/v1/rna/URS000063A371.gff3](/api/v1/rna/URS000063A371.gff3)

3. [Accept headers](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html)

  ```
  curl -H "Accept: application/json" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: text/fasta" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: application/yaml" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: text/html" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: text/bed" {{ BASE_URL }}/api/v1/rna/URS000063A371
  curl -H "Accept: text/gff" {{ BASE_URL }}/api/v1/rna/URS000063A371
  curl -H "Accept: text/gff3" {{ BASE_URL }}/api/v1/rna/URS000063A371
  ```

In case there is a conflict between the Accept headers and the format parameter, an error message is returned, for example:

```
curl -H "Accept: application/json" {{ BASE_URL }}/api/v1/?format=yaml
or
curl -H "Accept: application/yaml" http://127.0.0.1:8000/api/v1/?format=json
{
  "detail": "Could not satisfy the request's Accept header"
}
```

<h2 id="v1-filtering">Filtering</h2>

The API supports several filtering operations that complement the main RNAcentral search functionality.

<h3 id="v1-filtering-by-sequence-length">Filtering by sequence length</h3>

There are 3 url parameters: `length`, `min_length` (greater or equal length), and `max_length` (less or equal length).

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?length=2014](/api/v1/rna/?length=2014)
* [{{ BASE_URL }}/api/v1/rna/?min_length=200000](/api/v1/rna/?min_length=200000)
* [{{ BASE_URL }}/api/v1/rna/?max_length=10](/api/v1/rna/?max_length=10)
* [{{ BASE_URL }}/api/v1/rna/?min_length=1&max_length=4](/api/v1/rna/?min_length=1&max_length=4)

<h3 id="v1-filtering-by-database">Filtering by database</h3>

The expert database can be specified by setting the `database` url parameter
(possible values: *srpdb*, *mirbase*, *vega*, *tmrna_website*, *lncrnadb*, *gtrnadb*, *ena*, *rdp*, *rfam*, *refseq*).

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?database=srpdb](/api/v1/rna/?database=srpdb)
* [{{ BASE_URL }}/api/v1/rna/?database=mirbase](/api/v1/rna/?database=mirbase)
* [{{ BASE_URL }}/api/v1/rna/?database=vega](/api/v1/rna/?database=vega)
* [{{ BASE_URL }}/api/v1/rna/?database=tmrna_website](/api/v1/rna/?database=tmrna_website)
* [{{ BASE_URL }}/api/v1/rna/?database=lncrnadb](/api/v1/rna/?database=lncrnadb)
* [{{ BASE_URL }}/api/v1/rna/?database=gtrnadb](/api/v1/rna/?database=gtrnadb)
* [{{ BASE_URL }}/api/v1/rna/?database=ena](/api/v1/rna/?database=ena)
* [{{ BASE_URL }}/api/v1/rna/?database=rdp](/api/v1/rna/?database=rdp)
* [{{ BASE_URL }}/api/v1/rna/?database=rfam](/api/v1/rna/?database=rfam)
* [{{ BASE_URL }}/api/v1/rna/?database=refseq](/api/v1/rna/?database=refseq)

<h3 id="v1-filtering-by-external-ids">Filtering by external ids</h3>

The external id is an id assigned to a sequence in one of the Expert Databases,
which is imported into RNAcentral as a cross-reference.

The external id can be specified by setting the `external_id` url parameter.

#### Examples

* <a href="/api/v1/rna/?external_id=Stap.epid._AF269831" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=Stap.epid._AF269831</a> (SRPDB)
* <a href="/api/v1/rna/?external_id=MIMAT0000091" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=MIMAT0000091</a> (miRBase)
* <a href="/api/v1/rna/?external_id=OTTHUMG00000172092" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=OTTHUMG00000172092</a> (VEGA)
* <a href="/api/v1/rna/?external_id=Lepto_inter_Lai566" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=Lepto_inter_Lai566</a> (tmRNA Website)

<h3 id="v1-combined-filters">Combined filters</h3>

Any filters can be combined to narrow down the query using the `&` symbol as a separator,
which acts as the logical `AND` operator. More logical operators will be supported in the future.

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?database=srpdb&min_length=200](/api/v1/rna/?database=srpdb&min_length=200)
* [{{ BASE_URL }}/api/v1/rna/?min_length=1&max_length=4](/api/v1/rna/?min_length=1&max_length=4)

<h2 id="v1-genome-annotations">Genome annotations</h2>

The API provides an endpoint for retrieving annotations based on genomic coordinates.
Genome annotations are available for all sequences from [VEGA](/expert-database/vega).
Only **human genome** is currently supported, but more data from more genomes will become available in future.

The response content is similar to that provided by the
[Ensembl REST API](http://rest.ensembl.org/documentation/info/overlap_region)
and can be directly used to visualise the data using the [Genoverse](http://genoverse.org) HTML5 genome browser.

The genome location should be in the `chromosome:start-end` format and may contain optional commas.

#### Examples

* [{{ BASE_URL }}/api/v1/overlap/region/human/Y:26,631,479-26,632,610](/api/v1/overlap/region/human/Y:26,631,479-26,632,610)
* [{{ BASE_URL }}/api/v1/overlap/region/human/2:39,745,816-39,826,679](/api/v1/overlap/region/human/2:39,745,816-39,826,679)

<h2 id="v1-example-script">Example script</h2>

A common task is finding whether some sequence of interest has an RNAcentral id.

An example **Python** script for **looking up RNAcentral unique sequence ids** (URS) is provided
and can be used in more complicated programs.

Instead of sending the entire sequence over the network to the RNAcentral servers,
the script only submits the [md5](http://en.wikipedia.org/wiki/MD5) value
calculated based on the sequence. The md5 value is 32 characters long and is unique
for each sequence. Using md5 saves traffic and decreases the response time.

Internally RNAcentral uses the [Digest::MD5](http://search.cpan.org/dist/Digest-MD5/MD5.pm)
Perl module for computing the md5 values. Additional notes:

* all sequences are uppercase
* md5 is computed for DNA sequences (so all U's should be replaced with T's).

{# embedded GitHub gist #}
<script src="https://gist.github.com/AntonPetrov/177cef0a3b4799f01536.js"></script>

<h2 id='v1-cross-domain-requests'>Cross domain requests</h2>

To use the API in a javascript application, please use jsonp requests.

#### Example using jQuery

```
$.ajax({
    url: '{{ BASE_URL }}/api/v1/rna/URS0000000001?format=jsonp',
    dataType: 'jsonp',
    jsonp: false,
    jsonpCallback: 'callback',
    success: function(data){
        // do something with the data
        console.log(data.rnacentral_id + ', ' + data.sequence);
    },
});
```

<h2 id="v1-trailing-slash">Trailing slash</h2>

The trailing slash in all urls used in the API is **optional**.

#### Examples

These requests should return the same results, both in the browser and when retrieved programmatically:

* [{{ BASE_URL }}/api/v1](/api/v1)
* [{{ BASE_URL }}/api/v1/](/api/v1/)
