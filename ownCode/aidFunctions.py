


def getNodeSummary(network):
    xcoord = network.nodes.x_coord
    ycoord = network.nodes.y_coord
    tot_out_links = network.nodes.tot_out_links
    for i in range(len(xcoord)):
        if network.nodes.is_centroid[i]:
            extra = ' is Centroid'
        else:
            extra = ""
        print('x coord '+str(xcoord[i])+' y coord '+str(ycoord[i])+' outgoing links '+str(tot_out_links[i])+extra)