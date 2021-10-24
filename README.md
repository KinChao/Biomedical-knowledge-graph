Installation

Install typedb
https://vaticle.com/download 

Install typedb workspace/ typedb studio
https://vaticle.com/download#typedb-workbase

open cmd and cd to the typedb folder, for example:

cd C:\Users\mqcha\Downloads\typedb-all-windows-2.4.0\typedb-all-windows-2.4.0

open typedb server using the following code

typedb server

open another cmd and cd to the project folder, for example:

cd C:\Users\mqcha\Downloads\typedb\Biomedical-knowledge-graph

Run the migrate file with the following code:

python migrator.py -n x   ----  x=number of threads used in cpu
e.g.         python migrator.py -n 8

If the database already existed, use the following code instead:

python migrator.py -n x -f TRUE  --- x=number of threads used in cpu
 


Uniprot dataset glossary
$t isa transcript, has 'ensembl-transcript-stable-id'
$p isa protein, has 'uniprot-name', 'uniprot-name', 'function-description', 'uniprot-entry-name'
$g isa gene, has 'gene-symbol', 'entrez-id'
$h isa organism, has 'organism-name'
(translating-transcript:$t, translated-protein: $p) isa translation
(transcribing-gene: $g, encoded-transcript:$t) isa transcription
(associated-organism: $h, associating: $p) isa organism-association
(encoding-gene: $g, encoded-protein: $p) isa gene-protein-encoding



Query example: 
example query using typedb workbase:

match

$g isa gene, has gene-symbol "YWHAG";

$p isa protein;

$1 ($g, $p) isa gene-protein-encoding;
 

