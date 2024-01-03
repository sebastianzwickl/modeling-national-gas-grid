from pathlib import Path
import geopandas as gpd
import pyomo.environ as py
import pyomo
import pandas as pd
import numpy as np


def read_shapefile(path=None, name=None):
    """
    Parameters
    ----------
    path : String, required
        Sets the path to the shapefile. The default is None.
    name : String, required
        Name of the shapefile. The default is None.

    Returns
    -------
    _data : GeoDataFrame
        Includes the information of the shapefile input data.

    """
    _path = Path(path)
    _data = gpd.read_file(_path / name)
    return _data


def get_nodes_from_lines(transmission=None, high_pressure=None, mid_pressure=None):
    """
    Parameters
    ----------
    transmission : GeoDataFrame, required
        Includes the transmission lines. The default is None.
    high_pressure : GeoDataFrame, required
        Includes the high-pressure pipelines. The default is None.
    mid_pressure : GeoDataFrame, required
        Includes the low-pressure pipelines. The default is None.

    Returns
    -------
    network : Dict
        Includes a dictionary with compressor, network level, and delivery nodes.

    """
    nodes_tra = []
    nodes_tra = nodes_tra + list(transmission.Start) + list(transmission.End)
    nodes_tra = list(set(nodes_tra))

    nodes_high = []
    nodes_high = nodes_high + list(high_pressure.Start) + list(high_pressure.End)
    nodes_high = list(set(nodes_high))

    nodes_mid = []
    nodes_mid = nodes_mid + list(mid_pressure.Start) + list(mid_pressure.End)
    nodes_mid = list(set(nodes_mid))

    compressors = nodes_tra
    con_tra_high = [x for x in nodes_tra if x in nodes_high]
    con_high_mid = [x for x in nodes_high if x in nodes_mid]

    network = {
        "Compressor": compressors,
        "High-Pressure": nodes_high,
        "Mid-Pressure": nodes_mid,
        "Delivery (transmission_high)": con_tra_high,
        "Delivery (high_mid)": con_high_mid,
    }

    return network


def create_model():
    """
    Returns
    -------
    m : pyomo.ConcreteModel
        Includes the model instance.

    """
    m = py.ConcreteModel()
    m.name = "CANCEL"
    return m


def add_nodal_sets(model=None, nodes=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance.. The default is None.
    nodes : dictionary, required
        Includes a dictionary with compressor, network level, and delivery nodes. The default is None.

    Returns
    -------
    None.

    """
    model.set_compressor = py.Set(initialize=nodes["Compressor"])
    _isolated_nodes_from_transmission_network = [
        "Hainburg a.d.Donau",
        "Marchegg",
        "Hartberg",
        "Gabersdorf",
        "Rosegg",
        "Gänserndorf",
        "Wolfsthal",
        "Ludmannsdorf",
        "Lambrechten",
        "Heiligenkreuz am Waasen",
        "Kittsee",
        "Arnoldstein",
        "Enzersfeld im Weinviertel",
        "Wettmannstätten",
        "Roßbach",
        "Köttmannsdorf",
        "Pinggau",
        "Pillichsdorf",
        "Schwand im Innkreis",
        "Grafenstein",
        "Neustift im Mühlkreis",
        "Gralla",
        "Mannsdorf an der Donau",
        "Engelhartstetten",
        "Berg",
        "Schwanberg",
        "Kirchheim im Innkreis",
        "Ruden",
        "Straß in Steiermark",
        "Überackern",
        "Bromberg",
        "Leobendorf",
        "Deutsch Jahrndorf",
        "Enzersdorf an der Fischa",
    ]
    model.set_node_hp = py.Set(
        initialize=nodes["High-Pressure"] + _isolated_nodes_from_transmission_network
    )
    model.set_node_mp = py.Set(initialize=nodes["Mid-Pressure"])
    model.set_delivery_tra_hp = py.Set(initialize=nodes["Delivery (transmission_high)"])
    model.set_delivery_hp_mp = py.Set(initialize=nodes["Delivery (high_mid)"])
    _storage = list(set(model.storage["Node"]))
    model.set_storage = py.Set(initialize=_storage)
    # Knoten mit die von Netzebene 2 auf Netzebene 1 umgehängt werden.
    list_of_nodes_switched = ['Schlierbach', 'Kremsmünster', 'Roitham am Traunfall', 'Wartberg an der Krems',
                              'Micheldorf in Oberösterreich', 'Gampern',
                              'Kapfenberg', 'Wiener Neustadt', 'Spital am Semmering',
                              'Gramatneusiedl', 'Natschbach-Loipersbach', 'Schottwien',
                              'Sankt Marein im Mürztal', 'Eggendorf', 'Ebenfurth', 'Ebreichsdorf',
                              'Krieglach', 'Breitenau', 'Kindberg', 'Mürzzuschlag', 'Pottendorf',
                              ]
    model.set_nodes_switched = py.Set(initialize=list_of_nodes_switched)
    return


def add_line_sets(model=None, data=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.
    data : List, required
        Includes the (pipe)line information to be added as a set. The default is None.

    Returns
    -------
    None.

    """
    for _data in data:

        _type = list(set(_data.Type))

        if _type[0] == "Transmission line":
            model.set_line_tra = py.Set(initialize=_data.index)

        if _type[0] == "High-Pressure":
            model.set_line_high = py.Set(initialize=_data.index)

        if _type[0] == "Mid-Pressure":
            model.set_line_mid = py.Set(initialize=_data.index)

    return


def add_time_horizon(model=None, year=None, temporal=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.
    year : integer, required
        Defines the final year of the modeling. The default is None.
    temporal : integer, required
        Defines the time steps per year. The default is None.

    Returns
    -------
    None.

    """

    model.set_year = py.Set(initialize=range(2025, year + 1, 1))
    model.set_time_unit = py.Set(initialize=range(1, temporal + 1, 1))
    return


def add_cluster_sets(model=None):
    high = model.high
    high_cluster = list(set(high["cluster_km"]))
    model.set_high_cluster = py.Set(initialize=high_cluster)

    mid = model.mid
    mid_cluster = list(set(mid["cluster_km"]))
    model.set_mid_cluster = py.Set(initialize=mid_cluster)

    return


def transmission_line_capacity_per_year(model, line, year):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def high_line_capacity_per_year(model, line, year):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def mid_line_capacity_per_year(model, line, year):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    if _end > year:
        return _data.Capacity.item()
    else:
        return 0


def init_nodal_demand_at_high_pressure(model, node, year, time):
    if node in model.set_nodes_switched:
        if year < 2030:
            if node in model.set_node_mp:
                _data = model.demand_high
                if year > 2050:
                    return _data.loc[
                        (_data.Node == node)
                        & (_data.Year == 2050)
                        & (_data.Month == (time - 1))
                        ]["Value in MWh"].item()
                else:
                    return _data.loc[
                        (_data.Node == node)
                        & (_data.Year == year)
                        & (_data.Month == (time - 1))
                        ]["Value in MWh"].item()
            else:
                _data_h = model.demand_high
                _data_m = model.demand_mid
                if year > 2050:
                    _val_h = _data_h.loc[
                        (_data_h.Node == node)
                        & (_data_h.Year == 2050)
                        & (_data_h.Month == (time - 1))
                        ]["Value in MWh"].item()
                    _val_m = _data_m.loc[
                        (_data_m.Node == node)
                        & (_data_m.Year == 2050)
                        & (_data_m.Month == (time - 1))
                        ]["Value in MWh"].item()
                    return _val_h + _val_m
                else:
                    _val_h = _data_h.loc[
                        (_data_h.Node == node)
                        & (_data_h.Year == year)
                        & (_data_h.Month == (time - 1))
                        ]["Value in MWh"].item()
                    _val_m = _data_m.loc[
                        (_data_m.Node == node)
                        & (_data_m.Year == year)
                        & (_data_m.Month == (time - 1))
                        ]["Value in MWh"].item()
                    return _val_h + _val_m
        else:
            _data_h = model.demand_high
            _data_m = model.demand_mid
            if year > 2050:
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == 2050)
                    & (_data_h.Month == (time - 1))
                    ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == 2050)
                    & (_data_m.Month == (time - 1))
                    ]["Value in MWh"].item()
                return _val_h + _val_m
            else:
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == year)
                    & (_data_h.Month == (time - 1))
                    ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == year)
                    & (_data_m.Month == (time - 1))
                    ]["Value in MWh"].item()
                return _val_h + _val_m
    else:
        if node in model.set_node_mp:
            _data = model.demand_high
            if year > 2050:
                return _data.loc[
                    (_data.Node == node)
                    & (_data.Year == 2050)
                    & (_data.Month == (time - 1))
                ]["Value in MWh"].item()
            else:
                return _data.loc[
                    (_data.Node == node)
                    & (_data.Year == year)
                    & (_data.Month == (time - 1))
                ]["Value in MWh"].item()
        else:
            _data_h = model.demand_high
            _data_m = model.demand_mid
            if year > 2050:
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == 2050)
                    & (_data_h.Month == (time - 1))
                ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == 2050)
                    & (_data_m.Month == (time - 1))
                ]["Value in MWh"].item()
                return _val_h + _val_m
            else:
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == year)
                    & (_data_h.Month == (time - 1))
                ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == year)
                    & (_data_m.Month == (time - 1))
                ]["Value in MWh"].item()
                return _val_h + _val_m


def init_nodal_demand_at_mid_pressure(model, node, year, time):
    # methane demand is generally split into high-pressure (hp) and mid-pressure (mp).
    # therefore, it has to be checked to which pressure levels a node is connected.
    # in order to parametrize methane demands, first the mid-pressure nodes are used.
    # consequently, if a node is connected to the mp but not to the hp level, all methane demands are handled as mp.
    if node in model.set_nodes_switched:
        if year < 2030:
            if node in model.set_node_hp:
                # dieser knoten ist mit der mitteldruck und hochdruck ebene verbunden
                # daher können die verbräuche getrennt behandelt werden
                _data = model.demand_mid
                if year > 2050:
                    # constant mid-pressure methane demand between 2050 and 2065.
                    return _data.loc[
                        (_data.Node == node)
                        & (_data.Year == 2050)
                        & (_data.Month == (time - 1))
                        ]["Value in MWh"].item()
                else:
                    # return value accordingly to existing input data.
                    return _data.loc[
                        (_data.Node == node)
                        & (_data.Year == year)
                        & (_data.Month == (time - 1))
                        ]["Value in MWh"].item()
            else:
                # der knoten ist nur mit der mitteldruckebene verbunden, nicht aber mit der hochdruckebene
                # dementsprechend wird der gesamate methanverbrauch der mitteldruckebene zugeschrieben
                _data_h = model.demand_high
                _data_m = model.demand_mid
                if year > 2050:
                    # constant total methane demand (i.e., sum of mp and hp) between 2050 and 2065.
                    _val_h = _data_h.loc[
                        (_data_h.Node == node)
                        & (_data_h.Year == 2050)
                        & (_data_h.Month == (time - 1))
                        ]["Value in MWh"].item()
                    _val_m = _data_m.loc[
                        (_data_m.Node == node)
                        & (_data_m.Year == 2050)
                        & (_data_m.Month == (time - 1))
                        ]["Value in MWh"].item()
                    return _val_h + _val_m
                else:
                    # return value accordingly to existing input data.
                    _val_h = _data_h.loc[
                        (_data_h.Node == node)
                        & (_data_h.Year == year)
                        & (_data_h.Month == (time - 1))
                        ]["Value in MWh"].item()
                    _val_m = _data_m.loc[
                        (_data_m.Node == node)
                        & (_data_m.Year == year)
                        & (_data_m.Month == (time - 1))
                        ]["Value in MWh"].item()
                    return _val_h + _val_m
        else:
            return 0
    else:
        if node in model.set_node_hp:
            # dieser knoten ist mit der mitteldruck und hochdruck ebene verbunden
            # daher können die verbräuche getrennt behandelt werden
            _data = model.demand_mid
            if year > 2050:
                # constant mid-pressure methane demand between 2050 and 2065.
                return _data.loc[
                    (_data.Node == node)
                    & (_data.Year == 2050)
                    & (_data.Month == (time - 1))
                ]["Value in MWh"].item()
            else:
                # return value accordingly to existing input data.
                return _data.loc[
                    (_data.Node == node)
                    & (_data.Year == year)
                    & (_data.Month == (time - 1))
                ]["Value in MWh"].item()
        else:
            # der knoten ist nur mit der mitteldruckebene verbunden, nicht aber mit der hochdruckebene
            # dementsprechend wird der gesamate methanverbrauch der mitteldruckebene zugeschrieben
            _data_h = model.demand_high
            _data_m = model.demand_mid
            if year > 2050:
                # constant total methane demand (i.e., sum of mp and hp) between 2050 and 2065.
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == 2050)
                    & (_data_h.Month == (time - 1))
                ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == 2050)
                    & (_data_m.Month == (time - 1))
                ]["Value in MWh"].item()
                return _val_h + _val_m
            else:
                # return value accordingly to existing input data.
                _val_h = _data_h.loc[
                    (_data_h.Node == node)
                    & (_data_h.Year == year)
                    & (_data_h.Month == (time - 1))
                ]["Value in MWh"].item()
                _val_m = _data_m.loc[
                    (_data_m.Node == node)
                    & (_data_m.Year == year)
                    & (_data_m.Month == (time - 1))
                ]["Value in MWh"].item()
                return _val_h + _val_m


def init_nodal_demand_at_tra_pressure(model, node, year, time):
    # transmission demand (i.e., "TRANSITBEDARF") per node, year, and month
    # excel input file name: "transit_demand_final_from_frontier.xlsx"
    # input years are 2021, 2030, 2035, and 2040 (excl. Arnoldstein where only 2021 is included).
    # column names: Node; Drct.; Year; Month; Value in MWh
    # transmission demand indicated by Drct. == "Export"

    if node == "Arnoldstein":
        # existing value only for 2021 ==> no value / zero for time up from 2030.
        if year >= 2030:
            return 0
        else:
            _data = model.demand_tra
            _val = _data.loc[
                (_data.Node == node)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            # linearly decreasing value between 2021 and 2030.
            return _val - (_val / 9) * (year - 2021)

    elif ("Kittsee" == node) or ("Straß in Steiermark" == node):
        _data = model.demand_tra
        if year <= 2030:
            _val_2021 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2021)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            _val_2030 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2030)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            return _val_2021 - (_val_2021 - _val_2030) / 9 * (year - 2021)
        elif year <= 2035:
            _val_2030 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2030)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            _val_2035 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2035)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            return _val_2030 - (_val_2030 - _val_2035) / 5 * (year - 2030)
        elif year <= 2040:
            _val_2035 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2035)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            _val_2040 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2040)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            return _val_2035 - (_val_2035 - _val_2040) / 5 * (year - 2035)
        else:
            # this branch means that year is greater than 2040 (e.g., 2042).
            # we assume linearly decreasing transmission demands through Austria between 2040 and 2050.
            # resulting in 50% of 2040's values in 2050.
            _val2040 = _data.loc[
                (_data.Node == node)
                & (_data.Year == 2040)
                & (_data["Drct."] == "Export")
                & (_data.Month == time)
            ]["Value in MWh"].item()
            if year > 2050:
                return _val2040 - 0.5 * _val2040 * (2050 - 2040) / 10
            else:
                return _val2040 - 0.5 * _val2040 * (year - 2040) / 10
    else:
        return 0


def init_pipeline_length_tra(model, line):
    _line = model.transmission.loc[line]
    return _line.Length.item()


def init_pipeline_length_high(model, line):
    _line = model.high.loc[line]
    if line == 51:
        return 0.01
    if line == 52:
        return 0.01
    if line == 53:
        return 0.01
    if line == 54:
        return 0.01
    return _line.Length.item()


def init_pipeline_length_mid(model, line):
    _line = model.mid.loc[line]
    return _line.Length.item()


def init_refurbishment_inv_costs_tra(model):
    _type = "Transmission"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_refurbishment_inv_costs_high(model):
    _type = "High-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_refurbishment_inv_costs_mid(model):
    _type = "Mid-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[
        (_data.Type == _type) & (_data.Name == "Specific investment costs")
    ]["Costs"]
    return _costs.item()


def init_tra_node_per_type(model, node, year):
    _type = "Transmission"
    # input file: 'INPUT_Source.xlsx'
    _data = model.source
    _data = _data.loc[_data.Node == node]
    if _data.empty:
        if year == 2040:
            print('No Transit-Import 2040 at {}'.format(node))
        return 0
    else:
        _data = model.feasible
        # Data imported has to be multiplied with 1000.
        _value = _data.loc[(_data.Node == node) & (_data.Year == year)]["Value"].item() * 1000
        if year == 2040:
            print('Transit-Import 2040 at {}: {}'.format(node, _value))
        return _value


def init_hp_node_per_type(model, node, year):
    # die knoten stockerau und redlham müssen auf netzebene 1 / hochdruck einspeisen
    # methane source at high-pressure node per year
    _gen = model.generation
    if node in list(set(_gen.Node)):
        if year >= 2050:
            return _gen.loc[(_gen.Node == node) & (_gen.Year == 2050)][
                "Value in MWh"
            ].item()
        else:
            return _gen.loc[(_gen.Node == node) & (_gen.Year == year)][
                "Value in MWh"
            ].item()
    else:
        return 0
    # if (
    #     (not (node in model.set_node_mp))
    #     or (node == "Stockerau")
    #     or (node == "Redlham")
    # ):
    #     _gen = model.generation
    #     if year >= 2050:
    #         return _gen.loc[(_gen.Node == node) & (_gen.Year == 2050)][
    #             "Value in MWh"
    #         ].item()
    #     else:
    #         return _gen.loc[(_gen.Node == node) & (_gen.Year == year)][
    #             "Value in MWh"
    #         ].item()
    # else:
    #     return 0


def init_mp_node_per_type(model, node, year):
    if node == 'Hörbranz':
        _data = model.source
        _data = _data.loc[_data.Node == node]
        _generation = model.generation
        if year >= 2040:
            return 309000 + 74000
        else:
            return _data.Source.item()
    else:
        if (node == "Vils") or (node == "Kufstein"):
            _data = model.source
            _data = _data.loc[_data.Node == node]
            _generation = model.generation
            if year >= 2040:
                if year > 2050:
                    return _generation.loc[
                        (_generation.Node == node) & (_generation.Year == 2050)
                    ]["Value in MWh"].item()
                else:
                    return _generation.loc[
                        (_generation.Node == node) & (_generation.Year == year)
                    ]["Value in MWh"].item()
            else:
                return _data.Source.item()
        else:
            if node not in model.set_node_hp:
                _generation = model.generation
                if node in list(set(_generation.Node)):
                    if year > 2050:
                        return _generation.loc[
                            (_generation.Node == node) & (_generation.Year == 2050)
                        ]["Value in MWh"].item()
                    else:
                        return _generation.loc[
                            (_generation.Node == node) & (_generation.Year == year)
                        ]["Value in MWh"].item()
                else:
                    return 0
            else:
                return 0


def high_line_depreciation_factor_per_year(model, line, year):
    _year = model.par_year_of_inv_hp[line]
    if year < _year:
        return 0
    else:
        _val = 1 - ((year - _year) / 20)
        if _val >= 0:
            return _val
        else:
            return 0


def tra_line_depreciation_factor_per_year(model, line, year):
    _year = model.par_year_of_inv_tra[line]
    if year < _year:
        return 0
    else:
        _val = 1 - ((year - _year) / 20)
        if _val >= 0:
            return _val
        else:
            return 0


def mid_line_depreciation_factor_per_year(model, line, year):
    _year = model.par_year_of_inv_mp[line]
    if year < _year:
        return 0
    else:
        _val = 1 - ((year - _year) / 20)
        if _val >= 0:
            return _val
        else:
            return 0


def tra_line_book_value(model, line, year):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _c_inv = _data["Inv.-cost"].item()
    _amo = _data["Amort."].item()
    _l = model.par_tra_length[line]
    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _c_inv * _l) * (1 - (year - _con) / _amo)


def high_line_book_value(model, line, year):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    # LENGTH
    _l = model.par_high_length[line]
    # SPECIFIC INVESTMENT COSTS
    _specific = model.par_ref_high
    _amo = _data["Amort."].item()
    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _l * _specific) * (1 - (year - _con) / _amo)


def mid_line_book_value(model, line, year):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"

    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _capacity = _data.Capacity.item()
    _con = _data["Yr.-con."].item()

    _data = model.pipeline_economic
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _l = model.par_mid_length[line]
    _specific = model.par_ref_mid
    _amo = _data["Amort."].item()
    if year > _con + _amo:
        return 0
    else:
        return (_capacity * _l * _specific) * (1 - (year - _con) / _amo)


def init_fixed_costs_tra(model):
    _type = "Transmission"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_fixed_costs_high(model):
    _type = "High-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_fixed_costs_mid(model):
    _type = "Mid-Pressure"
    _data = model.refurbishment
    _costs = _data.loc[(_data.Type == _type) & (_data.Name == "Fixed costs")]["Costs"]
    return _costs.item()


def init_year_of_inv_tra(model, line):
    _line = model.transmission.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Transmission"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_year_of_inv_high(model, line):
    _line = model.high.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "High-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_year_of_inv_mid(model, line):
    _line = model.mid.loc[line]
    _start = _line.Start
    _end = _line.End
    _type = "Mid-Pressure"
    _data = model.pipeline_technical
    _data = _data.loc[
        (_data.Start == _start) & (_data.End == _end) & (_data.Type == _type)
    ]
    _start = _data["Yr.-con."].item()
    _end = _start + _data["Tec.-life"].item()
    return _end


def init_total_peak_rel_factor(model, month):
    """
    So far, a constant factor between total and peak gas demand per month is implemented.
    However, this should be updated to improve the temporal resolution of the analysis.
    In principle, this factor influences the utilization rate of a pipeline per month.
    """

    """
    Considering scaling factors (1.1) for both months January and December in order to consider daily gas peak demands.
    """
    return 720
    # if (month == 1) or (month == 12) or (month == 2):
    #     return 720 / 1.1
    # else:
    #     return 720


def init_gas_prices_per_year_and_month(model, year, month):
    _data = model.prices
    _val_per_year = _data.loc[_data.Year == year]["Price"].item()
    if (month == 1) or (month == 2) or (month == 3) or (month == 12) or (month == 11):
        return 1.01 * _val_per_year
    elif (month == 6) or (month == 7) or (month == 8) or (month == 9) or (month == 5):
        return 0.9999 * _val_per_year
    else:
        return _val_per_year


def add_parameter_to_model(model=None):
    """
    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        Includes the model instance. The default is None.

    Returns
    -------
    None.

    """
    model.par_tra_capacity = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=transmission_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Pipeline capacity at the transmission network level",
    )

    model.par_high_capacity = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Pipeline capacity at the high-pressure network level",
    )

    model.par_mid_capacity = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_capacity_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Pipeline capacity at the mid-pressure network level",
    )

    model.par_source_mp = py.Param(
        model.set_node_mp,
        model.set_year,
        initialize=init_mp_node_per_type,
        within=py.NonNegativeReals,
        doc="CHECKED: Mid-pressure gas source at node n in year y",
    )

    model.par_source_hp = py.Param(
        model.set_node_hp,
        model.set_year,
        initialize=init_hp_node_per_type,
        within=py.NonNegativeReals,
        doc="CHECKED: High-pressure gas source at node n in year y",
    )

    # Überprüfen ob Quellen und Verbrauch 2040 richtig parametrisiert sind.
    # 2) Einspeisung|2040|High
    _par_source_hp = sum(model.par_source_hp[node, 2040] for node in model.set_node_hp)
    print("Source|2040|High: ", np.around(_par_source_hp, 0))

    _par_source_mp = sum(model.par_source_mp[node, 2040] for node in model.set_node_mp)
    print("Source|2040|Mid: ", np.around(_par_source_mp, 0))
    #

    model.par_demand_mid = py.Param(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_mid_pressure,
        within=py.NonNegativeReals,
        doc="CHECKED: Mid-pressure gas demand at node n in year y and month m",
    )

    model.par_demand_high = py.Param(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_high_pressure,
        within=py.NonNegativeReals,
        doc="CHECKED: High-pressure gas demand at node n in year y and month m",
    )

    # Überprüfen ob Quellen und Verbrauch 2040 richtig parametrisiert sind.
    # 1) Verbrauch|2040|High
    _demand_2040_high_ = sum(
        model.par_demand_high[node, 2040, month]
        for node in model.set_node_hp
        for month in model.set_time_unit
    )
    print("Demand|2040|High: ", np.around(_demand_2040_high_, 0))

    _demand_2040_mid = sum(
        model.par_demand_mid[node, 2040, month]
        for node in model.set_node_mp
        for month in model.set_time_unit
    )
    print("Demand|2040|Mid: ", np.around(_demand_2040_mid, 0))
    #

    model.par_demand_tra = py.Param(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        initialize=init_nodal_demand_at_tra_pressure,
        within=py.NonNegativeReals,
        doc="CHECKED: Nodal gas demand at the transmission network level in year y and month m",
    )

    model.par_tra_length = py.Param(
        model.set_line_tra,
        initialize=init_pipeline_length_tra,
        within=py.NonNegativeReals,
        doc="CHECKED: Length of the tranmission pipeline",
    )

    model.par_high_length = py.Param(
        model.set_line_high,
        initialize=init_pipeline_length_high,
        within=py.NonNegativeReals,
        doc="CHECKED: Length of the high-pressure pipeline",
    )

    model.par_mid_length = py.Param(
        model.set_line_mid,
        initialize=init_pipeline_length_mid,
        within=py.NonNegativeReals,
        doc="CHECKED: Length of the mid-pressure pipeline",
    )

    model.par_ref_tra = py.Param(
        initialize=init_refurbishment_inv_costs_tra,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific transmission pipeline refurbishment investment costs per MW and km",
    )

    model.par_ref_high = py.Param(
        initialize=init_refurbishment_inv_costs_high,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific high-pressure pipeline refurbishment investment costs per MW and km",
    )

    model.par_ref_mid = py.Param(
        initialize=init_refurbishment_inv_costs_mid,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific mid-pressure pipeline refurbishment investment costs per MW and km",
    )

    model.par_wacc = py.Param(
        initialize=0.05, doc="CHECKED: Weighted average cost of capital"
    )

    model.par_source_tra = py.Param(
        model.set_compressor,
        model.set_year,
        initialize=init_tra_node_per_type,
        within=py.NonNegativeReals,
        doc="CHECKED: Nodal gas source at the transmission network level in year y",
    )

    model.par_year_of_inv_tra = py.Param(
        model.set_line_tra,
        initialize=init_year_of_inv_tra,
        within=py.NonNegativeReals,
        doc="CHECKED: Planned year of refurbishment investment per transmission line",
    )

    model.par_year_of_inv_hp = py.Param(
        model.set_line_high,
        initialize=init_year_of_inv_high,
        within=py.NonNegativeReals,
        doc="CHECKED: Planned year of refurbishment investment per high-pressure line",
    )

    model.par_year_of_inv_mp = py.Param(
        model.set_line_mid,
        initialize=init_year_of_inv_mid,
        within=py.NonNegativeReals,
        doc="CHECKED: Planned year of refurbishment investment per mid-pressure line",
    )

    model.par_depreciation_tra = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=tra_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Depreciation factor of a refurbished transmission pipeline investment",
    )

    model.par_depreciation_high = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Depreciation factor of a refurbished high-pressure pipeline investment",
    )

    model.par_depreciation_mid = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_depreciation_factor_per_year,
        within=py.NonNegativeReals,
        doc="CHECKED: Depreciation factor of a refurbished mid-pressure pipeline investment",
    )

    model.par_book_value_tra = py.Param(
        model.set_line_tra,
        model.set_year,
        initialize=tra_line_book_value,
        within=py.NonNegativeReals,
        doc="CHECKED: Book value of a pipeline at the transmission network level in year y",
    )

    model.par_book_value_high = py.Param(
        model.set_line_high,
        model.set_year,
        initialize=high_line_book_value,
        within=py.NonNegativeReals,
        doc="CHECKED: Book value of a pipeline at the high-pressure network level in year y",
    )

    model.par_book_value_mid = py.Param(
        model.set_line_mid,
        model.set_year,
        initialize=mid_line_book_value,
        within=py.NonNegativeReals,
        doc="CHECKED: Book value of a pipeline at the mid-pressure network level in year y",
    )

    model.par_i = py.Param(initialize=0.015, doc="Interest rate: 1.5%")

    model.par_fixed_tra = py.Param(
        initialize=init_fixed_costs_tra,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific fixed costs per transmission pipeline capacity",
    )

    model.par_fixed_high = py.Param(
        initialize=init_fixed_costs_high,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific fixed costs per high-pressure pipeline capacity",
    )

    model.par_fixed_mid = py.Param(
        initialize=init_fixed_costs_mid,
        within=py.NonNegativeReals,
        doc="CHECKED: Specific fixed costs per mid-pressure pipeline capacity",
    )

    model.par_total_peak_factor = py.Param(
        model.set_time_unit,
        initialize=init_total_peak_rel_factor,
        within=py.NonNegativeReals,
        doc="CHECKED: Transforming monthly demand values to max capacity values and vice versa.",
    )

    model.par_gas_prices = py.Param(
        model.set_year,
        model.set_time_unit,
        initialize=init_gas_prices_per_year_and_month,
        within=py.NonNegativeReals,
        doc="CHECKED: Gas price per year and month in order to include seasonal storage into the system.",
    )

    """VALUE OF LOST LOAD / KOSTEN EINER ALTERNATIVEN VERSORGUNG"""

    _Value_of_Lost_Load = pd.read_excel("data/INPUT_Value_of_Lost_Load.xlsx")
    _VoLL_High = (
        _Value_of_Lost_Load[_Value_of_Lost_Load.Type == "High-Pressure"]
        .groupby(["Year"])["Value in EUR per MWh"]
        .apply(lambda x: x.iloc[0])
        .to_dict()
    )
    _VoLL_Mid = (
        _Value_of_Lost_Load[_Value_of_Lost_Load.Type == "Mid-Pressure"]
        .groupby(["Year"])["Value in EUR per MWh"]
        .apply(lambda x: x.iloc[0])
        .to_dict()
    )
    model.par_value_of_lost_load_high = py.Param(
        model.set_year,
        initialize=_VoLL_High,
        within=py.NonNegativeReals,
        doc="CHECKED: Cost parameter for not supplying high-pressure gas demands per year in EUR / MWh.",
    )
    model.par_value_of_lost_load_mid = py.Param(
        model.set_year,
        initialize=_VoLL_Mid,
        within=py.NonNegativeReals,
        doc="CHECKED: Cost parameter for not supplying mid-pressure gas demands per year in EUR / MWh.",
    )

    return


def add_decision_variables(model=None):
    """


    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        The model instance that is used to add the decision variables. The default is None.

    Returns
    -------
    None.

    """

    model.var_capex = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="CAPEX: capital expenditures (per year)",
    )

    model.var_opex = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="OPEX: operational expenditures (per year)",
    )

    model.var_rev = py.Var(
        model.set_year, domain=py.NonNegativeReals, doc="REV: revenues (per year)"
    )

    model.var_pi = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of assets (per year)",
    )

    model.var_lambda_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for transmission pipelines (per year)",
    )

    model.var_lambda_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for high-pressure pipelines (per year)",
    )

    model.var_lambda_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Fixed costs for mid-pressure pipelines (per year)",
    )

    model.var_gamma_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed transmission pipeline capacity (per year)",
    )

    model.var_gamma_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed high-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total installed mid-pressure pipeline capacity (per year)",
    )

    model.var_gamma_tra_line = py.Var(
        model.set_year,
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Transmission pipeline capacity (per year)",
    )

    model.var_gamma_high_line = py.Var(
        model.set_year,
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="High-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid_line = py.Var(
        model.set_year,
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Mid-pressure pipeline capacity (per year)",
    )

    model.var_gamma_tra_line_inv = py.Var(
        model.set_year,
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Refurbished trans. pipeline capacity (per year)",
    )

    model.var_gamma_high_line_inv = py.Var(
        model.set_year,
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="Refurbished high-pressure pipeline capacity (per year)",
    )

    model.var_gamma_mid_line_inv = py.Var(
        model.set_year,
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Refurbished mid-pressure pipeline capacity (per year)",
    )

    '''
    LUMPINESS OF PIPELINE DIAMETERS IS SIMPLIFIED MODELED IN ORDER TO ENSURE SMALLEST DIAMETER CONSTRAINTS.
    
    Transmission : 13877,
    Netzebene 1 : 60,
    Netzebene 2 : 60
    
    '''

    model.lumpiness_tra = py.Var(model.set_line_tra, within=py.NonNegativeReals, bounds=(0, 1))
    model.lumpiness_high = py.Var(model.set_line_high, within=py.NonNegativeReals, bounds=(0, 1))
    model.lumpiness_mid = py.Var(model.set_line_mid, within=py.Binary, bounds=(0, 1))

    model.var_pi_tra = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of transmission pipelines (per year)",
    )

    model.var_pi_high = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of high-pressure pipelines (per year)",
    )

    model.var_pi_mid = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of mid-pressure pipelines (per year)",
    )

    model.var_pi_tra_line = py.Var(
        model.set_line_tra,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a transmission pipeline",
    )

    model.var_pi_high_line = py.Var(
        model.set_line_high,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a high-pressure pipeline",
    )

    model.var_pi_mid_line = py.Var(
        model.set_line_mid,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Book value of a mid-pressure pipeline",
    )

    model.var_pi_tra_line_inv = py.Var(
        model.set_line_tra,
        domain=py.NonNegativeReals,
        doc="Book value of the transmission pipeline refurbishment investment",
    )

    model.var_pi_high_line_inv = py.Var(
        model.set_line_high,
        domain=py.NonNegativeReals,
        doc="Book value of the high-pressure pipeline refurbishment investment",
    )

    model.var_pi_mid_line_inv = py.Var(
        model.set_line_mid,
        domain=py.NonNegativeReals,
        doc="Book value of the mid-pressure pipeline refurbishment investment",
    )

    """SOURCE AT THE NODAL AND NETWORK LEVEL"""
    model.var_source_tra = py.Var(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the transmission network level at a node",
    )

    model.var_source_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the high-pressure network level at a node",
    )

    model.var_source_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Source of natural gas at the mid-pressure network level at a node",
    )

    """TRANSPORTATION AT THE PIPELINES"""
    model.var_transported_tra = py.Var(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a transmission pipeline (per year and month)",
    )

    model.var_transported_high = py.Var(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a high-pressure pipeline (per year and month)",
    )

    model.var_transported_mid = py.Var(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
        doc="Gas amount transported at a mid-pressure pipeline (per year and month)",
    )

    """(SUPPLIED) NODAL DEMAND"""
    model.var_demand_tra = py.Var(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the transmission network level that is covered (per year and month)",
    )
    model.var_demand_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the high-pressure network level that is covered (per year and month)",
    )
    model.var_demand_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Gas demand at the mid-pressure network level that is covered (per year and month)",
    )

    """
    STORAGE INPUT/OUTPUT AND GAS STATE OF CHARGE
    - only at the high-pressure level
    """
    model.var_storage_in_out = py.Var(
        model.set_storage, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_storage_soc = py.Var(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    """IMPORT & EXPORT"""
    model.var_export_tra = py.Var(
        model.set_compressor, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_export_high = py.Var(
        model.set_node_hp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_export_mid = py.Var(
        model.set_node_mp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_tra = py.Var(
        model.set_compressor, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_high = py.Var(
        model.set_node_hp, model.set_year, model.set_time_unit, domain=py.Reals
    )
    model.var_import_mid = py.Var(
        model.set_node_mp, model.set_year, model.set_time_unit, domain=py.Reals
    )

    """REVENUES"""
    model.var_revenues_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )
    model.var_revenues_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    """SPENDING FOR GAS PURCHASE"""
    model.var_gas_purchase = py.Var(model.set_year, domain=py.NonNegativeReals)

    # THIS CONSTRAINT IS MODIFIED FOR THE GREEN GAS ("GG") SCENARIO.
    """DELIVERY BETWEEN TRANSMISSION AND HIGH-PRESSURE NETWORK LEVEL"""
    model.var_del_tra_high = py.Var(
        model.set_delivery_tra_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )

    model.var_del_high_mid = py.Var(
        model.set_delivery_hp_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.Reals,
    )

    # ADDING DECISION VARIABLES FOR SUPPLY THAT IS NOT SUPPLIED.
    model.var_demand_not_supplied_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )
    model.var_demand_not_supplied_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
    )
    # IMPLEMENTATION OF VALUE OF LOST LOAD
    model.var_value_of_lost_load = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Total costs resulting from not supplying gas demands per year",
    )
    model.var_value_of_lost_load_high = py.Var(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Costs resulting from not supplying high-pressure gas demands",
    )
    model.var_value_of_lost_load_mid = py.Var(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        domain=py.NonNegativeReals,
        doc="Costs resulting from not supplying mid-pressure gas demands",
    )
    model.var_VoLL_SOURCE = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Source-related Value of Lost Load per Year.",
    )

    # EXTENSION OF THE VALUE OF LOST LOAD RELATED TO GREEN METHANE PRODUCTION AT THE LOCAL LEVELS.
    model.var_VoLL_src_hp = py.Var(
        model.set_node_hp,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Quantity of the local green methane potential / production that is not used at the high-pressure level.",
    )
    model.var_VoLL_src_mp = py.Var(
        model.set_node_mp,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Quantity of the local green methane potential / production that is not used at the mid-pressure level.",
    )

    # VORZEITIGE STILLLEGUNG DER LEITUNG VOR ABLAUF DER TECHNISCHEN LEBENSDAUER UM O&M KOSTEN ZU SPAREN
    model.v_dec_early_hp = py.Var(
        model.set_line_high,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Kapazität auf Hochdruckleitung die vorzeitig stillgelegt wird, daher vor Ende technischen Lebensdauer.",
    )
    model.v_dec_early_mp = py.Var(
        model.set_line_mid,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Kapazität auf Mitteldruckleitung die vorzeitig stillgelegt wird, daher vor Ende technischen Lebensdauer.",
    )

    model.v_bd_early_hp_2030 = py.Var(
        model.set_line_high,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Hochdruck-Kapazität vor Ablauf der technischen Lebensdauer"
    )

    model.v_bd_early_hp_2035 = py.Var(
        model.set_line_high,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Hochdruck-Kapazität vor Ablauf der technischen Lebensdauer",
    )

    model.v_bd_early_hp_2040 = py.Var(
        model.set_line_high,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Hochdruck-Kapazität vor Ablauf der technischen Lebensdauer",
    )

    model.v_bd_early_mp_2030 = py.Var(
        model.set_line_mid,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Mitteldruck-Kapazität vor Ablauf der technischen Lebensdauer"
    )

    model.v_bd_early_mp_2035 = py.Var(
        model.set_line_mid,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Mitteldruck-Kapazität vor Ablauf der technischen Lebensdauer",
    )

    model.v_bd_early_mp_2040 = py.Var(
        model.set_line_mid,
        domain=py.NonNegativeReals,
        bounds=(0, 1),
        doc="Binäre EV: Stilllegung der existierenden Mitteldruck-Kapazität vor Ablauf der technischen Lebensdauer",
    )
    # CLUSTER DECISION VARIABLES
    model.bd_cluster_high_2030 = py.Var(
        model.set_high_cluster, domain=py.Binary, doc="BD of Cluster at High in 2030", bounds=(0, 1)
    )
    model.bd_cluster_high_2035 = py.Var(
        model.set_high_cluster, domain=py.Binary, doc="BD of Cluster at High in 2035", bounds=(0, 1)
    )
    model.bd_cluster_high_2040 = py.Var(
        model.set_high_cluster, domain=py.Binary, doc="BD of Cluster at High in 2040", bounds=(0, 1)
    )
    model.bd_cluster_mid_2030 = py.Var(
        model.set_mid_cluster, domain=py.Binary, doc="BD of Cluster at Mid in 2030", bounds=(0, 1)
    )
    model.bd_cluster_mid_2035 = py.Var(
        model.set_mid_cluster, domain=py.Binary, doc="BD of Cluster at Mid in 2035", bounds=(0, 1)
    )
    model.bd_cluster_mid_2040 = py.Var(
        model.set_mid_cluster, domain=py.Binary, doc="BD of Cluster at Mid in 2040", bounds=(0, 1)
    )

    # ABSCHREIBUNG
    model.v_hp_abschreibung = py.Var(
        model.set_line_high,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Abschreibung pro Hochdruckleitung und Jahr.",
    )

    model.v_mp_abschreibung = py.Var(
        model.set_line_mid,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Abschreibung pro Mitteldruckleitung und Jahr.",
    )

    model.v_tra_abschreibung = py.Var(
        model.set_line_tra,
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Abschreibung pro Fernleitung und Jahr.",
    )

    model.v_abschreibung = py.Var(
        model.set_year,
        domain=py.NonNegativeReals,
        doc="Gesamt-Abschreibung pro Jahr im Netzwerk.",
    )

    return


def obj_value(model=None):
    """


    Parameters
    ----------
    model : pyomo.ConcreteModel, required
        The model instance that is used to add the decision variables. The default is None.

    Returns
    -------
    Expression of the objective function
        SUM [ (1/(1+i)^(year-2025)) * (Capex + Opex - Revenues) ]

    """

    return sum(
        (1 / (1 + model.par_i) ** (year - 2025))
        * (
            model.var_capex[year]
            + model.var_opex[year]
            - model.var_rev[year]
            + model.var_gas_purchase[year]
            + model.var_value_of_lost_load[year]
            + model.var_VoLL_SOURCE[year]
            + model.v_abschreibung[year]
        )
        for year in range(2025, 2051, 1)
    )


def add_objective_function(model=None):
    """


    Parameters
    ----------
    model : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """

    model.objective = py.Objective(rule=obj_value, sense=py.minimize)

    return


def add_import_and_export_lines_per_node(model=None):
    """TRANSMISSION NETWORK LEVEL"""
    _data = model.transmission
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.tra_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.tra_import_lines = _dict

    """HIGH-PRESSURE NETWORK LEVEL"""
    _data = model.high
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.high_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.high_import_lines = _dict

    """MID-PRESSURE NETWORK LEVEL"""
    _data = model.mid
    _dict = dict()
    for node in _data.Start:
        _dict[node] = list(_data.loc[_data.Start == node].index)
    model.mid_export_lines = _dict
    _dict = dict()
    for node in _data.End:
        _dict[node] = list(_data.loc[_data.End == node].index)
    model.mid_import_lines = _dict

    return


def print_model(model=None):

    model.write("CANCEL.lp", io_options={"symbolic_solver_labels": True})

    """PRINT MODEL TO .TXT FILE"""
    _file = open("CANCEL.txt", "w", encoding="utf-8")
    model.pprint(ostream=_file, verbose=False, prefix="")
    _file.close()
    return


def set_solver_for_the_model(model=None):
    Solver = pyomo.opt.SolverFactory("gurobi")
    Solver.options["mipgap"] = 0.05
    Solver.options["MIPFocus"] = 3
    Solver.options['threads'] = 12
    # Solver.options["LogFile"] = str(model.name) + ".log"
    Solver.options['Cuts'] = 2
    Solver.options['Presolve'] = 2
    Solver.options['TimeLimit'] = 48 * 60 * 60
    return Solver
