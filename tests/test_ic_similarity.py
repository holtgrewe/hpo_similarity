"""
Copyright (c) 2015 Wellcome Trust Sanger Institute

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import math
import unittest

from hpo_similarity.ontology import open_ontology
from hpo_similarity.similarity import ICSimilarity

class TestICSimilarityPy(unittest.TestCase):
    """ class to test ICSimilarity
    """
    
    def setUp(self):
        """ construct a ICSimilarity object for unit tests
        """
        
        path = os.path.join(os.path.dirname(__file__), "data", "obo.txt")
        self.hpo_graph, _, _ = open_ontology(path)
        
        self.hpo_terms = {
            "person_01": ["HP:0000924"],
            "person_02": ["HP:0000118", "HP:0002011"],
            "person_03": ["HP:0000707", "HP:0002011"]
        }
        
        self.hpo_graph.tally_hpo_terms(self.hpo_terms)
    
    def test_get_term_count(self):
        """ check that get_term_count works correctly
        
        All of the counts here are derived from their usage in self.hpo_terms
        """
        
        # check that we count the term usage (and subterms correctly)
        self.assertEqual(self.hpo_graph.get_term_count("HP:0000118"), 3)
        self.assertEqual(self.hpo_graph.get_term_count("HP:0000707"), 2)
        self.assertEqual(self.hpo_graph.get_term_count("HP:0002011"), 2)
        
        # check that a terminal node, only used once in the probands, has a
        # count of 1
        self.assertEqual(self.hpo_graph.get_term_count("HP:0000924"), 1)
        
        # check the term/subterm count for a term that isn't used within any of
        # he probands, but which all of the used terms descend from.
        self.assertEqual(self.hpo_graph.get_term_count("HP:0000001"), 3)
    
    def test_calculate_information_content(self):
        """ check that calculate_information_content works correctly
        """
        
        # check that the top node has an information content of 0
        self.assertEqual(self.hpo_graph.calculate_information_content("HP:0000001"), \
            0)
        
        # check the information content for a terminal node
        self.assertAlmostEqual(self.hpo_graph.calculate_information_content("HP:0000924"), \
            -math.log(1/3.0))
        
        # check the information content for a node that is somewhat distant, but
        # which has some descendant nodes that need to be included in the term
        # count
        self.assertAlmostEqual(self.hpo_graph.calculate_information_content("HP:0000707"), \
            -math.log(2/3.0))
        
    def test_get_most_informative_ic(self):
        """ check that get_most_informative_ic works correctly
        """
        
        # check the most informative information content for two nodes where
        # every common ancestor is the ancestor of all terms used in the probands
        self.assertAlmostEqual(self.hpo_graph.get_most_informative_ic("HP:0000707", \
            "HP:0000924"), 0)
        
        # check the most informative information content for two nodes where
        # both nodes are somewhat down the HPO graph
        self.assertAlmostEqual(self.hpo_graph.get_most_informative_ic("HP:0000707", \
            "HP:0002011"), -math.log(2/3.0))
            
        # check the most informative information content for two identical nodes
        self.assertAlmostEqual(self.hpo_graph.get_most_informative_ic("HP:0000924", \
            "HP:0000924"), -math.log(1/3.0))
