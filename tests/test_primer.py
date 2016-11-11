import unittest
import os
import sys
sys.path.insert(0, '../')
import starseqr_utils


path = os.path.dirname(__file__)
if path != '':
    os.chdir(path)

class PrimerTestCase(unittest.TestCase):
    '''Tests primer design'''
    def test_runp3_v1(self):
        """test_runp3"""
        seq = "CATCAGCAGAATTCCCGCCATAGGTTAACTCTTTGACATTCTTATTACCACTGTGGGTCTCTTTGGGATCCCAGGGCACTGTAGGCAACTAGAACAATGTCCTTGGACTTGCAGAACTCCAGGAGTTTGCTCTGGTTGAGGTAAGGGTGACATTCCACCTGTAATTTTTCAAGACCAAAAGGTGTCACAATATATGAGCCAATAACCACATGCAAATTTAAACTGGAAAATAGAAAAGAAGATAAAGAAGGACATTTTCTATGGAATTCTCCTTTCTGGTGCCTAAGGAGCTCGGCCAAACAACCTTCAAGAGTTTCAGGAGGTGGTGATTAT"
        primer_res = starseqr_utils.run_primer3.runp3('test1', seq)
        self.assertTrue(primer_res == ('TGGACTTGCAGAACTCCAGG', 'TGCATGTGGTTATTGGCTCA'))

    def test_runp3_v2(self):
        """test_runp3 with no target"""
        seq = ":CATCAGCAGAATTCCCGCCATAGGTTAACTCTTTGACATTCTTATTACCACTGTGGGTCTCTTTGGGATCCCAGGGCACTGTAGGCAACTAGAACAATGTCCTTGGACTTGCAGAACTCCAGGAGTTTGCTCTGGTTGAGGTAAGGGTGACATTCCACCTGTAATTTTTCAAGACCAAAAGGTGTCACAATATATGAGCCAATAACCACATGCAAATTTAAACTGGAAAATAGAAAAGAAGATAAAGAAGGACATTTTCTATGGAATTCTCCTTTCTGGTGCCTAAGGAGCTCGGCCAAACAACCTTCAAGAGTTTCAGGAGGTGGTGATTAT"
        primer_res = starseqr_utils.run_primer3.runp3('test1', seq)
        self.assertTrue(primer_res == ())

    def test_runp3_v3(self):
        """test_runp3 with short seq"""
        seq = "CATCAGCAGAATTCCCGCCATAG"
        primer_res = starseqr_utils.run_primer3.runp3('test1', seq)
        self.assertTrue(primer_res == ())

    def test_runp3_v4(self):
        """test_runp3 with small target"""
        seq = "CATCAGCA:GAATTCCCGCCATAGGTTAACTCTTTGACATTCTTATTACCACTGTGGGTCTCTTTGGGATCCCAGGGCACTGTAGGCAACTAGAACAATGTCCTTGGACTTGCAGAACTCCAGGAGTTTGCTCTGGTTGAGGTAAGGGTGACATTCCACCTGTAATTTTTCAAGACCAAAAGGTGTCACAATATATGAGCCAATAACCACATGCAAATTTAAACTGGAAAATAGAAAAGAAGATAAAGAAGGACATTTTCTATGGAATTCTCCTTTCTGGTGCCTAAGGAGCTCGGCCAAACAACCTTCAAGAGTTTCAGGAGGTGGTGATTAT"
        primer_res = starseqr_utils.run_primer3.runp3('test1', seq)
        self.assertTrue(primer_res == ())

    def test_wrap_runp3_v1(self):
        """test wrapper for runp3"""
        fusions = ['ENST00000372201.4--ENST00000432496.6',
                   'ENST00000372201.4--ENST00000394708.6',
                   'ENST00000372201.4--ENST00000273980.9',
                   'ENST00000372201.4--ENST00000361687.8',
                   'ENST00000372201.4--ENST00000394706.7']
        res1 = starseqr_utils.run_primer3.wrap_runp3('chr1:45268528:+:chr4:107152937:-:0:2', fusions)
        assert(res1 == ('CCTGAGGCGGATGTATGGTC', 'ACATACATGCATAAGCCAAGGC'))

    def test_wrap_runp3_v2(self):
        """test wrapper for runp3. Empty fusion list"""
        fusions = []
        res1 = starseqr_utils.run_primer3.wrap_runp3('chr1:45268528:+:chr4:107152937:-:0:2', fusions)
        assert(res1 == ())

if __name__ == '__main__':
    unittest.main()