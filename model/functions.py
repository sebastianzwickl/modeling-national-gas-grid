import pandas as pd
import geopandas as gpd
from shapely.ops import nearest_points
from shapely.geometry import Point, MultiPoint


def get_nearest_node(origin=None, all_nodes=None, districts=None):
    no = all_nodes.LAU_NAME.to_list()
    
    if origin in no:
        # print('Enthalten: {}'.format(origin))
        return all_nodes.loc[all_nodes.LAU_NAME == origin]['LAU_NAME'].item()
    else:
        # print('Nicht enthalten: {}'.format(origin))
        origin_centroid = districts[districts['LAU_NAME']==origin].centroid.values[0]
        # print('{}: x={}, y={}'.format(origin, origin_centroid.x, origin_centroid.y))
        multipoint = MultiPoint(all_nodes.centroid.to_list())
        # print(multipoint)
        queried_geom, nearest_geom = nearest_points(origin_centroid, multipoint)
        # print('Queried: {}, Nearest: {}'.format(queried_geom, nearest_geom))  
        lau_name = all_nodes.loc[all_nodes.centroid == nearest_geom]
        # print(lau_name)
        # print('Solution node: {}'.format(lau_name.LAU_NAME.to_list()[0]))
        return lau_name.LAU_NAME.to_list()[0]


def shapefile_without_cluster_pipelines(cluster=None, pipelines=None, districts=None):
    _pipelines = pipelines.loc[pipelines.cluster_km == cluster]
    nodes = list(set(list(_pipelines.Start) + list(_pipelines.End)))
    _filter_pip = pipelines.drop(pipelines[pipelines.cluster_km == cluster].index)
    target_nodes = list(set(list(_filter_pip.Start) + list(_filter_pip.End)))
    _filter_districts = districts.loc[districts.LAU_NAME.isin(target_nodes)]
    return nodes, _filter_districts
    





#     print('Node: {}'.format(src_n))
#     src_centroid = all_targets[all_targets['LAU_NAME']==src_n].centroid.values[0]
#     
#     multipoint = targets.centroid.unary_union
#     queried_geom, nearest_geom = nearest_points(src_centroid, multipoint)
#     # print('Queried: {}, Nearest: {}'.format(queried_geom, nearest_geom))  
#     lau_name = targets['geometry'].contains(nearest_geom)
#     s_index = lau_name[lau_name == True].index.to_list()[0]
#     
#     print(targets.index.to_list())
#     
#     print('{} ==> {}'.format(src_n, _name))
#     return