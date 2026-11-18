import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from refresh import compare

class Comparison(unittest.TestCase):
    def test_add_remove_change_and_unchanged(self):
        old={'x':['1'],'y':['2'],'z':['3']}
        new={'x':['4'],'y':['2'],'a':['5']}
        result=compare(old,new,'2024-01-02','2024-01-04')
        self.assertEqual([row[2] for row in result],['a','x','z'])
        self.assertEqual(result[0][3],None)
        self.assertEqual(result[-1][4],None)
        self.assertEqual(compare(new,new,'a','b'),[])
