from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
import random
import string
import copy
import types
import pandas

from . import pygraphistry
from . import util


class Plotter(object):
    """Graph plotting class.

    Created using ``Graphistry.bind()``.

    Chained calls successively add data and visual encodings, and end with a plot call.

    To streamline reuse and replayable notebooks, Plotter manipulations are immutable. Each chained call returns a new instance that derives from the previous one. The old plotter or the new one can then be used to create different graphs.

    The class supports convenience methods for mixing calls across Pandas, NetworkX, and IGraph.
    """


    _defaultNodeId = '__nodeid__'

    def __init__(self):
        # Bindings
        self._edges = None
        self._nodes = None
        self._source = None
        self._destination = None
        self._node = None
        self._edge_title = None
        self._edge_label = None
        self._edge_color = None
        self._edge_weight = None
        self._point_title = None
        self._point_label = None
        self._point_color = None
        self._point_size = None
        # Settings
        self._height = 500
        self._url_params = {'info': 'true'}

    def __repr__(self):
        bnds = ['edges', 'nodes', 'source', 'destination', 'node', 'edge_title',
                'edge_label', 'edge_color', 'edge_weight', 'point_title',
                'point_label', 'point_color', 'point_size']
        stgs = ['height', 'url_params']

        rep = {'bindings': dict([(f, getattr(self, '_' + f)) for f in bnds]),
               'settings': dict([(f, getattr(self, '_' + f)) for f in stgs])}
        if util.in_ipython():
            from IPython.lib.pretty import pretty
            return pretty(rep)
        else:
            return str(rep)

    def bind(self, source=None, destination=None, node=None,
             edge_title=None, edge_label=None, edge_color=None, edge_weight=None,
             point_title=None, point_label=None, point_color=None, point_size=None):
        """Relate data attributes to graph structure and visual representation.

        To facilitate reuse and replayable notebooks, the binding call is chainable. Invocation does not effect the old binding: it instead returns a new Plotter instance with the new bindings added to the existing ones. Both the old and new bindings can then be used for different graphs.


        :param source: Attribute containing an edge's source ID
        :type source: String.

        :param destination: Attribute containing an edge's destination ID
        :type destination: String.

        :param node: Attribute containing a node's ID
        :type node: String.

        :param edge_title: Attribute overriding edge's minimized label text. By default, the edge source and destination is used.
        :type edge_title: HtmlString.

        :param edge_label: Attribute overriding edge's expanded label text. By default, scrollable list of attribute/value mappings.
        :type edge_label: HtmlString.

        :param edge_color: Attribute overriding edge's color. `See palette definitions <https://github.com/graphistry/pygraphistry/blob/master/graphistry.com/palette.html>`_ for values. Based on Color Brewer.
        :type edge_color: String.

        :param edge_weight: Attribute overriding edge weight. Default is 1. Advanced layout controls will relayout edges based on this value.
        :type edge_weight: String.

        :param point_title: Attribute overriding node's minimized label text. By default, the node ID is used.
        :type point_title: HtmlString.

        :param point_label: Attribute overriding node's expanded label text. By default, scrollable list of attribute/value mappings.
        :type point_label: HtmlString.

        :param point_color: Attribute overriding node's color. `See palette definitions <https://github.com/graphistry/pygraphistry/blob/master/graphistry.com/palette.html>`_ for values. Based on Color Brewer.
        :type point_color: Integer.

        :param point_size: Attribute overriding node's size. By default, uses the node degree. The visualization will normalize point sizes and adjust dynamically using semantic zoom.
        :type point_size: HtmlString.

        :returns: Plotter.
        :rtype: Plotter.

        **Example: Minimal**
            ::

                import graphistry
                g = graphistry.bind()
                g = g.bind(source='src', destination='dst')

        **Example: Node colors**
            ::

                import graphistry
                g = graphistry.bind()
                g = g.bind(source='src', destination='dst',
                           node='id', point_color='color')

        **Example: Chaining**
            ::

                import graphistry
                g = graphistry.bind(source='src', destination='dst', node='id')

                g1 = g.bind(point_color='color1', point_size='size1')

                g.bind(point_color='color1b')

                g2a = g1.bind(point_color='color2a')
                g2b = g1.bind(point_color='color2b', point_size='size2b')

                g3a = g2a.bind(point_size='size3a')
                g3b = g2b.bind(point_size='size3b')

        In the above **Chaining** example, all bindings use src/dst/id. Colors and sizes bind to:
            ::

                g: default/default
                g1: color1/size1
                g2a: color2a/size1
                g2b: color2b/size2b
                g3a: color2a/size3a
                g3b: color2b/size3b


        """
        res = copy.copy(self)
        res._source = source or self._source
        res._destination = destination or self._destination
        res._node = node or self._node

        res._edge_title = edge_title or self._edge_title
        res._edge_label = edge_label or self._edge_label
        res._edge_color = edge_color or self._edge_color
        res._edge_weight = edge_weight or self._edge_weight

        res._point_title = point_title or self._point_title
        res._point_label = point_label or self._point_label
        res._point_color = point_color or self._point_color
        res._point_size = point_size or self._point_size
        return res

    def nodes(self, nodes):
        """Specify the set of nodes and associated data.

        Must include any nodes referenced in the edge list.

        :param nodes: Nodes and their attributes.
        :type point_size: Pandas dataframe

        :returns: Plotter.
        :rtype: Plotter.

        **Example**
            ::

                import graphistry

                es = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                g = graphistry
                    .bind(source='src', destination='dst')
                    .edges(es)

                vs = pandas.DataFrame({'v': [0,1,2], 'lbl': ['a', 'b', 'c']})
                g = g.bind(node='v').nodes(vs)

                g.plot()

        """


        res = copy.copy(self)
        res._nodes = nodes
        return res

    def edges(self, edges):
        """Specify edge list data and associated edge attribute values.

        :param edges: Edges and their attributes.
        :type point_size: Pandas dataframe, NetworkX graph, or IGraph graph.

        :returns: Plotter.
        :rtype: Plotter.

        **Example**
            ::

                import graphistry
                df = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                graphistry
                    .bind(source='src', destination='dst')
                    .edges(df)
                    .plot()

        """

        res = copy.copy(self)
        res._edges = edges
        return res

    def graph(self, ig):
        """Specify the node and edge data.

        :param ig: Graph with node and edge attributes.
        :type ig: NetworkX graph or an IGraph graph.

        :returns: Plotter.
        :rtype: Plotter.
        """

        res = copy.copy(self)
        res._edges = ig
        res._nodes = None
        return res

    def settings(self, height=None, url_params={}):
        """Specify iframe height and add URL parameter dictionary.

        The library takes care of URI component encoding for the dictionary.

        :param height: Height in pixels.
        :type height: Integer.

        :param url_params: Dictionary of querystring parameters to append to the URL.
        :type url_params: Dictionary
        """

        res = copy.copy(self)
        res._height = height or self._height
        res._url_params = dict(self._url_params, **url_params)
        return res

    def plot(self, graph=None, nodes=None):
        """Upload data to the Graphistry server and show as an iframe of it.

        Uses the currently bound schema structure and visual encodings. Optional parameters override the current bindings.

        When used in a notebook environment, will also show an iframe of the visualization.

        :param graph: Edge table or graph.
        :type graph: Pandas dataframe, NetworkX graph, or IGraph graph.

        :param nodes: Nodes table.
        :type nodes: Pandas dataframe.

        **Example: Simple**
            ::

                import graphistry
                es = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                graphistry
                    .bind(source='src', destination='dst')
                    .edges(es)
                    .plot()

        **Example: Shorthand**
            ::

                import graphistry
                es = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                graphistry
                    .bind(source='src', destination='dst')
                    .plot(es)


        """
        if graph is None:
            if self._edges is None:
                util.error('Graph/edges must be specified.')
            g = self._edges
        else:
            g = graph
        n = self._nodes if nodes is None else nodes

        self._check_mandatory_bindings(not isinstance(n, type(None)))
        PyG = pygraphistry.PyGraphistry

        if (PyG.api == 1):
            dataset = self._plot_dispatch(g, n, 'json')
            info = PyG._etl1(dataset)
        elif (PyG.api == 2):
            dataset = self._plot_dispatch(g, n, 'vgraph')
            info = PyG._etl2(dataset['encodings'], dataset['vgraph'])

        viz_url = PyG._viz_url(info['name'], info['viztoken'], self._url_params)

        if util.in_ipython() is True:
            from IPython.core.display import HTML
            return HTML(util.make_iframe(viz_url, self._height, PyG._protocol))
        else:
            print('Url: http://%s' % viz_url)
            import webbrowser
            webbrowser.open(viz_url)
            return self

    def pandas2igraph(self, edges, directed=True):
        """Convert a pandas edge dataframe to an IGraph graph.

        Uses current bindings. Defaults to treating edges as directed.

        **Example**
            ::

                import graphistry
                g = graphistry.bind()

                es = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                g = g.bind(source='src', destination='dst')

                ig = g.pandas2igraph(es)
                ig.vs['community'] = ig.community_infomap().membership
                g.bind(point_color='community').plot(ig)
        """


        import igraph
        self._check_mandatory_bindings(False)
        self._check_bound_attribs(edges, ['source', 'destination'], 'Edge')
        if self._node is None:
            util.warn('"node" is unbound, automatically binding it to "%s".' % Plotter._defaultNodeId)

        self._node = self._node or Plotter._defaultNodeId
        eattribs = edges.columns.values.tolist()
        eattribs.remove(self._source)
        eattribs.remove(self._destination)
        cols = [self._source, self._destination] + eattribs
        etuples = [tuple(x) for x in edges[cols].values]
        return igraph.Graph.TupleList(etuples, directed=directed, edge_attrs=eattribs,
                                      vertex_name_attr=self._node)

    def igraph2pandas(self, ig):
        """Under current bindings, transform an IGraph into a pandas edges dataframe and a nodes dataframe.

        **Example**
            ::

                import graphistry
                g = graphistry.bind()

                es = pandas.DataFrame({'src': [0,1,2], 'dst': [1,2,0]})
                g = g.bind(source='src', destination='dst').edges(es)

                ig = g.pandas2igraph(es)
                ig.vs['community'] = ig.community_infomap().membership

                (es2, vs2) = g.igraph2pandas(ig)
                g.nodes(vs2).bind(point_color='community').plot()
        """

        def get_edgelist(ig):
            idmap = dict(enumerate(ig.vs[self._node]))
            for e in ig.es:
                t = e.tuple
                yield dict({self._source: idmap[t[0]], self._destination: idmap[t[1]]},
                            **e.attributes())

        self._check_mandatory_bindings(False)
        if self._node is None:
            util.warn('"node" is unbound, automatically binding it to "%s".' % Plotter._defaultNodeId)
            ig.vs[Plotter._defaultNodeId] = [v.index for v in ig.vs]
            self._node = Plotter._defaultNodeId
        elif self._node not in ig.vs.attributes():
            util.error('Vertex attribute "%s" bound to "node" does not exist.' % self._node)

        edata = get_edgelist(ig)
        ndata = [v.attributes() for v in ig.vs]
        nodes = pandas.DataFrame(ndata, columns=ig.vs.attributes())
        cols = [self._source, self._destination] + ig.es.attributes()
        edges = pandas.DataFrame(edata, columns=cols)
        return (edges, nodes)

    def networkx2pandas(self, g):
        def get_nodelist(g):
            for n in g.nodes(data=True):
                yield dict({self._node: n[0]}, **n[1])
        def get_edgelist(g):
            for e in g.edges(data=True):
                yield dict({self._source: e[0], self._destination: e[1]}, **e[2])

        self._check_mandatory_bindings(False)
        vattribs = g.nodes(data=True)[0][1] if g.number_of_nodes() > 0 else []
        if self._node is None:
            util.warn('"node" is unbound, automatically binding it to "%s".' % Plotter._defaultNodeId)
        elif self._node in vattribs:
            util.error('Vertex attribute "%s" already exists.' % self._node)

        self._node = self._node or Plotter._defaultNodeId
        nodes = pandas.DataFrame(get_nodelist(g))
        edges = pandas.DataFrame(get_edgelist(g))
        return (edges, nodes)

    def _check_mandatory_bindings(self, node_required):
        if self._source is None or self._destination is None:
            util.error('Both "source" and "destination" must be bound before plotting.')
        if node_required and self._node is None:
            util.error('Node identifier must be bound when using node dataframe.')

    def _check_bound_attribs(self, df, attribs, typ):
        cols = df.columns.values.tolist()
        for a in attribs:
            b = getattr(self, '_' + a)
            if b not in cols:
                util.error('%s attribute "%s" bound to "%s" does not exist.' % (typ, a, b))

    def _plot_dispatch(self, graph, nodes, mode='json'):
        if isinstance(graph, pandas.core.frame.DataFrame):
            return self._make_dataset(graph, nodes, mode)

        try:
            import igraph
            if isinstance(graph, igraph.Graph):
                (e, n) = self.igraph2pandas(graph)
                return self._make_dataset(e, n, mode)
        except ImportError:
            pass

        try:
            import networkx
            if isinstance(graph, networkx.classes.graph.Graph) or \
               isinstance(graph, networkx.classes.digraph.DiGraph) or \
               isinstance(graph, networkx.classes.multigraph.MultiGraph) or \
               isinstance(graph, networkx.classes.multidigraph.MultiDiGraph):
                (e, n) = self.networkx2pandas(graph)
                return self._make_dataset(e, n, mode)
        except ImportError:
            pass

        util.error('Expected Pandas dataframe(s) or Igraph/NetworkX graph.')

    def _sanitize_dataset(self, edges, nodes, nodeid):
        self._check_bound_attribs(edges, ['source', 'destination'], 'Edge')
        elist = edges.reset_index(drop=True).dropna(subset=[self._source, self._destination])
        if nodes is None:
            nodes = pandas.DataFrame()
            nodes[nodeid] = pandas.concat([edges[self._source], edges[self._destination]],
                                           ignore_index=True).drop_duplicates()
        else:
            self._check_bound_attribs(nodes, ['node'], 'Vertex')
        nlist = nodes.reset_index(drop=True).dropna(subset=[nodeid])
        return (elist, nlist)

    def _check_dataset_size(self, elist, nlist):
        edge_count = len(elist.index)
        node_count = len(nlist.index)
        graph_size = edge_count + node_count
        if edge_count > 8e6:
            util.error('Maximum number of edges (8M) exceeded: %d.' % edge_count)
        if node_count > 8e6:
            util.error('Maximum number of nodes (8M) exceeded: %d.' % node_count)
        if graph_size > 1e6:
            util.warn('Large graph: |nodes| + |edges| = %d. Layout/rendering might be slow.' % graph_size)

    def _bind_attributes_v1(self, edges, nodes):
        def bind(df, pbname, attrib, default=None):
            bound = getattr(self, attrib)
            if bound:
                if bound in df.columns.tolist():
                    df[pbname] = df[bound]
                else:
                    util.warn('Attribute "%s" bound to %s does not exist.' % (bound, attrib))
            elif default:
                df[pbname] = df[default]


        nodeid = self._node or Plotter._defaultNodeId
        (elist, nlist) = self._sanitize_dataset(edges, nodes, nodeid)
        self._check_dataset_size(elist, nlist)

        bind(elist, 'edgeColor', '_edge_color')
        bind(elist, 'edgeLabel', '_edge_label')
        bind(elist, 'edgeTitle', '_edge_title')
        bind(elist, 'edgeWeight', '_edge_weight')
        bind(nlist, 'pointColor', '_point_color')
        bind(nlist, 'pointLabel', '_point_label')
        bind(nlist, 'pointTitle', '_point_title', nodeid)
        bind(nlist, 'pointSize', '_point_size')
        return (elist, nlist)

    def _bind_attributes_v2(self, edges, nodes):
        def bind(enc, df, pbname, attrib, default=None):
            bound = getattr(self, attrib)
            if bound:
                if bound in df.columns.tolist():
                    enc[pbname] = bound
                else:
                    util.warn('Attribute "%s" bound to %s does not exist.' % (bound, attrib))
            elif default:
                enc[pbname] = default

        nodeid = self._node or Plotter._defaultNodeId
        (elist, nlist) = self._sanitize_dataset(edges, nodes, nodeid)
        self._check_dataset_size(elist, nlist)

        encodings = {
            'source': self._source,
            'destination': self._destination,
            'nodeId': self._node
        }
        bind(encodings, elist, 'edgeColor', '_edge_color')
        bind(encodings, elist, 'edgeLabel', '_edge_label')
        bind(encodings, elist, 'edgeTitle', '_edge_title')
        bind(encodings, elist, 'edgeWeight', '_edge_weight')
        bind(encodings, nlist, 'pointColor', '_point_color')
        bind(encodings, nlist, 'pointLabel', '_point_label')
        bind(encodings, nlist, 'pointTitle', '_point_title', nodeid)
        bind(encodings, nlist, 'pointSize', '_point_size')
        return (elist, nlist, encodings)

    def _make_dataset(self, edges, nodes, mode):
        if mode == 'json':
            return self._make_json_dataset(edges, nodes)
        elif mode == 'vgraph':
            return self._make_vgraph_dataset(edges, nodes)
        else:
            raise ValueError('Unknown mode: ' + mode)

    def _make_json_dataset(self, edges, nodes):
        (elist, nlist) = self._bind_attributes_v1(edges, nodes)

        edict = elist.where((pandas.notnull(elist)), None).to_dict(orient='records')
        name = ''.join(random.choice(string.ascii_uppercase +
                                     string.digits) for _ in range(10))
        bindings = {'idField': self._node or Plotter._defaultNodeId,
                    'destinationField': self._destination, 'sourceField': self._source}
        dataset = {'name': pygraphistry.PyGraphistry._dataset_prefix + name,
                   'bindings': bindings, 'type': 'edgelist', 'graph': edict}
        if nlist is not None:
            ndict = nlist.where((pandas.notnull(nlist)), None).to_dict(orient='records')
            dataset['labels'] = ndict
        return dataset

    def _make_vgraph_dataset(self, edges, nodes):
        from graph_vector_pb2 import VectorGraph

        def storeEdgeAttributes(df):
            coltypes = df.columns.to_series().groupby(df.dtypes)
            for dtype, cols in coltypes.groups.items():
                for col in cols:
                    if col == self._source or col == self._destination:
                        continue
                    if dtype.name == 'object':
                        df[col].where(pandas.notnull(df[col]), '', inplace=True)
                        df[col] = df[col].map(lambda x: x.decode('utf8'))
                    vec = typemap[dtype.name].add()
                    vec.name = col
                    vec.type = VectorGraph.EDGE
                    for val in df[col]:
                        vec.values.append(val)

        def storeNodeAttributes(df, nodeid, node_map):
            ordercol = '__order__'
            df[ordercol] = df[nodeid].map(lambda n: node_map[n])
            sdf = df.sort(ordercol)
            coltypes = df.columns.to_series().groupby(df.dtypes)
            for dtype, cols in coltypes.groups.items():
                for col in cols:
                    if col == nodeid or col == ordercol:
                        continue
                    if dtype.name == 'object':
                        df[col].where(pandas.notnull(df[col]), '', inplace=True)
                        df[col] = df[col].map(lambda x: x.decode('utf8'))
                    vec = typemap[dtype.name].add()
                    vec.name = col
                    vec.type = VectorGraph.VERTEX
                    for val in df[col]:
                        vec.values.append(val)

        (elist, nlist, enc) = self._bind_attributes_v2(edges, nodes)
        nodeid = self._node or Plotter._defaultNodeId

        vg = VectorGraph()
        typemap = {
            'object': vg.string_vectors,
            'int32': vg.int32_vectors,
            'int64': vg.int32_vectors,
            'float32': vg.double_vectors,
            'float64': vg.double_vectors
        }

        sources = elist[self._source]
        dests = elist[self._destination]

        lnodes = pandas.concat([sources, dests], ignore_index=True).unique()
        lnodes_df = pandas.DataFrame(lnodes, columns=[nodeid])
        filtered_nlist = pandas.merge(lnodes_df, nlist, on=nodeid, how='left')
        node_map = dict([(v, i) for i, v in enumerate(lnodes.tolist())])

        vg.version = 0
        vg.type = VectorGraph.DIRECTED
        vg.nvertices = len(node_map)
        vg.nedges = len(elist)
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        vg.name = pygraphistry.PyGraphistry._dataset_prefix + name

        for s, d in zip(sources.tolist(), dests.tolist()):
            e = vg.edges.add()
            e.src = node_map[s]
            e.dst = node_map[d]

        storeEdgeAttributes(elist)
        storeNodeAttributes(filtered_nlist, nodeid, node_map)

        return {'vgraph': vg, 'encodings': enc}
