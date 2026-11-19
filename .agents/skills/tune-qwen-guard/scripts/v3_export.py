"""Keep Ollama's native Jinja and Modelfile templates consistent for v3.

Ollama 0.40.16 prefers tokenizer.chat_template to the Go TEMPLATE on default
generation. Replace only this fixed-size metadata string, retaining all tensor
bytes and offsets. Every exported candidate also gets the matching Modelfile.
"""
from pathlib import Path

from gguf import GGUFReader, GGUFValueType
import v3_protocol as p


def native_template(length):
    text = p.TEMPLATE.read_text().replace('{{ .Prompt }}', "{{ messages[-1]['content'] }}")
    remaining = length - len(text.encode())
    if remaining < 4:
        raise ValueError('Source template field is too short for an in-place replacement')
    return text + '{#' + ' ' * (remaining - 4) + '#}'


def patch_template(path):
    path = Path(path)
    reader = GGUFReader(path)
    field = reader.fields['tokenizer.chat_template']
    if field.types != [GGUFValueType.STRING] or len(field.data) != 1:
        raise ValueError('Expected scalar native template')
    data = field.parts[field.data[0]]
    offset = int(data.__array_interface__['data'][0] - reader.data.__array_interface__['data'][0])
    replacement = native_template(data.nbytes).encode()
    if len(replacement) != data.nbytes:
        raise ValueError('Metadata patch would change tensor offsets')
    with path.open('r+b') as f:
        f.seek(offset); f.write(replacement)
    return dict(offset=offset, bytes=len(replacement), template_sha256=p.sha(p.TEMPLATE))
