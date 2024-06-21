class Prompts():
    def __init__(self):
        self.ner = """
        You are an AI trained to analyze sentences and extract entities and their relationships. For each entity, identify its type 
        (e.g., politician, organization, law/bill, other) and list any alternative names by which the entity might be known.

        Please process the following sentence and return the entities with their types and the relationships between them in JSON format:

        Sentence: "Ted Cruz is backed by the NRA."

        Instructions:
        - List each entity with its type and any known alternative names.
        - Describe the relationship between the entities clearly.

        Expected Format:
        - JSON output including entities and their types along with alternative names, and the relationships among them.

        Here is the expected output for the sentence above:

        {
        "entities": [
            {
            "name": "Ted Cruz",
            "type": "Politician",
            "alternative_names": ["Cruz", "Ted"]
            },
            {
            "name": "NRA",
            "type": "Organization",
            "alternative_names": ["National Rifle Association"]
            }
        ],
        "relationships": [
            {
            "source": "Ted Cruz",
            "relation": "is supported by",
            "target": "NRA"
            }
        ]
        }

        Second example:
        "Senator Elizabeth Warren introduced the Consumer Protection Act, which was opposed by several large corporations including Apple and Google."

        Expected output:
        {
        "entities": [
            {
            "name": "Elizabeth Warren",
            "type": "Politician",
            "alternative_names": ["Senator Warren", "Warren"]
            },
            {
            "name": "Consumer Protection Act",
            "type": "Law/Bill",
            "alternative_names": ["CPA"]
            },
            {
            "name": "Apple",
            "type": "Organization",
            "alternative_names": ["Apple Inc."]
            },
            {
            "name": "Google",
            "type": "Organization",
            "alternative_names": ["Google LLC"]
            }
        ],
        "relationships": [
            {
            "source": "Elizabeth Warren",
            "relation": "introduced",
            "target": "Consumer Protection Act"
            },
            {
            "source": "Consumer Protection Act",
            "relation": "was opposed by",
            "target": "Apple"
            },
            {
            "source": "Consumer Protection Act",
            "relation": "was opposed by",
            "target": "Google"
            }
        ]
        }

        Now do this for the following piece of text
        
        Case Sheet:
        $ctext
        """
        