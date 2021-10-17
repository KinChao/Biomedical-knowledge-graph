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

cd C:\Users\mqcha\Downloads\typdb

Run the migrate file with the following code:

python migrator.py -n x   ----  x=number of threads used in cpu
e.g.         python migrator.py -n 8

If the database already existed, use the following code instead:

python migrator.py -n x -f TRUE  --- x=number of threads used in cpu
 
 
Query example: 
example query using typedb workbase:

match

$g isa gene, has gene-symbol "YWHAG";

$p isa protein;

$1 ($g, $p) isa gene-protein-encoding;
 

