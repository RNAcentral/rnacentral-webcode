
# <i class="fa fa-database"></i> Public Postgres database

<img src="https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg" class="img-responsive pull-left" style="width: 100px; margin-right: 20px; margin-down: 5px;">

In addition to [downloadable files](/downloads), an [API](/api),
and the [text search](/search?q=RNA), RNAcentral provides a public
[Postgres](https://en.wikipedia.org/wiki/PostgreSQL) database that can be used
to query the data using SQL syntax. The database is updated every RNAcentral release
and contains a copy of the data available through the [RNAcentral website](/).

## Connection details

- Hostname: `pgsql-hhvm-001.ebi.ac.uk`
- Port: `5432`
- Database: `pfmegrnargs`
- User: `reader`
- Password: `NWDMCE5xdipIjRr`

To connect to the database using **command line**:

```
PGPASSWORD=NWDMCE5xdipIjRr psql -U reader 'postgresql://pgsql-hhvm-001.ebi.ac.uk:5432/pfmegrnargs'
```

**Pro tip**: if you don't have `psql` installed on your machine, consider using [Docker](https://www.docker.com/) to get started with a pre-configured Postgres image:

```
docker pull postgres
docker run -it postgres bash
psql
```

Alternatively, you can use a **Postgres client** like [DBeaver](https://dbeaver.io) or [PgAdmin](https://pgadmin.org).

<i class="fa fa-warning"></i> If your computer is behind a firewall, please ensure that outgoing TCP/IP connections to the corresponding ports are allowed.

## Main tables

- `rna` - contains RNA sequences and URS identifiers
- `xref` - contains cross-references to [Expert Databases](/expert-databases)
- `rnc_database` - contains a list of Expert Databases
- `rnc_accessions` - contains metadata associated with each cross-reference
- `rnc_rna_precomputed` - contains RNA types and descriptions for all sequences

## Example queries

### Search by external accessions

Although the VEGA database has been [archived](http://vega.archive.ensembl.org/info/website/archive.html) and its
identifiers are no longer searchable using the RNAcentral text search,
you can still query RNAcentral using VEGA identifiers:

```
SELECT
  upi,     -- RNAcentral URS identifier
  taxid,   -- NCBI taxid
  ac       -- external accession
FROM xref
WHERE ac IN ('OTTHUMT00000106564.1', 'OTTHUMT00000416802.1')
```

Example output:

```
URS00000B15DA	9606	OTTHUMT00000106564.1
URS00000A54A6	9606	OTTHUMT00000416802.1
```

## Example workflow to extract all bacterial rRNA sequences

The RNAcentral text search can only export up to 250,000 entries after the search is complete.
When you need to export more sequences, we suggest the following workflow:

1. Get RNAcentral identifiers

  ```
  SELECT
      precomputed.id
  FROM rnc_rna_precomputed precomputed
  JOIN rnc_taxonomy tax
  ON
      tax.id = precomputed.taxid
  WHERE
      tax.lineage LIKE 'cellular organisms; Bacteria; %'
      AND precomputed.is_active = true    -- exclude sequences without active cross-references
  LIMIT 100
  ```

  Example output:
  ```
  URS00000A753F_1158518
  URS00003D4707_243274
  URS00003D470D_261292
  ```

2. Extract the identifiers from the RNAcentral FASTA file:

  [seqkit](https://bioinf.shenwei.me/seqkit/)

  ```
  psql -f query.sql $DATABASE > ids
  esl-sfetch --index rnacentral.fasta
  esl-sfetch -f rnacentral.fasta ids > found.fasta
  seqkit grep --pattern-file id.txt duplicated-reads.fq.gz > duplicated-reads.subset.fq.gz
  ```

## Example Python script

Requires [psycopg2](http://initd.org/psycopg/) to connect to Postgres:

```
pip install psycopg2
```

<embed>


## Contributing to the RNAcentral website

The public Postgres database allows anyone to run the RNAcentral website locally
and contribute new code to RNAcentral using the instructions available on [GitHub](https://github.com/rnacentral/rnacentral-webcode).
