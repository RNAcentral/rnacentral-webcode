
# <i class="fa fa-database"></i> Public Postgres database

<img src="https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg" class="img-responsive pull-left" style="width: 100px; margin-right: 20px;">

In addition to [downloadable files](/downloads), an [API](/api),
and the [text search](/search?q=RNA), RNAcentral provides a public
[Postgres](https://en.wikipedia.org/wiki/PostgreSQL) database that can be used
to query the data using SQL syntax. The database is updated with every RNAcentral release
and contains a copy of the data available through the [RNAcentral website](/).

## Connection details

- Hostname: `hh-pgsql-public.ebi.ac.uk`
- Port: `5432`
- Database: `pfmegrnargs`
- User: `reader`
- Password: `NWDMCE5xdipIjRrp`

## Connecting to the database

To connect to the database using **command line**:

  ```
  psql postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs
  ```

**Pro tip**: if you don't have `psql` installed on your machine, consider using [Docker](https://www.docker.com/) to get started with a pre-configured Postgres image:

  ```
  docker pull postgres
  docker run -it postgres psql postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs
  ```

Alternatively, you can use a **Postgres client** like [DBeaver](https://dbeaver.io) or [PgAdmin](https://pgadmin.org).

<i class="fa fa-warning"></i> If your computer is behind a firewall, please ensure that outgoing TCP/IP connections to the corresponding ports are allowed.

## Database Schema (as of release 11)

<a href="/static/img/rnacentral_release_11_schema.png">
  <img src="/static/img/rnacentral_release_11_schema.png" class="img-responsive">
</a>

## Main tables

The entire RNAcentral schema contains more than 40 tables, but the following tables
are good starting points for exploring the data:

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

The RNAcentral text search can only export up to 250,000 search results.
If you need to export more sequences, you can use the following workflow:

1. Create a file `query.sql`:

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
      AND rna_type = 'rRNA'
  ```

1. Run the following command to execute the query:

  ```
  docker run -v `pwd`:/rnacentral -it postgres /bin/sh -c 'cd /rnacentral && psql -t -A -f query.sql postgres://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs > ids.txt'  
  ```

  The command will create a file `ids.txt` with a list of RNAcentral identifiers.

1. Download the following RNAcentral FASTA file:

  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/rnacentral_species_specific_ids.fasta.gz]()

1. Extract the sequences using [seqkit](https://bioinf.shenwei.me/seqkit/):

  ```
  seqkit grep -f ids.txt rnacentral_species_specific_ids.fasta.gz > output.fasta
  ```

  The file `output.fasta` will contain the desired subset of RNAcentral sequences in FASTA format.

## Example Python script

Requires [psycopg2](http://initd.org/psycopg/) to connect to Postgres:

```
pip install psycopg2
```

<script src="https://gist.github.com/AntonPetrov/ec248312feff6acc07a82b4bfb595440.js"></script>

## Contributing to the RNAcentral website

The public Postgres database allows anyone to run the RNAcentral website locally
and contribute new code to RNAcentral using the instructions available on [GitHub](https://github.com/rnacentral/rnacentral-webcode).
