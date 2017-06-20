from rest_framework import renderers


class BrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    Use this renderer instead of the original one to customize context variables.
    """

    def get_context(self, data, accepted_media_type, renderer_context):
        """
        """
        context = super(BrowsableAPIRenderer, self).get_context(data, accepted_media_type, renderer_context)
        return context


class RnaFastaRenderer(renderers.BaseRenderer):
    """
    Render the fasta data received from RnaFastaSerializer.
    """
    media_type = 'text/fasta'
    format = 'fasta'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaFastaSerializer can return either a single entry or a list of entries.
        """
        if 'results' in data: # list of entries
            text = '# %i total entries, next page: %s, previous page: %s\n' % (data['count'], data['next'], data['previous'])
            for entry in data['results']:
                text += entry['fasta']
            return text
        elif isinstance(data, list):
            text = []
            for entry in data:
                text.append(entry['fasta'])
            return ''.join(text)
        else: # single entry
            return data['fasta']


class RnaGffRenderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in GFF format received from RnaGffSerializer.
    """
    media_type = 'text/gff'
    format = 'gff'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaGffSerializer returns a single entry.
        """
        text = data['gff']
        if not text:
            text = '# Genomic coordinates not available'
        return text


class RnaGff3Renderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in GFF3 format received from RnaGff3Serializer.
    """
    media_type = 'text/gff3'
    format = 'gff3'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaGff3Serializer returns a single entry.
        """
        text = data['gff3']
        if not text or text == '##gff-version 3\n':
            text = '# Genomic coordinates not available'
        return text


class RnaBedRenderer(renderers.BaseRenderer):
    """
    Render the genomic coordinates in UCSC BED format received from RnaBedSerializer.
    """
    media_type = 'text/bed'
    format = 'bed'

    def render(self, data, media_type=None, renderer_context=None):
        """
        RnaBedSerializer returns a single entry.
        """
        text = data['bed']
        if not text:
            text = '# Genomic coordinates not available'
        return text
