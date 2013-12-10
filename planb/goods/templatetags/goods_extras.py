from django import template
from collections import defaultdict

register = template.Library()

class TreeNode(template.Node):
    def __init__(self, tree, node_list):
        self.tree = tree
        self.node_list = node_list

    def render(self, context):
        tree = self.tree.resolve(context)

        # итератор по входному списку, выдающий пары вида 
        # (элемент списка, его подсписок), причём одного из элемента пары
        # может не быть
        def pairs(items):

            # внутренний "грязный" генератор, выдающий пары, где могут быть
            # бесполезные: с обоими пустыми head и tail
            def dirty(items):
                items = iter(items)
                head = None
                try:
                    while True:
                        item = items.__next__()
                        if isinstance(item, (list, tuple)):
                            yield head, item
                            head = None
                        else:
                            yield head, None
                            head = item
                except StopIteration:
                    yield head, None

            # фильтр над грязным генератором, удаляющий бесполезные пары
            return ((h, t) for h, t in dirty(items) if h or t)

        # выводит элемент списка с подсписком
        # для подсписка рекурсивно вызывается render_items
        def render_item(item, sub_items, level):
            #возвращает \n и level штук \t
            def n_tab(level):
                return '\n'+''.join('\t' for i in range(level))
            
            return ''.join([
                n_tab(level),
                '<li>',
                (item and self.node_list.render(template.Context({'item': item, 'level': level})) or '').strip(),
                (sub_items and n_tab(level)+'<ul>%s' % ''.join(render_items(sub_items, level+1))+n_tab(level)+'</ul>' or ''),
                '</li>'
            ])

        # вывод списка элементов
        def render_items(items, level):
            return ''.join(render_item(h, t, level) for h, t in pairs(items))

        return render_items(tree, 0)

@register.tag
def tree(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%s" takes one argument: tree-structured list' % bits[0])
    node_list = parser.parse('end' + bits[0])
    parser.delete_first_token()
    return TreeNode(parser.compile_filter(bits[1]), node_list)

@register.filter
def astree(items, attribute_list):
    #attribute_list - 2 атрибута: свой Id и parentId, разделённые запятой
    Id_attribute = attribute_list.replace(' ','').split(',')[0]
    parId_attribute = attribute_list.replace(' ','').split(',')[1]

    # перевод списка в dict: parent -> список детей
    parent_map = defaultdict(list)
    for item in items:
        parent_map[getattr(item, parId_attribute)].append(item)

    # рекурсивный вывод детей одного parent'а
    def tree_level(parent):
        for item in parent_map[parent]:
            yield item
            sub_items = list(tree_level(getattr(item, Id_attribute)))
            if sub_items:
                yield sub_items

    return list(tree_level(""))
