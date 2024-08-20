import pathlib
from cldfbench import Dataset as BaseDataset, CLDFSpec, CLDFWriter

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "kogansemitic"

    def cldf_specs(self):
        return CLDFSpec(module='Wordlist', dir=self.cldf_dir)

    def cmd_makecldf(self, args):
        if args is None:
            args = self.make_args()

        # Ensure the directory exists
        self.cldf_dir.mkdir(exist_ok=True)

        with CLDFWriter(self.cldf_specs(), dataset=self) as writer:
            args.writer = writer

            # Add components only if they do not exist already
            if not writer.cldf.get('LanguageTable'):
                writer.cldf.add_component('LanguageTable')
            if not writer.cldf.get('ParameterTable'):
                writer.cldf.add_component('ParameterTable')
            if not writer.cldf.get('FormTable'):
                writer.cldf.add_component('FormTable')
            if not writer.cldf.get('CognateTable'):
                writer.cldf.add_component('CognateTable')

            # Read the TSV data
            print("Reading TSV file...")
            tsv_file_path = self.raw_dir / 'proto_semitic_words.tsv'
            rows = list(self.raw_dir.read_csv(tsv_file_path, delimiter='\t', dicts=True))

            # Create dictionaries to store unique languages and concepts
            languages = {row['DOCULECT'].replace(' ', '_'): row['DOCULECT'] for row in rows}
            concepts = {row['CONCEPT'] for row in rows}

            # Add languages
            print(f"Found {len(languages)} languages.")
            for key, value in languages.items():
                print(f"Adding language: {key}, {value}")
                writer.objects['LanguageTable'].append({"ID": key, "Name": value})

            # Add concepts (parameters)
            print(f"Adding {len(concepts)} concepts.")
            for concept in concepts:
                writer.objects['ParameterTable'].append({"ID": concept, "Name": concept})

            # Add forms and cognates
            print("Adding forms and cognates...")
            for row in rows:
                form_id = row['form_id']
                language_id = row['DOCULECT'].replace(' ', '_')
                concept_id = row['CONCEPT']
                value = row['VALUE']
                form = row['FORM']
                cognate_id = row['COGID']

                print(f"Adding form: {form_id}, {language_id}, {concept_id}, {value}, {form}")
                writer.objects['FormTable'].append({
                    "ID": form_id,
                    "Language_ID": language_id,
                    "Parameter_ID": concept_id,
                    "Value": value,
                    "Form": form
                })

                print(f"Adding cognate: {form_id}, {cognate_id}")
                writer.objects['CognateTable'].append({
                    "Form_ID": form_id,
                    "Cognateset_ID": cognate_id
                })

            # Explicitly write files
            writer.write()
            print(f"Files written to {self.cldf_dir}")

    def make_args(self):
        """Simulates the args object that would be provided by cldfbench."""
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
