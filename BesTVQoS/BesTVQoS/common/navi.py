# coding:utf-8

from HTMLParser import HTMLParser


class NaviItem():

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.children = []

    def append_child(self, child):
        assert isinstance(child, NaviItem)
        self.children.append(child)

    def find(self, target_url=None):
        path = []
        found = False
        if self.url == target_url:
            path.append(self)
            found = True
        elif self.children:
            for child in self.children:
                (found, sub_path) = child.find(target_url)
                if found:
                    path.append(self)
                    path.extend(sub_path)
                    break

        return found, path


class NaviTreeParser(HTMLParser):

    def __init__(self):
        self.naviTree = []
        self.href = 0
        self.url = ''
        self.deep = -1
        self.url_prefix = ['/navi/m', '/m']

        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'ul':
            self.deep += 1

        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.href = 1
                    self.url = self.url_prefix[self.deep] + value

    def handle_data(self, data):
        if self.href:
            item = NaviItem(data, self.url)
            if self.deep == 0:
                self.naviTree.append(item)
            elif self.deep == 1:
                self.naviTree[-1].append_child(item)
            else:
                pass

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.deep -= 1

        if tag == 'a':
            self.href = 0

    def get_navi(self):
        return self.naviTree

    def getresult(self):
        for value in self.naviTree:
            print value.name, value.url
            if value.children:
                for child in value.children:
                    print "\t", child.name, child.url


class Navi(object):

    def __init__(self):
        self.navi = None

        html = open("common/templates/navi_menu.html").read()
        parser = NaviTreeParser()
        parser.feed(html)
        self.navi = parser.get_navi()
        parser.close()

    def get_sub_items(self, root=None):
        ret = self.navi
        if root:
            if type(root) == type(u''):
                root = root.encode('utf-8')

            for item in self.navi:
                if item.name == root or item.url == root:
                    ret = item.children

        return ret

    def get_path(self, target_url):
        for item in self.navi:
            (found, path) = item.find(target_url)
            if found:
                return path
