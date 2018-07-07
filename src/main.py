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
        q2 = search_g_and_a(q1)
        return q2


def search_g_and_a(q):
    """
    groupId 和 artifactId 同时作为查询条件
    :param q: 查询表达式
    :return: 查询表达式
    """
    if q.startswith('g:') or q.startswith('a:') or q.startswith('m:') or (q.find(':') < 0):
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
    }
    q = q[2:]
    if q in q_map:
        return q_map[q]


def search_any():
    url = 'http://search.maven.org/solrsearch/select'
    q = fix_q(wf.args[0].strip())

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
    for it in items:
        if 'latestVersion' in it:
            v = it['latestVersion']
        else:
            v = it['v']
        des = it['id'] + ':' + v + ':' + it['p']
        pom_xml = '''
        <dependency>
            <groupId>%s</groupId>
            <artifactId>%s</artifactId>
            <version>%s</version>
        </dependency>
        ''' % (it['g'], it['a'], v)
        icns = ICON_WEB
        if 'jar' == it['p']:
            icns = 'icns/java.icns'
        elif 'pom' == it['p']:
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
        wf.add_item(title=des,
                    subtitle=subtitle,
                    arg=pom_xml,
                    valid=True,
                    icon=icns)

    wf.send_feedback()


if __name__ == u'__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
