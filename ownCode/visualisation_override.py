import numpy as np
from bokeh.io import  show
from dyntapy.settings import parameters
from dyntapy.utilities import __create_green_to_red_cm
from dyntapy.visualization import _process_plot_arguments, get_max_edge_width, _get_colors_and_coords, _edge_cds, warnings, Patches, HoverTool, _node_cds, Circle
from bokeh.models import  LabelSet, ColumnDataSource
from ownFunctions import global_signalized_nodes

traffic_cm = __create_green_to_red_cm()

link_highlight_colors = parameters.visualization.link_highlight_colors
node_highlight_color = parameters.visualization.node_highlight_color
node_color = parameters.visualization.node_color
centroid_color = parameters.visualization.centroid_color
node_size = parameters.visualization.node_size

def show_network(
    g,
    flows=None,
    link_kwargs=dict(),
    node_kwargs=dict(),
    highlight_links=np.array([]),
    highlight_nodes=np.array([]),
    euclidean=False,
    title=None,
    notebook=False,
    show_nodes=True,
    return_plot=False,
    signalized_nodes = False, 
    O_or_D = False,
):

    plot, tmp, link_width_scaling = _process_plot_arguments(
        g, title, notebook, euclidean, link_kwargs, node_kwargs
    )
    show_flows = True
    if flows is not None:
        pass
    else:
        flows = np.zeros(g.number_of_edges())
        show_flows = False
    max_flow = max(np.max(flows), 1)

    max_width_bokeh, max_width_coords = get_max_edge_width(
        tmp,
        link_width_scaling,
        parameters.visualization.plot_size,
    )

    if type(highlight_links) not in (np.ndarray, list):
        raise ValueError
    c, x, y = _get_colors_and_coords(
        tmp,
        max_width_coords,
        max_flow,
        flows,
        time_step=1,
        highlight_links=highlight_links,
        patch_ratio=parameters.visualization.link_width_min_max_ratio,
    )
    edge_source = _edge_cds(tmp, c, flows, x, y, **link_kwargs)
    edge_renderer = plot.add_glyph(
        edge_source,
        glyph=Patches(
            xs="x",
            ys="y",
            fill_color="color",
            line_color="black",
            line_alpha=0.8,
            fill_alpha=parameters.visualization.link_transparency,
        ),
    )
    edge_tooltips = [
        (item, f"@{item}")
        for item in parameters.visualization.link_keys + list(link_kwargs.keys())
        if item != "flow"
    ]
    if show_flows:
        edge_tooltips.append(("flow", "@flow{(0.00)}"))
    edge_hover = HoverTool(
        show_arrow=False,
        tooltips=edge_tooltips,
        renderers=[edge_renderer],
        description="Link Hover Tool",
    )
    if show_nodes:
        node_source = _node_cds(tmp, highlight_nodes, **node_kwargs)
        node_renderer = plot.add_glyph(
            node_source,
            glyph=Circle(
                x="x",
                y="y",
                size=node_size,
                line_color="black",
                fill_color="color",
                line_alpha=0.4,
                fill_alpha=0.7,
                line_width=node_size / 10,
            ),
        )
        node_tooltips = [
            (item, f"@{item}")
            for item in parameters.visualization.node_keys + list(node_kwargs.keys())
        ]
        node_hover = HoverTool(
            show_arrow=False,
            tooltips=node_tooltips,
            renderers=[node_renderer],
            description="Node Hover Tool",
        )
        plot.add_tools(node_hover)
    plot.add_tools(edge_hover)

    # add labels
    source1 = get_node_list(g,signalized_nodes)
    labels1 = LabelSet(x='x', y='y', text='names',
              x_offset=2, y_offset=2, source = source1, render_mode='css',text_color = "#444444", text_font_size = "24px")
    source2 = get_link_list(g)
    labels2 = LabelSet(x='x', y='y', text='names',
              x_offset=0, y_offset=0, source = source2, render_mode='css', text_color = '#0000FF' , text_font_size = "16px")
    source3 = get_signal_node_list(g,signalized_nodes)
    labels3 = LabelSet(x='x', y='y', text='names',
              x_offset=0, y_offset=0, source = source3, render_mode='css', text_color = '#FF0000' , text_font_size = "24px", text_font_style = 'bold')
    source4 = get_od_list(O_or_D)
    labels4 = LabelSet(x='x', y='y', text='names',
              x_offset=-25, y_offset=-25, source = source4, render_mode='css', text_color = '#008000' , text_font_size = "24px", text_font_style = 'bold')
    
    plot.add_layout(labels1)
    plot.add_layout(labels2)
    plot.add_layout(labels3)
    plot.add_layout(labels4)
    if not return_plot:
        show(plot)
    else:
        return plot
    

def get_node_list(g, signalized_nodes):
    x_coord = []
    y_coord = []
    id_s = []
    for v in g.nodes:
        try:
            g.nodes[v]['centroid']
        except KeyError:
            if g.nodes[v]['node_id'] not in signalized_nodes:
                x_coord.append(g.nodes[v]['x_coord'])
                y_coord.append(g.nodes[v]['y_coord'])
                id_s.append(str(g.nodes[v]['node_id']))
    source = ColumnDataSource(data=dict(x=x_coord,
                                    y=y_coord,
                                    names=id_s))
    return source

def get_link_list(g):
    x_coord = []
    y_coord = []
    id_s = []

    for u,v,data in g.edges.data():
        try:
            data['connector']
        except KeyError:
            x_coord.append((g.nodes[u]['x_coord']+g.nodes[v]['x_coord'])/2)
            y_coord.append((g.nodes[u]['y_coord']+g.nodes[v]['y_coord'])/2)
            id_s.append(str(data['link_id']))
    source = ColumnDataSource(data=dict(x=x_coord,
                                    y=y_coord,
                                    names=id_s))
    return source 

def get_signal_node_list(g, signalized_nodes):
    x_coord = []
    y_coord = []
    id_s = []

    for v in g.nodes:
        if g.nodes[v]['node_id'] in signalized_nodes:
            x_coord.append(g.nodes[v]['x_coord'])
            y_coord.append(g.nodes[v]['y_coord'])
            id_s.append(str(g.nodes[v]['node_id']))

    source = ColumnDataSource(data=dict(x=x_coord,
                                    y=y_coord,
                                    names=id_s))
    return source

def get_od_list(O_or_D):
    x_coord = []
    y_coord = []
    id_s = []
    for idx,(x,y) in enumerate(O_or_D):
        x_coord.append(x)
        y_coord.append(y)
        id_s.append(idx)
    source = ColumnDataSource(data=dict(x=x_coord,
                                    y=y_coord,
                                    names=id_s))
    return source