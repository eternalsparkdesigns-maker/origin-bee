"""Content tests for this game. Run from the repo root:  python3 -m unittest discover -s edit -v"""
import json, random, re, sys, unittest, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'edit'))
from bundle import enc, split

def js_list(src, name):
    body = re.search(name + r' = \[(.*?)\];', src, re.S).group(1)
    return re.findall(r"'([A-Z]+)'", body)

SRC = (ROOT / 'edit/template.html').read_text()

class Bee(unittest.TestCase):
    def setUp(self):
        self.words = js_list(SRC, 'ALL_WORDS')
        self.letters = js_list(SRC, 'ALL_LETTERS')
        self.outer = js_list(SRC, 'OUTER_INIT')
        self.center = re.search(r"CENTER = '([A-Z])'", SRC).group(1)

    def test_letter_set(self):
        self.assertEqual(sorted(self.letters), sorted(set('STRENGTH')))
        self.assertEqual(len(self.letters), 7)
        self.assertEqual(sorted(self.outer + [self.center]), sorted(self.letters))

    def test_every_word_is_playable(self):
        for w in self.words:
            self.assertGreaterEqual(len(w), 4, w)
            self.assertIn(self.center, w, w)
            self.assertLessEqual(set(w), set(self.letters), w)

    def test_no_duplicates(self):
        self.assertEqual(len(self.words), len(set(self.words)))

    def test_pangrams(self):
        p = [w for w in self.words if len(set(w)) == 7]
        self.assertIn('STRENGTH', p)
        self.assertEqual(set(p), {'STRENGTH','STRENGTHS','STRENGTHEN','STRENGTHENS','STRENGTHENER'})

    def test_footer_matches_letters(self):
        m = re.search(r'Letters: ([A-Z ·]+)\+', SRC).group(1)
        self.assertEqual(m.replace('·', '').split(), self.outer)

    def test_ranks_ascending_and_end_at_full(self):
        pcts = [float(x) for x in re.findall(r'pct: ([0-9.]+)', SRC)]
        self.assertEqual(pcts, sorted(pcts)); self.assertEqual(pcts[0], 0); self.assertEqual(pcts[-1], 1.0)

    def test_old_puzzle_gone(self):
        self.assertNotIn('THERAPY', self.words)
        self.assertNotIn('Pelvic Floor Spelling Bee', SRC)
class Bundle(unittest.TestCase):
    def test_index_matches_template(self):
        s = (ROOT / 'index.html').read_text(); m = split(s)
        self.assertEqual(json.loads(m.group(2)), SRC)
        self.assertEqual(enc(json.loads(m.group(2))), m.group(2))  # re-pack is byte-exact
        self.assertNotIn('</script', m.group(2))  # must not close the island early

if __name__ == '__main__':
    unittest.main()
