""" simple functions to load and parse data for HPO terms analyses
"""

import sys

def load_ddg2p(ddg2p_path):
    """ load a DDG2P gene file, so we can extract HPO terms for each gene
    
    Args:
        ddg2p_path: path to DDG2P file
    
    Returns:
        dictionary of hpo terms indexed by gene name, then inheritance type
    """
    
    f = open(ddg2p_path)
    
    # allow for gene files with different column names and positions
    header = f.readline().strip().split("\t")
    if "DDD_category" in header:
        gene_label = "gencode_gene_name"
        inheritance_label = "Allelic_requirement"
        hpo_label = "HPO_ids"
    else:
        raise ValueError("The gene file lacks expected header column names")
    
    # get the positions of the columns in the list of header labels
    gene_column = header.index(gene_label)
    inheritance_column = header.index(inheritance_label)
    hpo_column = header.index(hpo_label)
    
    genes = {}
    for line in f:
        line = line.split("\t")
        
        gene = line[gene_column]
        inheritance = line[inheritance_column]
        hpo_terms = line[hpo_column].strip()
        
        if gene not in genes:
            genes[gene] = {}
        
        if inheritance not in genes[gene]:
            genes[gene][inheritance] = set()
        
        # split the hpo terms, then update the gene/inheritance set
        hpo_terms = hpo_terms.split(";")
        hpo_terms = [x.strip() for x in hpo_terms]
        genes[gene][inheritance].update(hpo_terms)
        
    return genes


class FamilyHPO(object):
    """small class to handle HPO terms for family members of a trio
    """
    
    def __init__(self, child_hpo, maternal_hpo, paternal_hpo):
        """initiate the class
        
        Args:
            child_hpo: HPO string for the proband, eg "HP:0005487|HP:0001363"
            maternal_hpo: string of HPO terms for the mother
            paternal_hpo: string of HPO terms for the father
        """
        
        self.child_hpo = self.format_hpo(child_hpo)
        self.maternal_hpo = self.format_hpo(maternal_hpo)
        self.paternal_hpo = self.format_hpo(paternal_hpo)
    
    def format_hpo(self, hpo_terms):
        """ formats a string of hpo terms to a list
        
        Args:
            hpo_terms: string of hpo terms joined with "|"
        
        Returns:
            list of hpo terms, or None
        """
        
        hpo_terms = hpo_terms.strip()
        
        # account for no hpo terms recorded for a person
        if hpo_terms == ".":
            return None
        
        # account for multiple hpo terms for an individual
        if "|" in hpo_terms:
            hpo_terms = hpo_terms.split("|")
        else:
            hpo_terms = [hpo_terms]
        
        return hpo_terms
    
    def get_child_hpo(self):
        return self.child_hpo
    
    def get_maternal_hpo(self):
        return self.maternal_hpo
    
    def get_paternal_hpo(self):
        return self.paternal_hpo


def load_participants_hpo_terms(pheno_path, alt_id_path):
    """ loads patient data, and obtains
    """
    
    alt_ids = load_alt_id_map(alt_id_path)
    
    # load the phenotype data for each participant
    f = open(pheno_path)
    header = f.readline().strip().split("\t")
    
    # get the positions of the columns in the list of header labels
    proband_column = header.index("patient_id")
    child_hpo_column = header.index("child_hpo")
    maternal_hpo_column = header.index("maternal_hpo")
    paternal_hpo_column = header.index("paternal_hpo")
    
    participant_hpo = {}
    for line in f:
        line = line.split("\t")
        proband_id = line[proband_column]
        child_hpo = line[child_hpo_column]
        maternal_hpo = line[maternal_hpo_column]
        paternal_hpo = line[paternal_hpo_column]
        
        # swap the proband across to the DDD ID if it exists
        if proband_id in alt_ids:
            proband_id = alt_ids[proband_id]
        
        participant_hpo[proband_id] = FamilyHPO(child_hpo, maternal_hpo, paternal_hpo)
    
    return participant_hpo

def load_participants_phenotypes(pheno_path, alt_id_path):
    """ loads patient data, and obtains
    """
    
    alt_ids = load_alt_id_map(alt_id_path)
    
    # load the phenotype data for each participant
    f = open(pheno_path)
    
    # allow for gene files with different column names and positions
    header = f.readline().strip().split("\t")
    
    # get the positions of the columns in the list of header labels
    proband_column = header.index("patient_id")
    height_column = header.index("height_sd")
    weight_column = header.index("weight_sd")
    ofc_column = header.index("ofc_sd")
    
    phenotypes = {}
    for line in f:
        line = line.split("\t")
        proband_id = line[proband_column]
        height_sd = line[height_column]
        weight_sd = line[weight_column]
        ofc_sd = line[ofc_column]
        
        # swap the proband across to the DDD ID if it exists
        if proband_id in alt_ids:
            proband_id = alt_ids[proband_id]
        
        phenotypes[proband_id] = {"height": height_sd, "weight": weight_sd, \
            "ofc": ofc_sd}
    
    return phenotypes

def load_alt_id_map(alt_id_path):
    """ loads the decipher to DDD ID mapping file
    """
    
    alt_ids = {}
    
    with open(alt_id_path) as f:
        for line in f:
            line = line.split("\t")
            ref_id = line[0]
            alt_id = line[1]
            
            # if ":" in alt_id:
            #     alt_id = alt_id.split(":")[0]
            
            alt_ids[alt_id] = ref_id
    
    return alt_ids

def load_candidate_genes(candidate_genes_path):
    """ loads candidate genes for the participants
    """
    
    f = open(candidate_genes_path)
    header = f.readline().strip().split("\t")
    
    proband_column = header.index("proband")
    gene_column = header.index("gene")
    inheritance_column = header.index("inheritance")
    
    genes_index = {}
    probands_index = {}
    
    for line in f:
        # ignore blank lines
        if line == "\n":
            continue
        
        line = line.strip().split("\t")
        proband_ID = line[proband_column]
        gene = line[gene_column]
        inheritance = line[inheritance_column]
        
        if gene not in genes_index:
            genes_index[gene] = set()
         
        if proband_ID not in probands_index:
            probands_index[proband_ID] = set()
         
        genes_index[gene].add((proband_ID, inheritance))
        probands_index[proband_ID].add((gene, inheritance))
    
    return genes_index, probands_index

def load_obligate_terms(obligate_path):
    """ loads a list of HPO terms for specific genes that affected people must have
    """
    
    f = open(obligate_path)
    header = f.readline().strip().split("\t")
    
    # pull out the column numbers from the header
    gene_label = "gene"
    hpo_label = "hpo_id"
    gene_column = header.index(gene_label)
    hpo_column = header.index(hpo_label)
    
    obligate_genes = {}
    for line in f:
        line = line.strip().split("\t")
        gene = line[gene_column]
        hpo_term = line[hpo_column]
        
        if gene not in obligate_genes:
            obligate_genes[gene] = []
        
        obligate_genes[gene].append(hpo_term)
    
    return obligate_genes
    
def load_organ_terms(organ_to_hpo_mapper_path, ddg2p_organ_path):
    """ loads dict of hpo terms specific for DDG2P genes
    
    Args:
        organ_to_hpo_mapper_path: path to file listing HPO terms for abnormality for each organ
        ddg2p_organ_path: path to file listing organ abnormalities for ddg2p genes
    
    Returns:
        dictionary of hpo lists indexed by gene
    """
    
    f = open(organ_to_hpo_mapper_path)
    header = f.readline().strip().split("\t")
    organ_label = "organ"
    hpo_label = "hpo_id"
    organ_column = header.index(organ_label)
    hpo_column = header.index(hpo_label)
    
    # pull out the hpo terms that match organ labels
    organ_map = {}
    for line in f:
        line = line.strip().split("\t")
        organ = line[organ_column]
        hpo_term = line[hpo_column]
        
        organ_map[organ] = hpo_term
    
    # now open the list of ddg2p genes with their suggested organs
    f = open(ddg2p_organ_path)
    header = f.readline().strip().split("\t")
    gene_label = "gene"
    organ_label = "organ"
    gene_column = header.index(gene_label)
    organ_column = header.index(organ_label)
    
    obligate_organs = {}
    for line in f:
        line = line.strip().split("\t")
        gene = line[gene_column]
        organ = line[organ_column]
        
        if organ in organ_map:
            hpo_term = organ_map[organ]
        else:
            sys.exit("Unknown organ for DDG2P gene: " + gene + ", in: " + organ)
        
        if gene not in obligate_organs:
            obligate_organs[gene] = []
        
        obligate_organs[gene].append(hpo_term)
    
    return obligate_organs
        
def load_full_proband_hpo_list(path):
    """ loads a set of hpo terms from all probands recruited to date
    
    Args:
        path: path to proband phenotype file
    
    Returns:
        list of (proband, hpo_term) tuples
    """
    
    f = open(path, "r")
    
    hpo_list = []
    for line in f:
        line = line.strip().split("\t")
        proband = line[0]
        hpo_term = line[2]
        
        hpo_list.append((proband, hpo_term))
    
    return hpo_list
        
