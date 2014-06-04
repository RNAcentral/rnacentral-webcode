
<h1><i class="fa fa-info-circle"></i> Metadata search</h1>

## Query syntax

### Field-specific search

By default all fields are searched against a query, but search can also be restricted to specific fields such as:

* **expert database**

	Possible values: ena, rfam, mirbase, vega, gtrnadb, srpdb, "tmRNA Website"

	*Examples*: `expert_db:"tmrna website"`, `expert_db:mirbase`

* **gene**

	*Example*: `gene:hotair`

* **organelle**

	*Example*: `organelle:mitochondrion`

* **RNA type**

	To see the list of possible values, search for `RNA` and look at the "RNA types" facet.

	*Example*: `rna_type:pirna`.

* **description**

	*Example*: `description:16S`

* **length**

	*Example*: `length:1500`

* **scientific species name**

	*Example*: `species:"Mus musculus"`

* **common species name**

	*Example*: `common_name:mouse`

* **NCBI taxonomic identifier**

	*Example*: `TAXONOMY:"9606"` where [9606](http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=9606) is the NCBI taxonomy id for Homo sapiens.

---

### Logic operators

* **and** (default)

	Multiple search terms separated by white spaces are combined using `AND`,
	so a query like`Homo sapiens` is treated as `Homo AND sapiens` and only entries having both terms will be found.

* **or** (to indicate equivalence)

	*Example: `rna_type:pirna or rna_type:mirna`

* **not** (to indicate exclusion)

	*Example: `expert_db:lncrnadb not expert_db:rfam`.

---

### Wildcard

The `*` character can match any number of characters.

*Example*: a search for `1*S` will find both 18S and 16S rRNAs.

---

### Exact match

Use double quotes (`""`) to search for exact matches.

*Example*: `"precursor RNA"`

---

### Grouping

Use parentheses to group and nest logical terms.

*Example*: `(expert_db:mirbase OR expert_db:lncrnadb) NOT expert_db:mirbase`

---

## Search tips

* Use **full species names**.

    *Example*: use `Escherichia coli` and not `E. coli` as your search terms.

* Make sure your **spelling** is correct.

    *Example*: misspelled terms like `Esherichia` (missing "c") will find no results.

* Try relaxing your query by adding **wildcards** (*) to one or more of your search terms

	*Example*: a search for `Escherichia*` will find all Escherichia species.
