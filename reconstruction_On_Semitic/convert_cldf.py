import pathlib
from cldfbench import Dataset as BaseDataset, CLDFSpec, CLDFWriter

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "kogansemitic"

    def cldf_specs(self):
        return CLDFSpec(module='Wordlist', dir=self.cldf_dir)

    def sanitize_id(self, id_string):
        sanitized = (id_string.replace(' ', '_')
                         .replace(',', '_')
                         .replace('\'', '')
                         .replace('ä', 'a')
                         .replace('č', 'c')
                         .replace('ə', 'e')
                         .replace('ö', 'o')
                         .replace('ü', 'u')
                         .replace('ō', 'o')
                         .replace('é', 'e')
                         .replace('í', 'i')
                         .replace('ý', 'y')
                         .replace('Č', 'C')
                         .replace('Ž', 'Z')
                         .replace('Ə', 'E')
                         .replace('Á', 'A')
                         .replace('Ó', 'O')
                         .replace('Ú', 'U')
                         .replace('ó', 'o')
                         .replace('Ä', 'A')
                         .replace('Ž', 'Z')
                         .replace('ž', 'z')  # Replace lowercase ž
                         .replace('Š', 'S')
                         .replace('__', '_'))  # Replace double underscores if any
        return sanitized.strip('_')

    def cmd_makecldf(self, args):
        if args is None:
            args = self.make_args()

        self.cldf_dir.mkdir(exist_ok=True)

        with CLDFWriter(self.cldf_specs(), dataset=self) as writer:
            args.writer = writer

            if not writer.cldf.get('LanguageTable'):
                writer.cldf.add_component('LanguageTable')
            if not writer.cldf.get('ParameterTable'):
                writer.cldf.add_component('ParameterTable')
            if not writer.cldf.get('FormTable'):
                writer.cldf.add_component('FormTable')
            if not writer.cldf.get('CognateTable'):
                writer.cldf.add_component('CognateTable')

            tsv_file_path = self.raw_dir / 'proto_semitic_words.tsv'
            rows = list(self.raw_dir.read_csv(tsv_file_path, delimiter='\t', dicts=True))

            languages = {}
            concepts = {}

            # Add languages
            for row in rows:
                lang_id = self.sanitize_id(row['DOCULECT'])
                if not lang_id:
                    continue  # Skip if ID is missing
                if lang_id not in languages:
                    languages[lang_id] = row['DOCULECT']
                    writer.objects['LanguageTable'].append({"ID": lang_id, "Name": row['DOCULECT']})

            # Add concepts (parameters)
            for row in rows:
                concept_id = self.sanitize_id(row['CONCEPT'])
                if not concept_id:
                    continue  # Skip if ID is missing
                if concept_id not in concepts:
                    concepts[concept_id] = row['CONCEPT']
                    writer.objects['ParameterTable'].append({"ID": concept_id, "Name": row['CONCEPT']})

            # Add forms and cognates
            cognate_counter = 1
            form_counter = 1
            for row in rows:
                # Generate form ID
                form_id = f"form_{form_counter}"
                form_counter += 1
                language_id = self.sanitize_id(row['DOCULECT'])
                concept_id = self.sanitize_id(row['CONCEPT'])
                value = row.get('VALUE')
                form = row.get('FORM')
                cognate_id = row.get('COGID')

                # Ensure necessary fields are present
                if not concept_id or not language_id or not form:
                    continue

                writer.objects['FormTable'].append({
                    "ID": form_id,
                    "Language_ID": language_id,
                    "Parameter_ID": concept_id,
                    "Value": value,
                    "Form": form
                })

                # Generate cognate ID
                cognate_entry_id = f"cognate_{cognate_counter}"
                cognate_counter += 1

                writer.objects['CognateTable'].append({
                    "ID": cognate_entry_id,
                    "Form_ID": form_id,
                    "Cognateset_ID": cognate_id
                })

            writer.write()
            print(f"Files written to {self.cldf_dir}")

    def make_args(self):
        class Args:
            def __init__(self, writer):
                self.writer = writer
                self.log = self

            def info(self, msg):
                print(msg)

        return Args(None)

if __name__ == '__main__':
    dataset = Dataset()
    dataset.cmd_makecldf(None)
    print("CLDF conversion complete.")
