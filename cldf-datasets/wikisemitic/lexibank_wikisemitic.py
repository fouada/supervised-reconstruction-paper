import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language
from pylexibank import FormSpec

from raw.misc.replacements import replacements

blacklist = set(["Ì.GIŠ [m]ar-ru₁₂-um", "sú-ú-[sí-ma]", "íb-dum;  ì-ba-dum", "š[ˁl]", "*ḥVṣ-; *ḥVṣVṣ-",
                 "ù-gi-l[um]", "ti-[n]a?-[t]u₄", "ma-ar-˹ba˺-d[u]", "ga-ag-gi-m[i]"
                 "ri-i[g]-lu", "ma-[s]a-a-um /mašāyum/", "ŠE.MEŠ ḳè-e-ṣí"])
id_blacklist = set(["12082", "1286"])

@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "wikisemitic"
    form_spec = FormSpec(separators=",/ ", missing_data=["∅"], first_form_only=True,
                         replacements=replacements)
    language_class = CustomLanguage

    def cmd_download(self, args):
        """
        Download files to the raw/ directory.
        """
        # Here, we simply copy the existing TSV file to the raw directory
        self.raw_dir.write("proto_semitic_words.tsv", self.dir.parent.parent.joinpath("proto_semitic_words.tsv").read_text())

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        concepts = {}
        for concept in self.concepts:
            idx = concept["NUMBER"]+"_"+slug(concept["ENGLISH"])
            concepts[concept["ENGLISH"]] = idx
            try:
                args.writer.add_concept(
                    ID=idx,
                    Name=concept["ENGLISH"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"]
                )
            except KeyError:
                args.writer.add_concept(
                    ID=idx,
                    Name=concept["ENGLISH"]
                )

        languages = args.writer.add_languages(lookup_factory="Name")

        # read in data from the TSV file
        data = self.raw_dir.read_csv(
            "proto_semitic_words.tsv", delimiter="\t",
            dicts=True
        )
        
        # add data
        for i, row in pb(enumerate(data), desc="cldfify", total=len(data)):
            cog = row["COGID"]
            concept = row["CONCEPT"]
            # fetch cid from concepts if it exists
            cid = concepts.get(concept, None)
            if not cid:
                args.log.info(f"Concept for {row['ID']} not found")
                continue
            lid = slug(row["DOCULECT"])
            entry = row["VALUE"]
            # skip blacklisted entries
            if entry in blacklist or row["ID"] in id_blacklist:
                continue

            for lex in args.writer.add_forms_from_value(
                    Language_ID=lid,
                    Parameter_ID=cid,
                    Value=entry,
                    Cognacy=cog
                    ):
                args.writer.add_cognate(
                    lexeme=lex,
                    Cognateset_ID=cog
                )
