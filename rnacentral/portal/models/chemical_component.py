from caching.base import CachingMixin, CachingManager
from django.db import models


class ChemicalComponent(CachingMixin, models.Model):
    """List of all possible nucleotide modifications."""
    id = models.CharField(max_length=8, primary_key=True)
    description = models.CharField(max_length=500)
    one_letter_code = models.CharField(max_length=1)
    ccd_id = models.CharField(max_length=3, default='')  # Chemical Component Dictionary id
    source = models.CharField(max_length=10, default='')  # Modomics, PDBe, others
    modomics_short_name = models.CharField(max_length=20, default='')  # m2A for 2A

    objects = CachingManager()

    class Meta:
        db_table = 'rnc_chemical_components'

    def get_pdb_url(self):
        """
        Get a link to PDB Chemical Component Dictionary from PDB entries and
        Modomics entries that are mapped to PDB.
        """
        pdb_url = 'http://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/{id}'
        if self.source == 'PDB':
            return pdb_url.format(id=self.id)
        elif self.source == 'Modomics' and self.ccd_id:
            return pdb_url.format(id=self.ccd_id)
        else:
            return None

    def get_modomics_url(self):
        """Get a link to Modomics modifications."""
        return 'http://modomics.genesilico.pl/modifications/%s' % self.modomics_short_name if self.source == 'Modomics' else None