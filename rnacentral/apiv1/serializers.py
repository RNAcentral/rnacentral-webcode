"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import re

import requests
from django.core.paginator import Paginator
from django.db.models import Max, Min
from django.urls import reverse
from portal.models import (
    Accession,
    ChemicalComponent,
    DatabaseStats,
    EnsemblAssembly,
    EnsemblCompara,
    EnsemblKaryotype,
    Modification,
    OntologyTerm,
    ProteinInfo,
    QcStatus,
    Reference,
    Reference_map,
    RfamClan,
    RfamHit,
    RfamModel,
    Rna,
    RnaPrecomputed,
    SecondaryStructureWithLayout,
    SequenceFeature,
    Xref,
)
from rest_framework import serializers


class RawPublicationSerializer(serializers.ModelSerializer):
    """Serializer class for literature citations. Used in conjunction with raw querysets."""

    authors = serializers.ListField(serializers.CharField(), source="get_authors_list")
    publication = serializers.CharField(source="location")
    pubmed_id = serializers.CharField(source="pubmed")
    doi = serializers.CharField()
    title = serializers.CharField(source="get_title")
    pub_id = serializers.CharField(source="id")
    expert_db = serializers.BooleanField()

    class Meta:
        model = Reference
        fields = (
            "title",
            "authors",
            "publication",
            "pubmed_id",
            "doi",
            "pub_id",
            "expert_db",
        )


class CitationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for literature citations."""

    authors = serializers.ListField(
        serializers.CharField(), source="data.get_authors_list"
    )
    publication = serializers.CharField(source="data.location")
    pubmed_id = serializers.CharField(source="data.pubmed")
    doi = serializers.CharField(source="data.doi")
    title = serializers.ReadOnlyField(source="data.get_title")
    pub_id = serializers.ReadOnlyField(source="data.id")

    class Meta:
        model = Reference_map
        fields = ("title", "authors", "publication", "pubmed_id", "doi", "pub_id")


class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for individual cross-references."""

    id = serializers.CharField(source="accession")
    citations = serializers.HyperlinkedIdentityField(view_name="accession-citations")
    expert_db_url = serializers.ReadOnlyField(source="get_expert_db_external_url")

    # database-specific fields
    pdb_entity_id = serializers.ReadOnlyField(source="get_pdb_entity_id")
    pdb_structured_note = serializers.ReadOnlyField(source="get_pdb_structured_note")
    hgnc_enembl_id = serializers.ReadOnlyField(source="get_hgnc_ensembl_id")
    hgnc_id = serializers.ReadOnlyField(source="get_hgnc_id")
    biotype = serializers.ReadOnlyField(source="get_biotype")
    rna_type = serializers.ReadOnlyField(source="get_rna_type")
    srpdb_id = serializers.ReadOnlyField(source="get_srpdb_id")
    ena_url = serializers.ReadOnlyField(source="get_ena_url")
    ensembl_species_url = serializers.ReadOnlyField(source="get_ensembl_species_url")
    malacards_diseases = serializers.ReadOnlyField(source="get_malacards_diseases")

    class Meta:
        model = Accession
        fields = (
            "url",
            "id",
            "parent_ac",
            "seq_version",
            "feature_start",
            "feature_end",
            "feature_name",
            "description",
            "external_id",
            "optional_id",
            "locus_tag",
            "species",
            "inference",
            "rna_type",
            "gene",
            "product",
            "organelle",
            "citations",
            "expert_db_url",
            "standard_name",
            "pdb_entity_id",
            "pdb_structured_note",
            "hgnc_enembl_id",
            "hgnc_id",
            "biotype",
            "rna_type",
            "srpdb_id",
            "ena_url",
            "ensembl_species_url",
            "malacards_diseases",
        )


class ChemicalComponentSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for chemical components."""

    id = serializers.CharField()
    description = serializers.CharField()
    one_letter_code = serializers.CharField()
    ccd_id = serializers.CharField()
    source = serializers.CharField()
    modomics_short_name = serializers.CharField()
    pdb_url = serializers.ReadOnlyField(source="get_pdb_url")
    modomics_url = serializers.ReadOnlyField(source="get_modomics_url")

    class Meta:
        model = ChemicalComponent
        fields = (
            "id",
            "description",
            "one_letter_code",
            "ccd_id",
            "source",
            "modomics_short_name",
            "pdb_url",
            "modomics_url",
        )


class ModificationSerializer(serializers.ModelSerializer):
    """Django Rest Framework serializer class for modified positions."""

    position = serializers.IntegerField()
    author_assigned_position = serializers.IntegerField()
    chem_comp = ChemicalComponentSerializer(source="modification_id")

    class Meta:
        model = Modification
        fields = ("position", "author_assigned_position", "chem_comp")


class XrefSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for all cross-references associated with an RNAcentral id."""

    database = serializers.CharField(source="db.display_name")
    is_active = serializers.BooleanField(read_only=True)
    first_seen = serializers.CharField(source="created.release_date")
    last_seen = serializers.CharField(source="last.release_date")
    accession = AccessionSerializer()

    # database-specific fields
    modifications = ModificationSerializer(many=True)
    is_rfam_seed = serializers.BooleanField(read_only=True)
    ncbi_gene_id = serializers.CharField(source="get_ncbi_gene_id", read_only=True)
    ndb_external_url = serializers.URLField(
        source="get_ndb_external_url", read_only=True
    )
    mirbase_mature_products = serializers.SerializerMethodField()
    mirbase_precursor = serializers.SerializerMethodField()
    refseq_mirna_mature_products = serializers.SerializerMethodField()
    refseq_mirna_precursor = serializers.SerializerMethodField()
    refseq_splice_variants = serializers.SerializerMethodField()
    ensembl_splice_variants = serializers.SerializerMethodField()
    # tmrna_mate_upi = serializers.SerializerMethodField('get_tmrna_mate_upi')
    # tmrna_type = serializers.ReadOnlyField(source='get_tmrna_type')
    gencode_transcript_id = serializers.CharField(
        source="get_gencode_transcript_id", read_only=True
    )
    gencode_ensembl_url = serializers.CharField(
        source="get_gencode_ensembl_url", read_only=True
    )
    ensembl_url = serializers.SerializerMethodField("get_ensembl_url")

    class Meta:
        model = Xref
        fields = (
            "database",
            "is_active",
            "first_seen",
            "last_seen",
            "taxid",
            "accession",
            "modifications",  # used to send ~100 queries, optimized to 1
            "is_rfam_seed",
            "ncbi_gene_id",
            "ndb_external_url",
            "mirbase_mature_products",
            "mirbase_precursor",
            "refseq_mirna_mature_products",
            "refseq_mirna_precursor",
            "refseq_splice_variants",
            "ensembl_splice_variants",
            # 'tmrna_mate_upi',
            # 'tmrna_type',
            "gencode_transcript_id",
            "gencode_ensembl_url",
            "ensembl_url",
        )

    def upis_to_urls(self, upis):
        """
        Returns a list of urls or single url that points to unique rna sequence
        page, corresponding to given upi.

        :param upis: list of upis or a single upi
        :return: list of urls or a single url
        """
        protocol = "https://" if self.context["request"].is_secure() else "http://"
        hostport = self.context["request"].get_host()
        if isinstance(upis, list):
            return [
                protocol
                + hostport
                + reverse("unique-rna-sequence", kwargs={"upi": upi})
                for upi in upis
            ]
        else:  # upis is just a single item
            return (
                protocol
                + hostport
                + reverse("unique-rna-sequence", kwargs={"upi": upis})
            )

    def get_mirbase_mature_products(self, obj):
        return (
            self.upis_to_urls(obj.mirbase_mature_products)
            if hasattr(obj, "mirbase_mature_products")
            else None
        )

    def get_mirbase_precursor(self, obj):
        return (
            self.upis_to_urls(obj.mirbase_precursor)
            if hasattr(obj, "mirbase_precursor")
            else None
        )

    def get_refseq_mirna_mature_products(self, obj):
        return (
            self.upis_to_urls(obj.refseq_mirna_mature_products)
            if hasattr(obj, "refseq_mirna_mature_products")
            else None
        )

    def get_refseq_mirna_precursor(self, obj):
        return (
            self.upis_to_urls(obj.refseq_mirna_precursor)
            if hasattr(obj, "refseq_mirna_precursor")
            else None
        )

    def get_refseq_splice_variants(self, obj):
        return (
            self.upis_to_urls(obj.refseq_splice_variants)
            if hasattr(obj, "refseq_splice_variants")
            else None
        )

    def get_ensembl_splice_variants(self, obj):
        return (
            self.upis_to_urls(obj.ensembl_splice_variants)
            if hasattr(obj, "ensembl_splice_variants")
            else None
        )

    def get_tmrna_mate_upi(self, obj):
        return (
            self.upis_to_urls(obj.tmrna_mate_upi)
            if hasattr(obj, "tmrna_mate_upi")
            else None
        )

    def get_genomic_coordinates(self, obj):
        # In Django1.9+ we could try removing obj.accession.coordinates.exists() check and
        # replace obj.accession.coordinates.all()[0] with obj.accession.coordinates.first(),
        # but currently this prevents re-use of related queryset and created N+1 requests:
        #
        #  first_coordinate = obj.accession.coordinates.all().first()
        #  if first_coordinate:
        #      data = {
        #          'chromosome': first_coordinate.chromosome,
        #          'strand': first_coordinate.strand
        #      }
        #      return data

        # TODO: bring back all() -> filter(chromosome__isnull=False), when postgres is fully populated

        if (
            obj.accession.coordinates.exists()
            and obj.accession.coordinates.all()[0].chromosome
        ):
            data = {
                "chromosome": obj.accession.coordinates.all()[0].chromosome,
                "strand": obj.accession.coordinates.all()[0].strand,
                "start": obj.accession.coordinates.all().aggregate(
                    Min("primary_start")
                )["primary_start__min"],
                "end": obj.accession.coordinates.all().aggregate(Max("primary_end"))[
                    "primary_end__max"
                ],
            }

            exceptions = ["X", "Y"]
            if re.match(r"\d+", data["chromosome"]) or data["chromosome"] in exceptions:
                data["ucsc_chromosome"] = "chr" + data["chromosome"]
            else:
                data["ucsc_chromosome"] = data["chromosome"]
            return data

    def get_ensembl_url(self, obj):
        """Return the correct ensembl domain"""
        if obj.accession.database == "ENSEMBL_FUNGI":
            return "http://fungi.ensembl.org"
        elif obj.accession.database == "ENSEMBL_METAZOA":
            return "http://metazoa.ensembl.org"
        elif obj.accession.database == "ENSEMBL_PLANTS":
            return "http://plants.ensembl.org"
        elif obj.accession.database == "ENSEMBL_PROTISTS":
            return "http://protists.ensembl.org"
        else:
            return None


class RnaNestedSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer class for a unique RNAcentral sequence."""

    sequence = serializers.CharField(source="get_sequence", read_only=True)
    xrefs = serializers.HyperlinkedIdentityField(view_name="rna-xrefs")
    publications = serializers.HyperlinkedIdentityField(view_name="rna-publications")
    rnacentral_id = serializers.CharField(source="upi")
    is_active = serializers.BooleanField(read_only=True)
    description = serializers.CharField(source="get_description", read_only=True)
    rna_type = serializers.CharField(source="get_rna_type", read_only=True)
    count_distinct_organisms = serializers.IntegerField(read_only=True)
    distinct_databases = serializers.ReadOnlyField(source="get_distinct_database_names")

    class Meta:
        model = Rna
        fields = (
            "url",
            "rnacentral_id",
            "md5",
            "sequence",
            "length",
            "xrefs",
            "publications",
            "is_active",
            "description",
            "rna_type",
            "count_distinct_organisms",
            "distinct_databases",
        )


class RnaSecondaryStructureSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for presenting RNA secondary structures"""

    data = serializers.SerializerMethodField("get_secondary_structures")

    class Meta:
        model = Rna
        fields = ("data",)

    def get_secondary_structures(self, obj):
        """Return secondary structures filtered by taxid."""
        return obj.get_layout_secondary()


class SecondaryStructureSVGImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryStructureWithLayout
        fields = ("layout",)


class RnaSpeciesSpecificSerializer(serializers.Serializer):
    """
    Serializer class for species-specific RNAcentral ids.

    Requires context['xrefs'] and context['taxid'].
    """

    rnacentral_id = serializers.ReadOnlyField(source="id")
    sequence = serializers.ReadOnlyField(source="upi.get_sequence")
    length = serializers.ReadOnlyField(source="upi.length")
    description = serializers.ReadOnlyField()
    short_description = serializers.ReadOnlyField()
    species = serializers.SerializerMethodField()
    taxid = serializers.SerializerMethodField()
    genes = serializers.SerializerMethodField()
    rna_type = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    distinct_databases = serializers.ReadOnlyField(source="databases")

    def get_genes(self, obj):
        """Get a species-specific list of genes associated with the sequence in this particular sequence."""
        return self.context["gene"]

    def get_species(self, obj):
        """Get the name of the species based on taxid."""
        return self.context["species"]

    def get_taxid(self, obj):
        return int(self.context["taxid"])


class RnaFlatSerializer(RnaNestedSerializer):
    """Override the xrefs field in the default nested serializer to provide a flat representation."""

    xrefs = serializers.SerializerMethodField("paginated_xrefs")

    def paginated_xrefs(self, obj):
        """Include paginated xrefs."""
        queryset = obj.xrefs.all()
        page = self.context.get("page", 1)
        page_size = self.context.get("page_size", 100)
        paginator = Paginator(queryset, page_size)
        xrefs = paginator.page(page)

        serializer = XrefSerializer(xrefs, many=True, context=self.context)

        return serializer.data

    class Meta:
        model = Rna
        fields = (
            "url",
            "rnacentral_id",
            "md5",
            "sequence",
            "length",
            "xrefs",
            "publications",
            "is_active",
            "description",
            "rna_type",
            "count_distinct_organisms",
            "distinct_databases",
        )


class RnaFastaSerializer(serializers.ModelSerializer):
    """Serializer for presenting RNA sequences in FASTA format"""

    fasta = serializers.CharField(source="get_sequence_fasta", read_only=True)

    class Meta:
        model = Rna
        fields = ("fasta",)


class ProteinTargetsSerializer(serializers.ModelSerializer):
    target_accession = (
        serializers.CharField()
    )  # use non-null target_accession instead of nullable protein_accession
    source_accession = serializers.CharField()
    methods = serializers.ListField(serializers.CharField())

    class Meta:
        model = ProteinInfo
        fields = (
            "target_accession",
            "source_accession",
            "description",
            "label",
            "synonyms",
            "methods",
        )


class LncrnaTargetsSerializer(serializers.ModelSerializer):
    target_accession = serializers.CharField()
    source_accession = serializers.CharField()
    target_urs_taxid = serializers.CharField()
    methods = serializers.ListField(serializers.CharField())
    description = serializers.SerializerMethodField("select_description")

    def select_description(self, obj):
        if hasattr(obj, "target_rna_description"):
            return obj.target_rna_description
        elif hasattr(obj, "target_ensembl_description"):
            return obj.target_ensembl_description
        else:
            return ""

    class Meta:
        model = ProteinInfo
        fields = (
            "target_accession",
            "source_accession",
            "description",
            "label",
            "synonyms",
            "methods",
            "description",
            "target_urs_taxid",
        )


class ExpertDatabaseStatsSerializer(serializers.ModelSerializer):
    """Serializer for presenting DatabaseStats"""

    length_counts = serializers.SerializerMethodField()
    taxonomic_lineage = serializers.SerializerMethodField()

    class Meta:
        model = DatabaseStats
        fields = ("database", "length_counts", "taxonomic_lineage")

    def get_length_counts(self, obj):
        return json.loads(obj.length_counts)

    def get_taxonomic_lineage(self, obj):
        return json.loads(obj.taxonomic_lineage)


class OntologyTermSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)
    quickgo_url = serializers.CharField(read_only=True)

    class Meta:
        model = OntologyTerm
        fields = (
            "ontology_term_id",
            "ontology",
            "name",
            "definition",
            "url",
            "quickgo_url",
        )


class RfamClanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RfamClan
        fields = ("rfam_clan_id", "name", "description", "family_count")


class RfamModelSerializer(serializers.ModelSerializer):
    rfam_clan = RfamClanSerializer(source="rfam_clan_id")
    go_terms = OntologyTermSerializer(many=True)

    class Meta:
        model = RfamModel
        fields = (
            "rfam_model_id",
            "short_name",
            "long_name",
            "description",
            "rfam_clan",
            "seed_count",
            "full_count",
            "length",
            "is_suppressed",
            "domain",
            "rna_type",
            "rfam_rna_type",
            "thumbnail_url",
            "url",
            "go_terms",
        )


class RfamHitSerializer(serializers.ModelSerializer):
    rfam_model = RfamModelSerializer()

    class Meta:
        model = RfamHit
        fields = (
            "sequence_start",
            "sequence_stop",
            "sequence_completeness",
            "rfam_model",
        )


class SequenceFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceFeature
        fields = "__all__"


class EnsemblAssemblySerializer(serializers.ModelSerializer):
    human_readable_ensembl_url = serializers.SerializerMethodField()
    example_chromosome = serializers.SerializerMethodField()
    example_start = serializers.SerializerMethodField()
    example_end = serializers.SerializerMethodField()

    class Meta:
        model = EnsemblAssembly
        fields = (
            "assembly_id",
            "assembly_full_name",
            "gca_accession",
            "assembly_ucsc",
            "common_name",
            "taxid",
            "ensembl_url",
            "human_readable_ensembl_url",
            "division",
            "subdomain",
            "example_chromosome",
            "example_start",
            "example_end",
        )

    def get_human_readable_ensembl_url(self, obj):
        return obj.ensembl_url.replace("_", " ").capitalize()

    def get_example_chromosome(self, obj):
        return obj.example_chromosome

    def get_example_start(self, obj):
        return obj.example_start

    def get_example_end(self, obj):
        return obj.example_end


class EnsemblKaryotypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnsemblKaryotype
        fields = ("karyotype",)


class RnaPrecomputedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RnaPrecomputed
        fields = ("id", "rna_type", "description", "databases")


class EnsemblComparaSerializer(serializers.ModelSerializer):
    rnacentral_id = RnaPrecomputedSerializer(source="urs_taxid")

    class Meta:
        model = EnsemblCompara
        fields = ("ensembl_transcript_id", "rnacentral_id")


class RnaPrecomputedJsonSerializer(serializers.ModelSerializer):
    """Serializer class for the Json download."""

    sequence = serializers.CharField(source="get_sequence", read_only=True)
    databases = serializers.SerializerMethodField()

    class Meta:
        model = RnaPrecomputed
        fields = ("id", "rna_type", "description", "databases", "sequence")

    def get_databases(self, obj):
        return (
            [database for database in obj.databases.split(",")] if obj.databases else []
        )


class QcStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = QcStatus
        fields = "__all__"


class InteractionsSerializer(serializers.Serializer):
    """Serializer class for interactions"""

    urs_taxid = serializers.PrimaryKeyRelatedField(read_only=True)
    interacting_id = serializers.SerializerMethodField(method_name="get_interacting_id")
    interacting_id_url = serializers.SerializerMethodField(
        method_name="get_interacting_id_url"
    )
    hgnc = serializers.SerializerMethodField(method_name="get_hgnc")
    source = serializers.SerializerMethodField(method_name="get_source")

    def get_interacting_id(self, obj):
        if "intact:" in obj.interacting_id:
            match_urs = [item for item in obj.names if item.lower().startswith("urs")]
            match_ensembl = [
                item for item in obj.names if item.lower().startswith("ens")
            ]

            if match_ensembl:
                interacting_id = f"IntAct: {match_ensembl[0]}"
            elif match_urs:
                interacting_id = f"IntAct: {match_urs[0]}"
            else:
                interacting_id = obj.interacting_id.replace("intact:", "IntAct: ")
        elif "uniprotkb" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("uniprotkb:", "UniProt: ")
        elif "chebi" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("chebi:", "ChEBI: ")
        elif "complex portal" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace(
                "complex portal:", "Complex Portal: "
            )
        elif "ddbj/embl/genbank" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace(
                "ddbj/embl/genbank:", "DDBJ/EMBL/GenBank: "
            )
        elif "ensembl" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("ensembl:", "Ensembl: ")
        elif "flybase" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("flybase:", "FlyBase: ")
        elif "intenz" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("intenz:", "IntEnz: ")
        elif "reactome" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("reactome:", "Reactome: ")
        elif "sgd" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("sgd:", "SGD: ")
        elif "signor" in obj.interacting_id:
            interacting_id = obj.interacting_id.replace("signor:", "SIGNOR: ")
        else:
            interacting_id = obj.interacting_id.replace(":", ": ")

        return interacting_id

    def get_interacting_id_url(self, obj):
        if "intact:" in obj.interacting_id:
            match_urs = [item for item in obj.names if item.lower().startswith("urs")]
            match_ensembl = [
                item for item in obj.names if item.lower().startswith("ens")
            ]

            if match_ensembl:
                interacting_id = match_ensembl[0]
                ens_type = "Gene" if "ENSG" in interacting_id else "Transcript"
                try:
                    response = requests.get(
                        f"https://rest.ensembl.org/lookup/id/{interacting_id.split('.')[0]}?expand=1;content-type=application/json"
                    )
                    data = json.loads(response.text)
                    species = data["species"]
                    url = f"https://ensembl.org/{species}/{ens_type}/Summary?db=core;t={interacting_id}"
                except Exception:
                    url = ""
            elif match_urs:
                url = f"/rna/{match_urs[0]}"
            else:
                intact_id = obj.intact_id
                url = f"https://www.ebi.ac.uk/intact/details/interaction/{intact_id}"
        elif "uniprotkb:" in obj.interacting_id:
            uniprot_id = obj.interacting_id.replace("uniprotkb:", "")
            url = f"https://www.uniprot.org/uniprot/{uniprot_id}"
        elif "chebi" in obj.interacting_id:
            chebi_id = obj.interacting_id.replace("chebi:", "")
            url = f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:{chebi_id}"
        elif "complex portal" in obj.interacting_id:
            complex_portal_id = obj.interacting_id.replace("complex portal:", "")
            url = f"https://www.ebi.ac.uk/complexportal/complex/{complex_portal_id}"
        elif "ddbj/embl/genbank:" in obj.interacting_id:
            genbank_id = obj.interacting_id.replace("ddbj/embl/genbank:", "")
            url = f"https://www.ncbi.nlm.nih.gov/nuccore/{genbank_id}"
        elif "ensembl" in obj.interacting_id:
            ensembl_id = obj.interacting_id.replace("ensembl:", "")
            ens_type = "Gene" if "ENSG" in ensembl_id else "Transcript"
            try:
                response = requests.get(
                    f"https://rest.ensembl.org/lookup/id/{ensembl_id.split('.')[0]}?expand=1;content-type=application/json"
                )
                data = json.loads(response.text)
                species = data["species"]
                url = f"https://ensembl.org/{species}/{ens_type}/Summary?db=core;t={ensembl_id}"
            except Exception:
                url = ""
        elif "flybase:" in obj.interacting_id:
            flybase_id = obj.interacting_id.replace("flybase:", "")
            url = f"https://flybase.org/reports/{flybase_id}.html"
        elif "intenz" in obj.interacting_id:
            intenz_id = obj.interacting_id.replace("intenz:", "")
            url = f"https://www.ebi.ac.uk/intenz/query?q={intenz_id}"
        elif "mgd/mgi:" in obj.interacting_id:
            urs = obj.intact_id.split("-")[0]
            url = f"/rna/{urs}"
        elif "protein ontology:" in obj.interacting_id:
            uniprot_id = obj.interacting_id.replace("protein ontology:", "")
            url = f"https://www.uniprot.org/uniprot/{uniprot_id}"
        elif "reactome:" in obj.interacting_id:
            reactome_id = obj.interacting_id.replace("reactome:", "")
            url = f"https://reactome.org/content/detail/{reactome_id}"
        elif "RNAcentral:" in obj.interacting_id:
            urs = obj.interacting_id.replace("RNAcentral:", "")
            url = f"/rna/{urs}"
        elif "sgd:" in obj.interacting_id:
            sgd_id = obj.interacting_id.replace("sgd:", "")
            url = f"https://www.yeastgenome.org/locus/{sgd_id}"
        elif "signor:" in obj.interacting_id:
            signor_id = obj.interacting_id.replace("signor:", "")
            url = f"https://signor.uniroma2.it/relation_result.php?id={signor_id}"
        else:
            url = None

        return url

    def get_hgnc(self, obj):
        e_transcript = [item for item in obj.names if item.lower().startswith("ens")]

        if (
            "uniprotkb:" in obj.interacting_id
            or "protein ontology:" in obj.interacting_id
        ):
            if "uniprotkb:" in obj.interacting_id:
                uniprot_id = obj.interacting_id.replace("uniprotkb:", "")
            else:
                uniprot_id = obj.interacting_id.replace("protein ontology:", "")
            try:
                response = requests.get(
                    f"https://rest.uniprot.org/uniprotkb/{uniprot_id}?fields=accession%2Cgene_names"
                )
                data = json.loads(response.text)
                hgnc = data["genes"][0]["geneName"]["value"]
            except Exception:
                hgnc = ""
        elif e_transcript:
            e_transcript = e_transcript[0].split(".")[0]
            try:
                response = requests.get(
                    f"https://rest.ensembl.org/lookup/id/{e_transcript}?content-type=application/json"
                )
                data = json.loads(response.text)
                if "Parent" in data:
                    parent = data["Parent"]
                    parent_response = requests.get(
                        f"https://rest.ensembl.org/lookup/id/{parent}?content-type=application/json"
                    )
                    parent_data = json.loads(parent_response.text)
                    hgnc = parent_data["display_name"]
                else:
                    hgnc = data["display_name"]
            except Exception:
                hgnc = ""
        else:
            hgnc = ""

        if hgnc:
            try:
                response = requests.get(
                    f"https://rest.genenames.org/fetch/symbol/{hgnc}",
                    headers={"Accept": "application/json"},
                )
                data = json.loads(response.text)
                num_found = data["response"]["numFound"]
                if num_found > 0:
                    hgnc_id = data["response"]["docs"][0]["hgnc_id"]
                    hgnc_url = f"http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id={hgnc_id}"
                else:
                    hgnc_url = ""
            except Exception:
                hgnc_url = ""
        else:
            hgnc_url = ""

        return hgnc, hgnc_url

    def get_source(self, obj):
        return "View in QuickGO" if "PSICQUIC" in obj.intact_id else "View in IntAct"
