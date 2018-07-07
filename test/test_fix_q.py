# -* - coding: UTF-8 -* -
from unittest import TestCase

from main import fix_q


class TestFix_q(TestCase):
    def test_fix_q(self):
        self.assertEquals(fix_q('a:demo'), 'a:"demo"')
        self.assertEquals(fix_q('a:"demo"'), 'a:"demo"')
        self.assertEquals(fix_q('g:demo'), 'g:"demo"')
        self.assertEquals(fix_q('g:"demo"'), 'g:"demo"')
        self.assertEquals(fix_q('m:poi'), 'g:"org.apache.poi"')
        #  不正确的写法，保持原样
        self.assertEquals(fix_q('a:"demo'), 'a:"demo')
