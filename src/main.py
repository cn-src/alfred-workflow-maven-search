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
from workflow import Workflow3, ICON_WEB, web


def fix_q(q):
    if ((not q.startswith('a:"')) and q.startswith('a:')) or (not q.startswith('g:"')) and q.startswith('g:'):
        q = q[:2] + '"' + q[2:]
        if ' ' in q:
            return q.replace(' ', '" ', 1)
        else:
            return q + '"'
    else:
        return q


def search_any():
    url = 'http://search.maven.org/solrsearch/select'
    q = fix_q(wf.args[0].strip())

    params = {'q': q, 'rows': 10, 'wt': 'json'}
    r = web.get(url, params)

    r.raise_for_status()

    result = r.json()
    items = result['response']['docs']
    items.sort(key=lambda it: long(it['timestamp']), reverse=True)
    return items


def main(wf):
    items = wf.cached_data(wf.args[0].strip(), search_any, max_age=60 * 3)
    for it in items:
        des = it['id'] + ':' + it['latestVersion'] + ':' + it['p']
        pom_xml = '''
        <dependency>
            <groupId>%s</groupId>
            <artifactId>%s</artifactId>
            <version>%s</version>
        </dependency>
        ''' % (it['g'], it['a'], it['latestVersion'])
        icns = ICON_WEB
        if 'jar' == it['p']:
            icns = 'icns/java.icns'
        elif 'pom' == it['p']:
            icns = 'icns/xml.icns'
        wf.add_item(title=des,
                    subtitle='maven',
                    arg=pom_xml,
                    valid=True,
                    icon=icns)

    wf.send_feedback()


if __name__ == u'__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
