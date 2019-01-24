
# <i class="fa fa-search"></i> Text search

RNAcentral text search supports advanced queries using the following syntax:

### Exact matching <a style="cursor: pointer" id="exact-matching" ng-click="scrollTo('exact-matching')" name="exact-matching" class="text-muted smaller"><i class="fa fa-link"></i></a>

Use double quotes (**""**) to search for exact matches.

*Example*: `"hsa-mir-21"` will find only *hsa-mir-21* and not *hsa-mir-212*

---

### Wildcards <a style="cursor: pointer" id="wildcards" ng-click="scrollTo('wildcards')" name="wildcards" class="text-muted smaller"><i class="fa fa-link"></i></a>

A wildcard character (<strong>*</strong>) can match any number of characters. Wildcards are added automatically to all search terms that are not enclosed in double quotes.

*Example*: a search for `HOTAIR` (no double quotes) will find both *HOTAIR* and *HOTAIRM1* genes
and a search for `"HOTAIR"` (with double quotes) will find only *HOTAIR*.

---

### Field-specific search <a style="cursor: pointer" id="field-specific-search" ng-click="scrollTo('field-specific-search')" name="field-specific-search" class="text-muted smaller"><i class="fa fa-link"></i></a>

Search can be restricted to specific fields using the **field_name:"field value"** syntax.
Please note that "field value" **must be enclosed in double quotes**.

| Field                          | Examples                                                                                                                                           |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **expert database**            | `expert_db:"tmrna website"`, `expert_db:"mirbase"`, search for `RNA` and look at the "Expert databases" facet                                      |
| **NCBI taxonomic identifier**  | `taxonomy:"9606"` where [9606](http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=9606) is the NCBI taxonomy id for Homo sapiens           |
| **taxonomy string**            | `tax_string:"primates"` - allows to search for taxonomic group                                                                                                                            |
| **scientific species name**    | `species:"Mus musculus"`                                                                                                                           |
| **common species name**        | `common_name:"mouse"`                                                                                                                              |
| **RNA type**                   | `rna_type:"pirna"`, search for `RNA` and look at the "RNA types" facet.                                                                            |
| **gene**                       | `gene:"hotair"`                                                                                                                                    |
| **organelle**                  | `organelle:"mitochondrion"`, `organelle:"plastid"`                                                                                                 |
| **description**                | `description:"16S"`                                                                                                                                |
| **length**                     | `length:"1500"`, `length:[9000 to 10000]` (supports range queries)                                                                                 |
| **publication title**          | `pub_title:"Danish population"`                                                                                                                    |
| **author**                     | `author:"Girard A."`                                                                                                                               |
| **PubMed id**                  | `pubmed:"17881443"`                                                                                                                                |
| **Digital Object Identifier**  | `doi:"10.1093/nar/19.22.6328"`                                                                                                                     |
| **MD5**                        | `md5:"020711a90d35bb197e29e085595dd52e"` [MD5](http://en.wikipedia.org/wiki/MD5) hash value of uppercase DNA corresponding to RNAcentral sequence. |

---

### Logic operators <a style="cursor: pointer" id="logic-operators" ng-click="scrollTo('logic-operators')" name="logic-operators" class="text-muted smaller"><i class="fa fa-link"></i></a>

* **and** (default)

	Multiple search terms separated by white spaces are combined using AND,
	so a query like `Homo sapiens` is treated as `Homo AND sapiens` and only entries having both terms will be found.

* **or** (to indicate equivalence)

	*Example: `rna_type:"pirna" or rna_type:"mirna"`

* **not** (to indicate exclusion)

	*Example: `expert_db:"lncrnadb" not expert_db:"rfam"`.

---

### Grouping <a style="cursor: pointer" id="grouping" ng-click="scrollTo('grouping')" name="grouping" class="text-muted smaller"><i class="fa fa-link"></i></a>

Use parentheses to group and nest logical terms.

*Example*: `(expert_db:"mirbase" OR expert_db:"lncrnadb") NOT expert_db:"rfam"`

---

## Search tips <a style="cursor: pointer" id="tips" ng-click="scrollTo('tips')" name="tips" class="text-muted smaller"><i class="fa fa-link"></i></a>

* Make sure your **spelling** is correct.

    *Example*: misspelled terms like `Esherichia` (missing "c") won't find any results.

* Use **full species names**.

    *Example*: use `Escherichia coli` and not `E. coli` as your search terms.

---

## About RNAcentral search <a style="cursor: pointer" id="ebi-search" ng-click="scrollTo('ebi-search')" name="ebi-search" class="text-muted smaller"><i class="fa fa-link"></i></a>

RNAcentral is powered by the [EBI search](http://www.ebi.ac.uk/ebisearch/),
which provides a publicly available REST interface for querying the data.
