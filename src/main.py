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
import time, datetime

from workflow import Workflow3, ICON_WEB, web


def fix_q(q):
    """
    填充分号
    :param q: 查询表达式
    :return: 查询表达式
    """
    if ((not q.startswith('a:"')) and q.startswith('a:')) \
            or (not q.startswith('g:"')) and q.startswith('g:'):
        q = q[:2] + '"' + q[2:]
        if ' ' in q:
            return q.replace(' ', '" ', 1)
        else:
            return q + '"'
    else:
        q1 = search_m(q)
        if q1 is None:
            return ""
        q2 = search_g_and_a(q1)
        return q2


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


def search_g_and_a(q):
    """
    groupId 和 artifactId 同时作为查询条件
    :param q: 查询表达式
    :return: 查询表达式
    """
    if q.startswith('g:') \
            or q.startswith('a:') \
            or q.startswith('m:') \
            or q.startswith('tags:') \
            or q.startswith('c:') \
            or q.startswith('fc:') \
            or q.startswith('1:') \
            or (q.find(':') < 0):
        return q
    g_and_a = q.split(':', 1)
    return 'g:"%s"+AND+a:"%s"' % (g_and_a[0], g_and_a[1])


def search_m(q):
    """
    自定义的常用简短查询
    :param q: 查询表达式
    :return: 查询表达式
    """
    if not q.startswith('m:'):
        return q
    q_map = {
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
    q = q[2:]
    if q in q_map:
        return q_map[q]


def search_any():
    url = 'http://search.maven.org/solrsearch/select'
    q = fix_q(wf.args[0].strip())
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
    items = wf.cached_data(wf.args[0].strip(), search_any, max_age=60 * 3)
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
