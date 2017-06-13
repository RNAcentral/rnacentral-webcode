
# <i class="fa fa-search"></i> Text search

### Exact matching <a name="exact-matching" href="#exact-matching" class="text-muted smaller"><i class="fa fa-link"></i></a>

Use double quotes (**""**) to search for exact matches.

*Example*: `"hsa-mir-21"` will find only *hsa-mir-21* and not *hsa-mir-212*

---

### Wildcards <a name="wildcards" href="#wildcards" class="text-muted smaller"><i class="fa fa-link"></i></a>

A wildcard character (<strong>*</strong>) can match any number of characters. Wildcards are added automatically to all search terms that are not enclosed in double quotes.

*Example*: a search for `HOTAIR` (no double quotes) will find both *HOTAIR* and *HOTAIRM1* genes
and a search for `"HOTAIR"` (with double quotes) will find only *HOTAIR*.

---

### Field-specific search <a name="field-specific-search" href="#field-specific-search" class="text-muted smaller"><i class="fa fa-link"></i></a>

Search can be restricted to specific fields using the **field_name:"field value"** syntax.
Please note that "field value" **must be enclosed in double quotes**.

* **expert database**

	Possible values: "ena", "gtrnadb", "lncrnadb", "mirbase", "refseq", "rfam", "srpdb", "tmRNA Website", "vega", "pdbe", "snopy" and other imported database names.

	*Examples*: `expert_db:"tmrna website"`, `expert_db:"mirbase"`

* **NCBI taxonomic identifier**

	*Example*: `taxonomy:"9606"` where [9606](http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=9606) is the NCBI taxonomy id for Homo sapiens.

* **scientific species name**

	*Example*: `species:"Mus musculus"`

* **common species name**

	*Example*: `common_name:"mouse"`

* **RNA type**

	To see the list of possible values, search for `RNA` and look at the "RNA types" facet.

	*Example*: `rna_type:"pirna"`.

* **gene**

	*Example*: `gene:"hotair"`

* **organelle**

	*Example*: `organelle:"mitochondrion"`, `organelle:"plastid"`

* **description**

	*Example*: `description:"16S"`

* **length** (supports range queries)

	*Example*: `length:"1500"`, `length:[9000 to 10000]`

* **publication title**

  *Example*: `pub_title:"Danish population"`

* **author**

	*Example*: `author:"Girard A."`

* **PubMed id**

	*Example*: `pubmed:"17881443"`

* **Digital Object Identifier**

	*Example*: `doi:"10.1093/nar/19.22.6328"`

* **MD5**

	Use [MD5](http://en.wikipedia.org/wiki/MD5) hash value of the uppercase DNA version of the sequence
	to lookup the associated RNAcentral id.

	*Example*: `md5:"020711a90d35bb197e29e085595dd52e"`

---

### Logic operators <a name="logic-operators" href="#logic-operators" class="text-muted smaller"><i class="fa fa-link"></i></a>

* **and** (default)

	Multiple search terms separated by white spaces are combined using AND,
	so a query like `Homo sapiens` is treated as `Homo AND sapiens` and only entries having both terms will be found.

* **or** (to indicate equivalence)

	*Example: `rna_type:"pirna" or rna_type:"mirna"`

* **not** (to indicate exclusion)

	*Example: `expert_db:"lncrnadb" not expert_db:"rfam"`.

---

### Grouping <a name="grouping" href="#grouping" class="text-muted smaller"><i class="fa fa-link"></i></a>

Use parentheses to group and nest logical terms.

*Example*: `(expert_db:"mirbase" OR expert_db:"lncrnadb") NOT expert_db:"rfam"`

---

## Search tips <a name="tips" href="#tips" class="text-muted smaller"><i class="fa fa-link"></i></a>

* Make sure your **spelling** is correct.

    *Example*: misspelled terms like `Esherichia` (missing "c") won't find any results.

* Use **full species names**.

    *Example*: use `Escherichia coli` and not `E. coli` as your search terms.

---

## About RNAcentral search <a name="ebi-search" href="#ebi-search" class="text-muted smaller"><i class="fa fa-link"></i></a>

RNAcentral is powered by the [EBI search](http://www.ebi.ac.uk/ebisearch/),
which provides a publicly available REST interface for querying the data.
