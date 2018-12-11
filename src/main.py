# -* - coding: UTF-8 -* -
# Copyright (C) 2018 cn-src <public@javaer.cn>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import time
import hashlib

from workflow import Workflow3, web


def fix_query(query):
    """
    填充分号
    :param query: 查询表达式
    :return: 查询表达式
    """
    if ((not query.startswith('a:"')) and query.startswith('a:')) \
            or (not query.startswith('g:"')) and query.startswith('g:'):
        query = query[:2] + '"' + query[2:]
        if ' ' in query:
            return query.replace(' ', '" ', 1)
        else:
            return query + '"'

    (has, q_xml) = query_from_xml(query)
    if has:
        return q_xml

    (has, q_m) = query_from_m(query)
    if has:
        return q_m

    (has, q_ga) = query_from_g_and_a(query)
    if has:
        return q_ga

    return query


def fix_length(des):
    if len(des) <= 50 or des.find(':') < 0:
        return des
    s1 = des.split(':', 1)
    if s1[0].find('.') < 0:
        return des
    s1s = s1[0].split('.')
    r_s = ""
    for s in s1s:
        r_s = r_s + s[:1] + '.'
    if r_s.endswith('.'):
        r_s = r_s[:-1]
    return r_s + ':' + s1[1]


def query_from_xml(query):
    g_start = query.find('groupId>')
    g_end = query.find('</groupId>')
    g_id = None
    if g_start > -1 and g_end > -1:
        g_id = query[g_start + len('groupId>'): g_end]

    a_start = query.find('artifactId>')
    a_end = query.find('</artifactId>')
    a_id = None
    if a_start > -1 and a_end > -1:
        a_id = query[a_start + len('artifactId>'): a_end]

    if g_id and a_id:
        return True, 'g:"%s"+AND+a:"%s"' % (g_id, a_id)

    if g_id:
        return True, 'g:"%s"' % g_id
    elif a_id:
        return True, 'a:"%s"' % a_id

    return False, None


def query_from_g_and_a(query):
    """
    groupId 和 artifactId 同时作为查询条件
    :param query: 查询表达式
    :return: 查询表达式
    """
    if query.startswith('g:') \
            or query.startswith('a:') \
            or query.startswith('m:') \
            or query.startswith('tags:') \
            or query.startswith('c:') \
            or query.startswith('fc:') \
            or query.startswith('1:') \
            or (query.find(':') < 0):
        return False, query
    g_and_a = query.split(':', 1)
    return True, 'g:"%s"+AND+a:"%s"' % (g_and_a[0], g_and_a[1])


def query_from_m(query):
    """
    自定义的常用简短查询
    :param query: 查询表达式
    :return: 查询表达式
    """
    if not query.startswith('m:'):
        return False, query

    q_mapping = {
        'poi': 'g:"org.apache.poi"',
        'jodd': 'g:"org.jodd"',
        'h2': 'g:"com.h2database"',
        'querydsl': 'g:"com.querydsl"',
        'netty': 'g:"io.netty"',
        'commons': 'g:"org.apache.commons"',
        'lang': 'g:"org.apache.commons"+AND+a:"commons-lang3"',
        'guava': 'g:"com.google.guava"+AND+a:"guava"',
        'http': 'g:"org.apache.httpcomponents"',
        'groovy': 'g:"org.codehaus.groovy"',
        'jooq': 'g:"org.jooq"',
        'lombok': 'g:"org.projectlombok"',
        'slf4j': 'g:"org.slf4j"',
        'spring': 'g:"org.springframework"',
        'springboot': 'g:"org.springframework.boot"',
    }
    query = query[2:]
    if query in q_mapping:
        return True, q_mapping[query]

    return False, None


def search_any():
    url = 'http://search.maven.org/solrsearch/select'
    q = fix_query(wf.args[0].strip())
    if q is None or len(q) <= 0:
        return []
        # 不能使用 web.get 的参数形式 Maven 官方 API 仅仅只是对双引号做了 url 编码
    params = '?q=%s&rows=20&wt=json' % q.replace('"', '%22')
    if q.find('"+AND+a:"') > -1:
        params = params + '&core=gav'

    r = web.get(url + params)

    r.raise_for_status()

    result = r.json()
    items = result['response']['docs']
    items.sort(key=lambda it: long(it['timestamp']), reverse=True)
    return items


def main(wf):
    md5 = hashlib.md5()
    md5.update(wf.args[0].strip().encode("utf-8"))
    token = md5.hexdigest()

    items = wf.cached_data(token, search_any, max_age=60 * 3)
    if items is None or len(items) == 0:
        items = search_any()
    has_des = []
    for it in items:
        if 'latestVersion' in it:
            v = it['latestVersion']
        else:
            v = it['v']
        des = it['g'] + ':' + it['a'] + ':' + v
        pom_xml = '''
        <dependency>
            <groupId>%s</groupId>
            <artifactId>%s</artifactId>
            <version>%s</version>
        </dependency>
        ''' % (it['g'], it['a'], v)
        if '.jar' in it['ec']:
            icns = 'icns/java.icns'
        else:
            icns = 'icns/xml.icns'
        ecs = ''
        for ec in it['ec']:
            ecs = ecs + ec[1:] + ', '
        if ecs.endswith(', '):
            ecs = ecs[:-2]
        update_time = time.strftime("%Y-%m-%d", time.localtime(long(it['timestamp']) / 1000))
        if 'versionCount' in it:
            subtitle = 'all:%s updated:%s ec:%s' % (it['versionCount'], update_time, ecs)
        else:
            subtitle = 'updated:%s ec:%s' % (update_time, ecs)
        if des not in has_des:
            has_des.append(des)
            wf.add_item(title=fix_length(des),
                        subtitle=subtitle,
                        arg=pom_xml,
                        valid=True,
                        icon=icns)

    wf.send_feedback()


if __name__ == u'__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
