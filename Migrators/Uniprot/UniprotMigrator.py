from typedb.client import TransactionType
import csv
import re

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from Migrators.Helpers.batchLoader import write_batch


def migrate_uniprot(session, num, num_threads, batch_size):
    if num != 0:
        print('  ')
        print('Opening Uniprot dataset...')
        print('  ')


        uniprotdb = get_uniprotdb(num_threads)
        insert_organism(uniprotdb, session, num_threads, batch_size)
        insert_genes(uniprotdb, session, num_threads, batch_size)
        insert_proteins(uniprotdb, session, num_threads, batch_size)
        insert_transcripts(uniprotdb, session, num_threads, batch_size)
        insert_transcripts2(uniprotdb, session, num_threads, batch_size)
        insert_gene_protein_encoding(uniprotdb, session, num_threads, batch_size)
        print('.....')
        print('Finished migrating Uniprot file.')
        print('.....')


def get_uniprotdb(split_size):
    with open('Dataset/Uniprot/uniprot-reviewed_yes+AND+proteome.tsv', 'rt', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='\t')
        raw_file = []
        n = 0
        for row in csvreader:
            n = n + 1
            if n != 1:
                raw_file.append(row)

    uniprotdb = []
    for i in raw_file[:split_size]:
        data = {}
        data['uniprot-id'] = i[0]
        data['uniprot-entry-name'] = i[1]
        data['protein-name'] = i[3]
        data['gene-symbol'] = i[4]
        data['organism'] = i[5]
        data['function-description'] = i[7]
        data['ensembl-transcript'] = i[11]
        data['entrez-id'] = i[12]
        uniprotdb.append(data)
    return uniprotdb

def transcript_helper(q):
    list = []
    n = q['ensembl-transcript']
    nt = n.count(';')
    if nt != 0:
        while nt != 0:
            nt = nt - 1
            pos = [m.start() for m in re.finditer(r";", n)]
            if nt == 0:
                n2 = n[0:pos[0]]
            else:
                try:
                    pos_st = pos[nt - 1] + 1
                    pos_end = pos[nt]
                    n2 = n[pos_st:pos_end]
                except:
                    pass
            #estr = n2.find('[') - 1
            #n2 = n2[:estr]
            list.append(n2)
    list1 = ','.join(list)
    return list1

# Insert transcripts
def insert_transcripts(uniprotdb, session, num_threads, batch_size):
    batch = []
    batches = []
    batch1 = []
    batches1 = []

    for q in uniprotdb:
        if q['ensembl-transcript'] != '':
            tr = transcript_helper(q)

            typeql = f"insert $t isa transcript, has ensembl-transcript-stable-id '{tr}';"
            if q['protein-name'] != '':
                typeql1 =  f"match $p isa protein, has uniprot-name '{q['protein-name']}'; $t isa transcript, has ensembl-transcript-stable-id '{tr}'; insert $r (translating-transcript:$t, translated-protein: $p) isa translation;"
            batch.append(typeql)
            batch1.append(typeql1)
            if len(batch) == batch_size:
                batches.append(batch)
                batch = []
            if len(batch1) == batch_size:
                batches1.append(batch1)
                batch1 = []
    batches.append(batch)
    batches1.append(batch1)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.map(partial(write_batch, session), batches1)
    pool.close()
    pool.join()
    print('Transcripts committed!')

def insert_transcripts2(uniprotdb, session, num_threads, batch_size):
    batch = []
    batches = []
    for q in uniprotdb:
        if q['ensembl-transcript'] != '':
            tr = transcript_helper(q)
            if q['gene-symbol'] != "":
                typeql = f"match $g isa gene, has gene-symbol '{q['gene-symbol']}'; $t isa transcript, has ensembl-transcript-stable-id '{tr}'; insert $r2 (transcribing-gene: $g, encoded-transcript:$t) isa transcription;"
                batch.append(typeql)
                if len(batch) == batch_size:
                    batches.append(batch)
                    batch = []
    batches.append(batch)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.close()
    pool.join()



# Returns: a list of [gene, entrez-id]
# Method removes synonyms from genes and only takes the first one
def gene_helper(q):
    gene_name = q['gene-symbol']
    entrez_id = q['entrez-id'][0:-1]
    if gene_name.find(' ') != -1:
        gene_name = gene_name[0:gene_name.find(' ')]
    list = [gene_name, entrez_id]
    return list

def insert_organism(uniprotdb, session, num_threads, batch_size):
    protein_list = []
    batch = []
    batches = []

    for q in uniprotdb:
        if q['protein-name'] != '':
            typeql = f"match $p isa protein, has uniprot-name '{q['protein-name']}'; insert $h isa organism, has organism-name '{q['organism']}'; $r (associated-organism: $h, associating: $p) isa organism-association;"
            batch.append(typeql)
            if len(batch) == batch_size:
                batches.append(batch)
                batch = []
    batches.append(batch)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.close()
    pool.join()
    print('organisms committed!')


# Insert genes from gene-symbol.
# NB: We only insert the first name, if there are synonyms, we ignore them.
def insert_genes(uniprotdb, session, num_threads, batch_size):
    gene_list = []
    batch = []
    batches = []
    for q in uniprotdb:
        if q['gene-symbol'] != "":
            gene_list.append(gene_helper(q))

    # gene_list = list(dict.fromkeys(gene_list)) # TO DO: Remove duplicate gene-symbols

    for g in gene_list:
        typeql = f"insert $g isa gene, has gene-symbol '{g[0]}', has entrez-id '{g[1]}';"
        batch.append(typeql)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []
    batches.append(batch)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.close()
    pool.join()
    print('Genes committed!')






def protein_helper(q):
    uniprot_id = q['uniprot-id']
    uniprot_name = q['protein-name']
    function_description = q['function-description']
    uniprot_entry_name = q['uniprot-entry-name']

    list = [uniprot_id, uniprot_name, function_description, uniprot_entry_name]
    return list

def insert_proteins(uniprotdb, session, num_threads, batch_size):
    protein_list = []
    batch = []
    batches = []

    for q in uniprotdb:
        if q['uniprot-id'] != "":
            protein_list.append(protein_helper(q))

    for p in protein_list:
        typeql = f"insert $p isa protein, has uniprot-id '{p[0]}', has uniprot-name '{p[1]}', has function-description '{p[2]}', has uniprot-entry-name '{p[3]}';"
        batch.append(typeql)
        if len(batch) == batch_size:
            batches.append(batch)
            batch = []
    batches.append(batch)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.close()
    pool.join()
    print('Proteins committed!')

def insert_gene_protein_encoding(uniprotdb, session, num_threads, batch_size):
    batch = []
    batches = []
    list = []
    for q in uniprotdb:
        if q['gene-symbol'] != "":
            typeql = f"match $g isa gene, has gene-symbol '{q['gene-symbol']}'; $p isa protein, has uniprot-name '{q['protein-name']}'; insert $gpe (encoding-gene: $g, encoded-protein: $p) isa gene-protein-encoding;"
            batch.append(typeql)
            if len(batch) == batch_size:
                batches.append(batch)
                batch = []
    batches.append(batch)
    pool = ThreadPool(num_threads)
    pool.map(partial(write_batch, session), batches)
    pool.close()
    pool.join()
