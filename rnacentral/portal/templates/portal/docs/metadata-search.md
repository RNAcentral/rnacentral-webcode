
<h1><i class="fa fa-info-circle"></i> Metadata search</h1>

## Query syntax

### Wildcards

The wildcard character (`*`) can match any number of characters.

**Wildcards are added automatically** to all search terms that are not part of field-specific
search and that are not enclosed in double quotes (see below).

*Example*: a search for `HOTAIR` (no double quotes) will find both HOTAIR and HOTAIRM1 genes
and a search for `"HOTAIR"` (with double quotes) will find only HOTAIR.

---

### Exact matching

Use double quotes (`""`) to search for exact matches.

*Example*: `"precursor RNA"`

---

### Field-specific search

Search can be restricted to specific fields using the `field_name:"field value"` syntax.
Please note that `"field value"` must be enclosed in double quotes.

* **expert database**

	Possible values: "ena", "gtrnadb", "lncrnadb", "mirbase", "refseq", "rfam", "srpdb", "tmRNA Website", "vega"

	*Examples*: `expert_db:"tmrna website"`, `expert_db:"mirbase"`

* **gene**

	*Example*: `gene:"hotair"`

* **organelle**

	*Example*: `organelle:"mitochondrion"`

* **RNA type**

	To see the list of possible values, search for `RNA` and look at the "RNA types" facet.

	*Example*: `rna_type:"pirna"`.

* **description**

	*Example*: `description:"16S"`

* **length**

	*Example*: `length:"1500"`

* **scientific species name**

	*Example*: `species:"Mus musculus"`

* **common species name**

	*Example*: `common_name:"mouse"`

* **NCBI taxonomic identifier**

	*Example*: `TAXONOMY:"9606"` where [9606](http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=9606) is the NCBI taxonomy id for Homo sapiens.

---

### Logic operators

* **and** (default)

	Multiple search terms separated by white spaces are combined using `AND`,
	so a query like `Homo sapiens` is treated as `Homo AND sapiens` and only entries having both terms will be found.

* **or** (to indicate equivalence)

	*Example: `rna_type:"pirna" or rna_type:"mirna"`

* **not** (to indicate exclusion)

	*Example: `expert_db:"lncrnadb" not expert_db:"rfam"`.

---

### Grouping

Use parentheses to group and nest logical terms.

*Example*: `(expert_db:"mirbase" OR expert_db:"lncrnadb") NOT expert_db:"rfam"`

---

## Search tips

* Make sure your **spelling** is correct.

    *Example*: misspelled terms like `Esherichia` (missing "c") won't find any results.

* Use **full species names**.

    *Example*: use `Escherichia coli` and not `E. coli` as your search terms.

---

## About RNAcentral search

RNAcentral is powered by the [EBI search](http://www.ebi.ac.uk/ebisearch/),
which provides publicly available REST and SOAP interfaces for querying the data.
