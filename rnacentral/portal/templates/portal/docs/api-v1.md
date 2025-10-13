
# <i class="fa fa-book" id="overview"></i> API overview

Most data in RNAcentral can be accessed programmatically using a RESTful API
allowing for integration with other resources.
The API implementation is based on the [Django Rest Framework](http://www.django-rest-framework.org/).

## Web browsable API <a style="cursor: pointer" id="web-browsable-api" ng-click="scrollTo('web-browsable-api')" name="web-browsable-api" class="text-muted smaller"><i class="fa fa-link"></i></a>

The RNAcentral API is **web browsable**, which means that:

* the data is served in either **human- or computer-friendly formats** depending on whether
a URL is viewed in a browser or is retrieved programmatically

* many resources are **hyperlinked** so that it's possible to navigate the API in the browser.

As a result, developers can familiarise themselves with the API and get a better sense of the RNAcentral data.

<a href="/api/v1" class="btn btn-primary" role="button" target="_blank">Browse the API</a>

## Versioning <a style="cursor: pointer" id="versioning" ng-click="scrollTo('versioning')" name="versioning" class="text-muted smaller"><i class="fa fa-link"></i></a>

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
please consider signing up for the [RNAcentral updates](https://blog.rnacentral.org).

## Throttling <a style="cursor: pointer" id="throttling" ng-click="scrollTo('throttling')" name="throttling" class="text-muted smaller"><i class="fa fa-link"></i></a>

The maximum number of requests from the same IP address is limited to **20 requests per second**.
Currently, there is no limit on the total number of requests from the same IP.

The limit can be lifted for registered users, so please get in touch if you require a higher request rate.

<hr>

# API v1 documentation <a style="cursor: pointer" id="v1" ng-click="scrollTo('v1')" name="v1" class="text-muted smaller"><i class="fa fa-link"></i></a>

## Example responses <a style="cursor: pointer" id="v1-example-responses" ng-click="scrollTo('v1-example-responses')" name="v1-example-responses" class="text-muted smaller"><i class="fa fa-link"></i></a>

Responses containing **multiple entries** have the following fields:

* *next* and *previous* are urls to the corresponding results page
* *results* is an array of entries.

#### Example

```
{{ BASE_URL }}/api/v1/rna/
{
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
{{ BASE_URL }}/api/v1/rna/URS0000000001
{
    "url": "{{ BASE_URL }}/api/v1/rna/URS0000000001",
    "rnacentral_id": "URS0000000001",
    "md5": "06808191a979cc0b933265d9a9c213fd",
    "sequence": "CUGAAUAAAUAAGGUAUCUUAUAUCUUUUAAUUAACAGUUAAACGCUUCCAUAAAGCUUUUAUCCA",
    "length": 66,
    "xrefs": "{{ BASE_URL }}/api/v1/rna/URS0000000001/xrefs"
}
```

### Hyperlinked vs flat responses <a style="cursor: pointer" id="v1-hyperlinked-vs-flat-responses" ng-click="scrollTo('v1-hyperlinked-vs-flat-responses')" name="v1-hyperlinked-vs-flat-responses" class="text-muted smaller"><i class="fa fa-link"></i></a>

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

##Pagination <a style="cursor: pointer" id="v1-pagination" ng-click="scrollTo('v1-pagination')" name="v1-pagination" class="text-muted smaller"><i class="fa fa-link"></i></a>

Responses containing multiple entries are paginated to prevent accidental downloads of large amounts of data and to speed up the API.

To navigate between pages, specify the `page` parameter.

The page size is controlled by the `page_size` parameter. Its default value is
**10 entries per page**, and the maximum number of entries per page is **100**.

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?page_size=5](/api/v1/rna/?page_size=5)
* [{{ BASE_URL }}/api/v1/rna/?page=2&page_size=5](/api/v1/rna/?page_size=5&page=2)

## Output formats <a style="cursor: pointer" id="v1-output-formats" ng-click="scrollTo('v1-output-formats')" name="v1-output-formats" class="text-muted smaller"><i class="fa fa-link"></i></a>

The following output formats are supported for all endpoints:
**JSON**, **JSONP** (for cross-origin Javascript requests), **YAML**, **HTML**.

In addition, the data for individual RNA sequences can be downloaded in **FASTA** format.

There are three ways of specifying the format:

1. `format` url parameter
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=json](/api/v1/rna/URS0000000001/?format=json)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=fasta](/api/v1/rna/URS0000000001/?format=fasta)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=yaml](/api/v1/rna/URS0000000001/?format=yaml)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001/?format=api](/api/v1/rna/URS0000000001/?format=api)

2. `.format` suffix
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.json](/api/v1/rna/URS0000000001.json)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.fasta](/api/v1/rna/URS0000000001.fasta)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.yaml](/api/v1/rna/URS0000000001.yaml)
  * [{{ BASE_URL }}/api/v1/rna/URS0000000001.api](/api/v1/rna/URS0000000001.api)

3. [Accept headers](http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html)

  ```
  curl -H "Accept: application/json" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: text/fasta" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: application/yaml" {{ BASE_URL }}/api/v1/rna/URS0000000001
  curl -H "Accept: text/html" {{ BASE_URL }}/api/v1/rna/URS0000000001
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
<p>
## Filtering <a style="cursor: pointer" id="v1-filtering" ng-click="scrollTo('v1-filtering')" name="v1-filtering" class="text-muted smaller"><i class="fa fa-link"></i></a>

The API supports several filtering operations that complement the main RNAcentral search functionality.

### Filtering by sequence length <a style="cursor: pointer" id="v1-filtering-by-sequence-length" ng-click="scrollTo('v1-filtering-by-sequence-length')" name="v1-filtering-by-sequence-length" class="text-muted smaller"><i class="fa fa-link"></i></a>

There are 3 url parameters: `length`, `min_length` (greater or equal length), and `max_length` (less or equal length).

#### Examples

* [{{ BASE_URL }}/api/v1/rna/?length=2014](/api/v1/rna/?length=2014)
* [{{ BASE_URL }}/api/v1/rna/?min_length=200000](/api/v1/rna/?min_length=200000)
* [{{ BASE_URL }}/api/v1/rna/?max_length=10](/api/v1/rna/?max_length=10)
* [{{ BASE_URL }}/api/v1/rna/?min_length=10&max_length=100](/api/v1/rna/?min_length=10&max_length=100)

### Filtering by external ids <a style="cursor: pointer" id="v1-filtering-by-external-ids" ng-click="scrollTo('v1-filtering-by-external-ids')" name="v1-filtering-by-external-ids" class="text-muted smaller"><i class="fa fa-link"></i></a>

The external id is an id assigned to a sequence in one of the Expert Databases,
which is imported into RNAcentral as a cross-reference.

The external id can be specified by setting the `external_id` url parameter.

#### Examples

* <a href="/api/v1/rna/?external_id=Stap.epid._AF269831" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=Stap.epid._AF269831</a> (SRPDB)
* <a href="/api/v1/rna/?external_id=MIMAT0000091" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=MIMAT0000091</a> (miRBase)
* <a href="/api/v1/rna/?external_id=OTTHUMG00000172092" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=OTTHUMG00000172092</a> (Vega)
* <a href="/api/v1/rna/?external_id=Lepto_inter_Lai566" target="_blank">{{ BASE_URL }}/api/v1/rna/?external_id=Lepto_inter_Lai566</a> (tmRNA Website)

### Combined filters <a style="cursor: pointer" id="v1-combined-filters" ng-click="scrollTo('v1-combined-filters')" name="v1-combined-filters" class="text-muted smaller"><i class="fa fa-link"></i></a>

Any filters can be combined to narrow down the query using the `&` symbol as a separator,
which acts as the logical `AND` operator. More logical operators will be supported in the future.

#### Example

* [{{ BASE_URL }}/api/v1/rna/?min_length=10&max_length=100](/api/v1/rna/?min_length=10&max_length=100)


## Genome annotations <a style="cursor: pointer" id="v1-genome-annotations" ng-click="scrollTo('v1-genome-annotations')" name="v1-genome-annotations" class="text-muted smaller"><i class="fa fa-link"></i></a>

The API provides an endpoint for retrieving annotations based on genomic coordinates for a [number of species](/help/genomic-mapping).

The response content is similar to that provided by the
[Ensembl REST API](http://rest.ensembl.org/documentation/info/overlap_region)
and can be directly used to visualise the data using the [Genoverse](http://genoverse.org) HTML5 genome browser.

The genome location should be in the `chromosome:start-end` format and may contain optional commas.

#### Examples

-[{{ BASE_URL }}/api/v1/overlap/region/homo_sapiens/2:39,745,816-39,826,679](/api/v1/overlap/region/homo_sapiens/2:39,745,816-39,826,679)

## Example script <a style="cursor: pointer" id="v1-example-script" ng-click="scrollTo('v1-example-script')" name="v1-example-script" class="text-muted smaller"><i class="fa fa-link"></i></a>

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
* md5 is computed for DNA sequences (so all Us should be replaced with Ts).

{# embedded GitHub gist #}
<script src="https://gist.github.com/rnacentralAdmin/b5aa714af3688e1eb49bc11d9ab032f8.js"></script>

## Cross domain requests <a style="cursor: pointer" id="v1-cross-domain-requests" ng-click="scrollTo('v1-cross-domain-requests')" name="v1-cross-domain-requests" class="text-muted smaller"><i class="fa fa-link"></i></a>

To use the API in a javascript application, please use jsonp requests.

#### Example using jQuery <a style="cursor: pointer" id="v1-example-using-jquery" ng-click="scrollTo('v1-example-using-jquery')" name="v1-example-using-jquery" class="text-muted smaller"><i class="fa fa-link"></i></a>


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


## Trailing slash <a style="cursor: pointer" id="v1-trailing-slash" ng-click="scrollTo('v1-trailing-slash')" name="v1-trailing-slash" class="text-muted smaller"><i class="fa fa-link"></i></a>

The trailing slash in all urls used in the API is **optional**.

#### Examples

These requests should return the same results, both in the browser and when retrieved programmatically:

* [{{ BASE_URL }}/api/v1](/api/v1)
* [{{ BASE_URL }}/api/v1/](/api/v1/)
<p>