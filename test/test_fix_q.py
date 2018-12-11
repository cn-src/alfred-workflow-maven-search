# -* - coding: UTF-8 -* -
from unittest import TestCase

from main import fix_query, query_from_xml


class TestFix_q(TestCase):
    def test_fix_q(self):
        self.assertEquals(fix_query('a:demo'), 'a:"demo"')
        self.assertEquals(fix_query('a:"demo"'), 'a:"demo"')
        self.assertEquals(fix_query('g:demo'), 'g:"demo"')
        self.assertEquals(fix_query('g:"demo"'), 'g:"demo"')
        self.assertEquals(fix_query('m:poi'), 'g:"org.apache.poi"')
        #  不正确的写法，保持原样
        self.assertEquals(fix_query('a:"demo'), 'a:"demo')

    def test_fix_from_xml(self):
        self.assertEquals(query_from_xml('<groupId>org.hibernate</groupId>'), 'g:org.hibernate')
        self.assertEquals(query_from_xml('<artifactId>hibernate-java8</artifactId>'), 'a:hibernate-java8')
        self.assertEquals(query_from_xml('''
        <dependency>
            <groupId>org.hibernate</groupId>
            <artifactId>hibernate-java8</artifactId>
        </dependency>
        '''), 'org.hibernate:hibernate-java8')
