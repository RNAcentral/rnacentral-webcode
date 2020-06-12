from rest_framework import renderers


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
        if 'results' in data:  # list of entries
            text = '# %i total entries, next page: %s, previous page: %s\n' % (data['count'], data['next'], data['previous'])
            for entry in data['results']:
                text += entry['fasta']
            return text
        elif isinstance(data, list):
            text = []
            for entry in data:
                text.append(entry['fasta'])
            return ''.join(text)
        else:  # single entry
            return data['fasta']
