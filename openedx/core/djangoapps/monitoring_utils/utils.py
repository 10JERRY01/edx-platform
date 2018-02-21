"""
Monitoring utilities which aren't used by the application by default, but can
be used as needed to troubleshoot problems.
"""
import os
from StringIO import StringIO
import logging

import objgraph
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile

log = logging.getLogger(__name__)

indices = {}

DUMP_DIR = u'memory_graphs'
MAX_CONSOLE_ROWS = 30
MAX_GRAPHED_OBJECT_TYPES = 20
REFS_DEPTH = 3
BACK_REFS_DEPTH = 8
MAX_OBJECTS_PER_TYPE = 5
IGNORED_TYPES = ('set',)
GRAPH_TYPES = {'cell', 'dict', 'function', 'instancemethod', 'list', 'set', 'tuple', 'type', 'weakref'}


def show_memory_leaks(
        label=u'memory_leaks',
        dump_dir=DUMP_DIR,
        max_console_rows=MAX_CONSOLE_ROWS,
        max_graphed_object_types=MAX_GRAPHED_OBJECT_TYPES,
        refs_depth=REFS_DEPTH,
        back_refs_depth=BACK_REFS_DEPTH,
        max_objects_per_type=MAX_OBJECTS_PER_TYPE,
        ignored_types=IGNORED_TYPES,
        show_graphs=True):
    """
    Call this function to get data about memory leaks; what objects are being
    leaked, where did they come from, and what do they contain?  The leaks
    are measured from the last call to ``objgraph.get_new_ids()`` (which is
    called within this function).  Some data is printed to stdout, and more
    details are available in graphs stored in ``dump_dir``.  Subsequent calls
    with the same label are indicated by an increasing index in the filename.

    Args:
        label (unicode): The start of the filename for each graph
        dump_dir (unicode): The directory (under the default storage backend)
            in which graphs are dumped.
        max_console_rows (int): The max number of object types for which to
            show data on the console
        max_graphed_object_types (int): The max number of object types for
            which to generate reference graphs
        refs_depth (int): Maximum depth of forward reference graphs
        back_refs_depth (int): Maximum depth of backward reference graphs
        max_objects_per_type (int): Max number of objects per type to use as
            starting points in the reference graphs
        ignored_types (iterable): Object type names for which graphs should
            not be generated even if the new object count is high.  "set" is
            ignored by default because many sets are created in the course of
            tracking the number of new objects of each type.
    """
    new_objects_output = StringIO()
    new_ids = objgraph.get_new_ids(limit=max_console_rows, sortby='old', file=new_objects_output)
    new_objects_text = new_objects_output.getvalue()
    log.info('\n' + new_objects_text)
    index = indices.setdefault(label, 1)
    indices[label] += 1
    pid = os.getpid()

    tmp_storage = FileSystemStorage(location='/tmp')
    path = u'{dir}/{label}_{pid}_{index}.txt'.format(dir=dump_dir, label=label, pid=pid, index=index)
    tmp_storage.save(path, ContentFile(new_objects_text))

    if not show_graphs:
        return
    sorted_by_count = sorted(new_ids.items(), key=lambda entry: len(entry[1]), reverse=True)

    for item in sorted_by_count:
        type_name = item[0]
        object_ids = new_ids[type_name]
        if type_name not in GRAPH_TYPES or len(object_ids) == 0:
            continue
        objects = objgraph.at_addrs(object_ids)[:max_objects_per_type]

        backrefs_dot = StringIO()
        refs_dot = StringIO()

        objgraph.show_backrefs(objects, max_depth=back_refs_depth, output=backrefs_dot)
        objgraph.show_refs(objects, max_depth=refs_depth, output=refs_dot)
        data = {'dir': dump_dir, 'label': label, 'pid': pid, 'index': index, 'type_name': type_name}

        path = u'{dir}/{label}_{pid}_{index}_{type_name}_backrefs.dot'.format(**data)
        tmp_storage.save(path, ContentFile(backrefs_dot.getvalue()))
        log.info(u'Graph generated at %s', os.path.join(tmp_storage.location, path))

        # path = u'{dir}/{label}_{pid}_{index}_{type_name}_refs.dot'.format(**data)
        # tmp_storage.save(path, ContentFile(refs_dot.getvalue()))
        # log.info(u'Graph generated at %s', os.path.join(tmp_storage.location, path))
