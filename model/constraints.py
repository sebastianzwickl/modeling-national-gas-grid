import pyomo.environ as py


def cal_capex_per_year(model, year):
    # Kalkulatorische Zinsen = Gesamtbuchwert x WACC
    return model.var_capex[year] == model.var_pi[year] * model.par_wacc


def cal_total_fixed_costs_per_year(model, year):
    # Laufende Betriebskosten = Summe(Fernleitung, Netzebene 1, Netzebene 2)
    return (
        model.var_opex[year]
        == model.var_lambda_tra[year]
        + model.var_lambda_high[year]
        + model.var_lambda_mid[year]
    )


def cal_fixed_costs_tra(model, year):
    return model.var_lambda_tra[year] == model.var_gamma_tra[year] * model.par_fixed_tra


def cal_fixed_costs_high(model, year):
    return (
        model.var_lambda_high[year] == model.var_gamma_high[year] * model.par_fixed_high
    )


def cal_fixed_costs_mid(model, year):
    return model.var_lambda_mid[year] == model.var_gamma_mid[year] * model.par_fixed_mid


def cal_total_tra_capacity(model, year):
    # IT IS ASSUMED THAT 200KM ARE A REPRESENTATIVE LENGTH FOR A LINE AT THE TRANSMISSION LEVEL.
    # BASED ON THAT, FIXED COSTS ARE SCALED BY THE LENGTH OF THE CONSIDERED LINE LENGTH.
    return model.var_gamma_tra[year] == sum(
        model.var_gamma_tra_line[year, line] * model.par_tra_length[line] / 200
        for line in model.set_line_tra
    )


def cal_total_high_capacity(model, year):
    # IT IS ASSUMED THAT 150KM ARE A REPRESENTATIVE LENGTH FOR A LINE AT THE HIGH-PRESSURE LEVEL.
    # BASED ON THAT, FIXED COSTS ARE SCALED BY THE LENGTH OF THE CONSIDERED LINE LENGTH.
    return model.var_gamma_high[year] == sum(
        model.var_gamma_high_line[year, line] * model.par_high_length[line] / 150
        for line in model.set_line_high
    )


def cal_total_mid_capacity(model, year):
    # IT IS ASSUMED THAT 25KM ARE A REPRESENTATIVE LENGTH FOR A LINE AT THE MID-PRESSURE LEVEL.
    # BASED ON THAT, FIXED COSTS ARE SCALED BY THE LENGTH OF THE CONSIDERED LINE LENGTH.
    return model.var_gamma_mid[year] == sum(
        model.var_gamma_mid_line[year, line] * model.par_mid_length[line] / 25
        for line in model.set_line_mid
    )


def cal_cap_per_tra_line(model, year, line):
    return (
        model.var_gamma_tra_line[year, line]
        == model.par_tra_capacity[line, year] + model.var_gamma_tra_line_inv[year, line]
    )


def cal_cap_per_hp_line(model, year, line):
    return (
        model.var_gamma_high_line[year, line]
        == model.par_high_capacity[line, year]
        + model.var_gamma_high_line_inv[year, line]
        - model.v_dec_early_hp[line, year]
    )


def cal_cap_per_mp_line(model, year, line):
    return (
        model.var_gamma_mid_line[year, line]
        == model.par_mid_capacity[line, year]
        + model.var_gamma_mid_line_inv[year, line]
        - model.v_dec_early_mp[line, year]
    )


def cal_total_book_value_per_year(model, year):
    """
    SUM BOOK VALUE OF ALL PIPELINES AT THE TRANSMISSION, HIGH-PRESSURE, AND MID-PRESSURE NETWORK LEVEL.
    For each year.
    """
    return (
        model.var_pi[year]
        == model.var_pi_tra[year] + model.var_pi_high[year] + model.var_pi_mid[year]
    )


def cal_book_value_tra_per_year(model, year):
    """SUM ALL PIPELINES AT THE TRANSMISSION NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_tra[year] == sum(
        model.var_pi_tra_line[line, year] for line in model.set_line_tra
    )


def cal_book_value_high_per_year(model, year):
    """SUM ALL PIPELINES AT THE HIGH-PRESSURE NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_high[year] == sum(
        model.var_pi_high_line[line, year] for line in model.set_line_high
    )


def cal_book_value_mid_per_year(model, year):
    """SUM ALL PIPELINES AT THE MID-PRESSURE NETWORK LEVEL (PER YEAR)"""
    return model.var_pi_mid[year] == sum(
        model.var_pi_mid_line[line, year] for line in model.set_line_mid
    )


def cal_book_value_tra_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_tra_line[line, year]
        == model.par_book_value_tra[line, year]
        + model.par_depreciation_tra[line, year] * model.var_pi_tra_line_inv[line]
    )


def cal_book_value_high_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_high_line[line, year]
        == model.par_book_value_high[line, year]
        + model.par_depreciation_high[line, year] * model.var_pi_high_line_inv[line]
    )


def cal_book_value_mid_line(model, year, line):
    """TOTAL BOOK VALUE == EXISTING + REFURBISHMENT"""
    return (
        model.var_pi_mid_line[line, year]
        == model.par_book_value_mid[line, year]
        + model.par_depreciation_mid[line, year] * model.var_pi_mid_line_inv[line]
    )


def cal_investment_costs_per_tra_line(model, line):
    _inv_year = model.par_year_of_inv_tra[line]
    return (
        model.var_pi_tra_line_inv[line]
        == model.par_ref_tra
        * model.par_tra_length[line]
        * model.var_gamma_tra_line_inv[_inv_year, line]
    )


def cal_investment_costs_per_high_line(model, line):
    _inv_year = model.par_year_of_inv_hp[line]
    return (
        model.var_pi_high_line_inv[line]
        == model.par_ref_high
        * model.par_high_length[line]
        * model.var_gamma_high_line_inv[_inv_year, line]
    )


def cal_investment_costs_per_mid_line(model, line):
    _inv_year = model.par_year_of_inv_mp[line]
    return (
        model.var_pi_mid_line_inv[line]
        == model.par_ref_mid
        * model.par_mid_length[line]
        * model.var_gamma_mid_line_inv[_inv_year, line]
    )


def set_bounds_of_gamma_inv_transmission(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_tra[line]
    if year < _inv_year:
        return model.var_gamma_tra_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_tra_line_inv[year, line]
            == model.var_gamma_tra_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def set_bounds_of_gamma_inv_high(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_hp[line]
    if year < _inv_year:
        return model.var_gamma_high_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_high_line_inv[year, line]
            == model.var_gamma_high_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def set_bounds_of_gamma_inv_mid(model, line, year):
    """
    - Refurbished pipeline capacity set to 0 before year of investment
    - Constant capacity after year of investment
    """
    _inv_year = model.par_year_of_inv_mp[line]
    if year < _inv_year:
        return model.var_gamma_mid_line_inv[year, line] == 0
    elif year > _inv_year:
        return (
            model.var_gamma_mid_line_inv[year, line]
            == model.var_gamma_mid_line_inv[year - 1, line]
        )
    else:
        return py.Constraint.Skip


def export_from_transmission_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the transmission network level (compressor stations)
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    # lines : alle leitungen die export richtung von knoten n haben
    if n in model.tra_export_lines.keys():
        lines = model.tra_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_tra[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_tra[n, y, m] == model.var_transported_tra[lines[0], y, m]
        )
    else:
        return model.var_export_tra[n, y, m] == sum(
            model.var_transported_tra[line, y, m] for line in lines
        )


def import_from_transmission_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the transmission network level (compressor stations)
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.tra_import_lines.keys():
        lines = model.tra_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_tra[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_tra[n, y, m] == model.var_transported_tra[lines[0], y, m]
        )
    else:
        return model.var_import_tra[n, y, m] == sum(
            model.var_transported_tra[line, y, m] for line in lines
        )


def export_from_high_node(model, n, y, m):
    if n in model.high_export_lines.keys():
        lines = model.high_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_high[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_high[n, y, m] == model.var_transported_high[lines[0], y, m]
        )
    else:
        return model.var_export_high[n, y, m] == sum(
            model.var_transported_high[line, y, m] for line in lines
        )


def import_from_high_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.high_import_lines.keys():
        lines = model.high_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_high[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_high[n, y, m] == model.var_transported_high[lines[0], y, m]
        )
    else:
        return model.var_import_high[n, y, m] == sum(
            model.var_transported_high[line, y, m] for line in lines
        )


def export_from_mid_node(model, n, y, m):
    if n in model.mid_export_lines.keys():
        lines = model.mid_export_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_export_mid[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_export_mid[n, y, m] == model.var_transported_mid[lines[0], y, m]
        )
    else:
        return model.var_export_mid[n, y, m] == sum(
            model.var_transported_mid[line, y, m] for line in lines
        )


def import_from_mid_node(model, n, y, m):
    """
    model : pyomo.ConcreteModel
    n : node at the high-pressure network level
    y : year
    m : month

    Return : Constraint (12) (Part 1)
    """
    if n in model.mid_import_lines.keys():
        lines = model.mid_import_lines[n]
    else:
        lines = []
    _length = len(lines)

    if _length == 0:
        return model.var_import_mid[n, y, m] == 0
    elif _length == 1:
        return (
            model.var_import_mid[n, y, m] == model.var_transported_mid[lines[0], y, m]
        )
    else:
        return model.var_import_mid[n, y, m] == sum(
            model.var_transported_mid[line, y, m] for line in lines
        )


def positive_bound_per_tra_line(model, p, y, m):
    return model.var_transported_tra[p, y, m] <= model.var_gamma_tra_line[y, p]


def positive_bound_per_high_line(model, p, y, m):
    if (m == 1) or (m == 12):
        return 1.1 * model.var_transported_high[p, y, m] <= model.var_gamma_high_line[y, p]
    else:
        return model.var_transported_high[p, y, m] <= model.var_gamma_high_line[y, p]


def positive_bound_per_mid_line(model, p, y, m):
    if (m == 1) or (m == 12):
        return 1.1 * model.var_transported_mid[p, y, m] <= model.var_gamma_mid_line[y, p]
    else:
        return model.var_transported_mid[p, y, m] <= model.var_gamma_mid_line[y, p]


def negative_bound_per_tra_line(model, p, y, m):
    return -model.var_transported_tra[p, y, m] <= model.var_gamma_tra_line[y, p]


def negative_bound_per_high_line(model, p, y, m):
    if (m == 1) or (m == 12):
        return 1.1 * (-model.var_transported_high[p, y, m]) <= model.var_gamma_high_line[y, p]
    else:
        return -model.var_transported_high[p, y, m] <= model.var_gamma_high_line[y, p]


def negative_bound_per_mid_line(model, p, y, m):
    if (m == 1) or (m == 12):
        return 1.1 * (-model.var_transported_mid[p, y, m]) <= model.var_gamma_mid_line[y, p]
    else:
        return -model.var_transported_mid[p, y, m] <= model.var_gamma_mid_line[y, p]


def gas_balance_constraint_transmission(model, n, y, m):
    if n not in model.set_delivery_tra_hp:
        """Consequently, node n is only connected to the transmission network level"""
        return (
            model.var_source_tra[n, y, m]
            - model.var_demand_tra[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_tra[n, y, m] - model.var_import_tra[n, y, m])
            == 0
        )
    else:
        """Node n is connected to both, the transmission and high-pressure network level"""
        return (
            model.var_source_tra[n, y, m]
            - model.var_demand_tra[n, y, m]
            - model.var_del_tra_high[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_tra[n, y, m] - model.var_import_tra[n, y, m])
            == 0
        )


def gas_balance_con_high_pressure(model, n, y, m):
    # Knoten ist mit der Fernleitung verbunden! Fern & NE1
    if (n in model.set_delivery_tra_hp) and (n not in model.set_delivery_hp_mp):
        """
        Node n is only connected to the transmission and high-pressure network level. 
        Consequently, this node does not supply mid-pressure gas demand
        """
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                - model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )
    # Knoten ist nur an der Netzebene 1 angeschlossen! NE1
    elif (n not in model.set_delivery_tra_hp) and (n not in model.set_delivery_hp_mp):
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                - model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )
    # Knoten ist nur mit Netzebene 1 und Netzebene 2 verbunden! NE1 & NE2
    elif (n not in model.set_delivery_tra_hp) and (n in model.set_delivery_hp_mp):
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                - model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )
    # FERN & NE1 & NE2
    else:
        if n in model.set_storage:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                - model.var_storage_in_out[n, y, m]
                == 0
            )
        else:
            return (
                model.var_source_high[n, y, m]
                + model.var_del_tra_high[n, y, m]
                - model.var_demand_high[n, y, m]
                - model.var_del_high_mid[n, y, m]
                - model.par_total_peak_factor[m]
                * (model.var_export_high[n, y, m] - model.var_import_high[n, y, m])
                == 0
            )


def gas_balance_con_mid_pressure(model, n, y, m):
    if n not in model.set_delivery_hp_mp:
        """Node is only connected to the mid-pressure network level"""
        return (
            model.var_source_mid[n, y, m]
            - model.var_demand_mid[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_mid[n, y, m] - model.var_import_mid[n, y, m])
            == 0
        )
    else:
        return (
            model.var_source_mid[n, y, m]
            + model.var_del_high_mid[n, y, m]
            - model.var_demand_mid[n, y, m]
            - model.par_total_peak_factor[m]
            * (model.var_export_mid[n, y, m] - model.var_import_mid[n, y, m])
            == 0
        )


"""STORAGE CONSTRAINTS"""


def gas_balance_con_storage(model, n, y, m):
    if (y == 2025) and (m == 1):
        return model.var_storage_soc[n, y, m] == model.var_storage_in_out[n, y, m]
    elif m != 1:
        return (
            model.var_storage_soc[n, y, m]
            == model.var_storage_soc[n, y, m - 1]
            + model.var_storage_in_out[n, y, m]
        )
    elif m == 1:
        return (
            model.var_storage_soc[n, y, m]
            == model.var_storage_soc[n, y - 1, 12]
            + model.var_storage_in_out[n, y, m]
        )


def state_of_charge_upper_bound(model, n, y, m):
    _data = model.storage
    return (
        model.var_storage_soc[n, y, m] <= _data.loc[_data.Node == n]["Capacity"].item()
    )


"""REVENUES CONSTRAINTS"""


def revenues_high_pressure_level(model, n, y, m):
    # return (
    #     model.var_revenues_high[n, y, m]
    #     == model.var_demand_high[n, y, m] * model.par_gas_prices[y, 4]
    # )
    return model.var_revenues_high[n, y, m] == model.var_demand_high[n, y, m] * 0


def revenues_mid_pressure_level(model, n, y, m):
    # return (
    #     model.var_revenues_mid[n, y, m]
    #     == model.var_demand_mid[n, y, m] * model.par_gas_prices[y, 4]
    # )
    return model.var_revenues_mid[n, y, m] == model.var_demand_mid[n, y, m] * 0


def revenues_per_year(model, y):
    _high = sum(
        model.var_revenues_high[n, y, m]
        for n in model.set_node_hp
        for m in model.set_time_unit
    )
    _mid = sum(
        model.var_revenues_mid[n, y, m]
        for n in model.set_node_mp
        for m in model.set_time_unit
    )
    return model.var_rev[y] == _high + _mid


"""DEMAND SATISFACTION CONSTRAINTS"""


def meet_tra_gas_demand(model, n, y, m):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Since no revenues are gained by supplying gas demand at the transmission network level, the corresponding (transmission)
    demand has to be covered (hard constrained).

    Returns
    -------
    pyomo.Constraint.

    """

    return model.var_demand_tra[n, y, m] == model.par_demand_tra[n, y, m]


def demand_upper_bound_high(model, n, y, m):
    """

    Parameters
    ----------
    model : pyomo.ConcreteModel
        Instance of a model.
    n : pyomo.Set
        Node.
    y : pyomo.Set
        Year.
    m : pyomo.Set
        Month.

    Since the supplied demand at the high-pressure network level results in revenues which are considered in the objective function, the covered demand needs to be limited by the demand paramater.

    Returns
    -------
    pyomo.Constraint.

    """

    return (
        model.var_demand_high[n, y, m] + model.var_demand_not_supplied_high[n, y, m]
        == model.par_demand_high[n, y, m]
    )


def demand_upper_bound_mid(model, n, y, m):
    if n in ['Feldkirch', 'Höchst']:
        return model.var_demand_mid[n, y, m] == model.par_demand_mid[n, y, m]
    else:
        return (
            model.var_demand_mid[n, y, m] + model.var_demand_not_supplied_mid[n, y, m]
            == model.par_demand_mid[n, y, m]
        )


def max_annual_source_per_node_tra(model, n, y):
    return (
        sum(model.var_source_tra[n, y, month] for month in model.set_time_unit)
        <= model.par_source_tra[n, y]
    )


def max_annual_source_per_node_high(model, n, y):
    return (
        sum(model.var_source_high[n, y, month] for month in model.set_time_unit)
        <= model.par_source_hp[n, y]
    )


def max_monthly_source_high_node(model, node, year, month):
    return model.var_source_high[node, year, month] <= model.par_source_hp[node, year]


def max_monthly_source_mid_node(model, node, year, month):
    return model.var_source_mid[node, year, month] <= model.par_source_mp[node, year]


def max_annual_source_per_node_mid(model, n, y):
    return (
        sum(model.var_source_mid[n, y, month] for month in model.set_time_unit)
        <= model.par_source_mp[n, y]
    )


def total_spendings_per_year(model, year):
    return model.var_gas_purchase[year] == sum(
        model.var_del_tra_high[node, year, month] * 0
        for node in model.set_delivery_tra_hp
        for month in model.set_time_unit
    )


def total_value_of_lost_load(model, year):
    return model.var_value_of_lost_load[year] == sum(
        model.var_value_of_lost_load_high[node, year, month]
        for node in model.set_node_hp
        for month in model.set_time_unit
    ) + sum(
        model.var_value_of_lost_load_mid[node, year, month]
        for node in model.set_node_mp
        for month in model.set_time_unit
    )


def value_of_lost_load_high(model, node, year, time):
    return (
        model.var_value_of_lost_load_high[node, year, time]
        == model.par_value_of_lost_load_high[year]
        * model.var_demand_not_supplied_high[node, year, time]
    )


def value_of_lost_load_mid(model, node, year, time):
    return (
        model.var_value_of_lost_load_mid[node, year, time]
        == model.par_value_of_lost_load_mid[year]
        * model.var_demand_not_supplied_mid[node, year, time]
    )


def lumpiness_tra(model, tra_line):
    _inv_year = model.par_year_of_inv_tra[tra_line]
    return 13877 * model.lumpiness_tra[tra_line] <= model.var_gamma_tra_line_inv[_inv_year, tra_line]


def link_bdv_and_cap_tra(model, tra_line):
    _inv_year = model.par_year_of_inv_tra[tra_line]
    return model.var_gamma_tra_line_inv[_inv_year, tra_line] <= model.lumpiness_tra[tra_line] * 60000


def lumpiness_high(model, hp_line):
    _inv_year = model.par_year_of_inv_hp[hp_line]
    return 400 * model.lumpiness_high[hp_line] <= model.var_gamma_high_line_inv[_inv_year, hp_line]


def link_bdv_and_cap_high(model, hp_line):
    _inv_year = model.par_year_of_inv_hp[hp_line]
    return model.var_gamma_high_line_inv[_inv_year, hp_line] <= model.lumpiness_high[hp_line] * 30000


def lumpiness_mid(model, mp_line):
    _inv_year = model.par_year_of_inv_mp[mp_line]
    return 60 * model.lumpiness_mid[mp_line] <= model.var_gamma_mid_line_inv[_inv_year, mp_line]


def link_bdv_and_cap_mid(model, mp_line):
    _inv_year = model.par_year_of_inv_mp[mp_line]
    return model.var_gamma_mid_line_inv[_inv_year, mp_line] <= model.lumpiness_mid[mp_line] * 15000


def green_gas_constraint(model, node, year, month):

    # Meeting vom 23.01.2023
    # Beim Szenario "Grünes Methan" gibt es keine Entkopplung (!)
    # Bei den restlichen Szenario ist die Fernleitungsebene von NE1 & 2 entkoppelt.
    # AKTIVIEREN BZW. DEAKTIVIEREN DIESER NEBENBEDINGUNG

    if year >= 2040:
        return model.var_del_tra_high[node, year, month] == 0
    else:
        return py.Constraint.Skip


def con_quantity_src_not_used_hp(model, node, year):
    _annual = sum(
        model.var_source_high[node, year, month] for month in model.set_time_unit
    )
    return (
        model.var_VoLL_src_hp[node, year]
        == (model.par_source_hp[node, year] - _annual) * 500
    )


def limit_demand_not_supplied_high_2040(model, node, year):
    if year == 2040:
        if node == 'Innsbruck':
            return py.Constraint.Skip
        else:
            _annual = sum(model.var_demand_not_supplied_high[node, year, month] for month in model.set_time_unit)
            return _annual <= 40000
    else:
        return py.Constraint.Skip


def limit_demand_not_supplied_mid_2040(model, node, year):
    if year == 2040:
        if node == 'Innsbruck':
            return py.Constraint.Skip
        else:
            _annual = sum(model.var_demand_not_supplied_mid[node, year, month] for month in model.set_time_unit)
            return _annual <= 40000
    else:
        return py.Constraint.Skip


def con_quantity_src_not_used_mp(model, node, year):
    if (node == "Hörbranz") or (node == "Kufstein") or (node == "Vils"):
        return model.var_VoLL_src_mp[node, year] == 0
    else:
        _annual = sum(
            model.var_source_mid[node, year, month] for month in model.set_time_unit
        )
        return (
            model.var_VoLL_src_mp[node, year]
            == (model.par_source_mp[node, year] - _annual) * 500
        )


def con_src_not_year(model, year):
    _value = sum(model.var_VoLL_src_hp[node, year] for node in model.set_node_hp) + sum(
        model.var_VoLL_src_mp[node1, year] for node1 in model.set_node_mp
    )
    return model.var_VoLL_SOURCE[year] == _value


"""NEBENBEDINGUNGEN FÜR VORZEITIGE STILLLEGUNG"""


def set_early_20xx_mid_to_zero(model, line, year):
    if model.par_year_of_inv_mp[line] <= 2040:
        if year == 2030:
            return model.v_bd_early_mp_2030[line] == 0
        elif year == 2035:
            return model.v_bd_early_mp_2035[line] == 0
        elif year == 2040:
            return model.v_bd_early_mp_2040[line] == 0
        else:
            return py.Constraint.Skip
    else:
        return py.Constraint.Skip


def set_early_20xx_high_to_zero(model, line, year):
    if model.par_year_of_inv_hp[line] <= 2040:
        if year == 2030:
            return model.v_bd_early_hp_2030[line] == 0
        elif year == 2035:
            return model.v_bd_early_hp_2035[line] == 0
        elif year == 2040:
            return model.v_bd_early_hp_2040[line] == 0
        else:
            return py.Constraint.Skip
    else:
        return py.Constraint.Skip


def early_decom_hp(model, line, year):
    if model.par_year_of_inv_hp[line] > 2040:
        if year < 2030:
            return model.v_dec_early_hp[line, year] == 0
        elif year == 2030:
            return (
                model.v_dec_early_hp[line, year]
                == model.v_bd_early_hp_2030[line] * model.par_high_capacity[line, year]
            )
        elif (year > 2030) and (year < 2035):
            return model.v_dec_early_hp[line, year] == model.v_dec_early_hp[line, 2030]
        elif year == 2035:
            return (
                model.v_dec_early_hp[line, year]
                == model.v_dec_early_hp[line, 2030]
                + model.v_bd_early_hp_2035[line] * model.par_high_capacity[line, year]
            )
        elif (year > 2035) and (year < 2040):
            return model.v_dec_early_hp[line, year] == model.v_dec_early_hp[line, 2035]
        elif year == 2040:
            return (
                model.v_dec_early_hp[line, year]
                == model.v_dec_early_hp[line, 2035]
                + model.v_bd_early_hp_2040[line] * model.par_high_capacity[line, year]
            )
        elif year < model.par_year_of_inv_hp[line]:
            return model.v_dec_early_hp[line, year] == model.v_dec_early_hp[line, 2040]
        else:
            return model.v_dec_early_hp[line, year] == 0
    else:
        return model.v_dec_early_hp[line, year] == 0


def early_decom_mp(model, line, year):
    if model.par_year_of_inv_mp[line] > 2040:
        if year < 2030:
            return model.v_dec_early_mp[line, year] == 0
        elif year == 2030:
            return (
                model.v_dec_early_mp[line, year]
                == model.v_bd_early_mp_2030[line] * model.par_mid_capacity[line, year]
            )
        elif (year > 2030) and (year < 2035):
            return model.v_dec_early_mp[line, year] == model.v_dec_early_mp[line, 2030]
        elif year == 2035:
            return (
                model.v_dec_early_mp[line, year]
                == model.v_dec_early_mp[line, 2030]
                + model.v_bd_early_mp_2035[line] * model.par_mid_capacity[line, year]
            )
        elif (year > 2035) and (year < 2040):
            return model.v_dec_early_mp[line, year] == model.v_dec_early_mp[line, 2035]
        elif year == 2040:
            return (
                model.v_dec_early_mp[line, year]
                == model.v_dec_early_mp[line, 2035]
                + model.v_bd_early_mp_2040[line] * model.par_mid_capacity[line, year]
            )
        elif year < model.par_year_of_inv_mp[line]:
            return model.v_dec_early_mp[line, year] == model.v_dec_early_mp[line, 2040]
        else:
            return model.v_dec_early_mp[line, year] == 0
    else:
        return model.v_dec_early_mp[line, year] == 0


def early_decom_binary_sum_1_high(model, line):
    return (
        model.v_bd_early_hp_2030[line]
        + model.v_bd_early_hp_2035[line]
        + model.v_bd_early_hp_2040[line]
        <= 1
    )


def early_decom_binary_sum_1_mid(model, line):
    return (
        model.v_bd_early_mp_2030[line]
        + model.v_bd_early_mp_2035[line]
        + model.v_bd_early_mp_2040[line]
        <= 1
    )


def gesamte_abschreibung_pro_jahr(model, year):
    return model.v_abschreibung[year] == sum(
        model.v_tra_abschreibung[t_line, year] for t_line in model.set_line_tra
    ) + sum(
        model.v_hp_abschreibung[h_line, year] for h_line in model.set_line_high
    ) + sum(
        model.v_mp_abschreibung[m_line, year] for m_line in model.set_line_mid
    )


def tra_abschreibung_pro_leitung(model, line, year):
    # CHECK IF YEAR IS BEFORE INVESTMENT YEAR ==> IF YES, THEN NO DEPRECIATION
    if year <= model.par_year_of_inv_tra[line]:
        return model.v_tra_abschreibung[line, year] == 0
    # NEW INVESTMENTS ARE DEPRECIATED FOR 20 YEARS!
    elif year <= (model.par_year_of_inv_tra[line] + 20):
        return (
            model.v_tra_abschreibung[line, year] == model.var_pi_tra_line_inv[line] / 20
        )
    else:
        return model.v_tra_abschreibung[line, year] == 0


def hp_abschreibung_pro_leitung(model, line, year):
    if year <= model.par_year_of_inv_hp[line]:
        return model.v_hp_abschreibung[line, year] == 0
    elif year <= model.par_year_of_inv_hp[line] + 20:
        return (
            model.v_hp_abschreibung[line, year] == model.var_pi_high_line_inv[line] / 20
        )
    else:
        return model.v_hp_abschreibung[line, year] == 0


def mp_abschreibung_pro_leitung(model, line, year):
    if year <= model.par_year_of_inv_mp[line]:
        return model.v_mp_abschreibung[line, year] == 0
    elif year <= model.par_year_of_inv_mp[line] + 20:
        return (
            model.v_mp_abschreibung[line, year] == model.var_pi_mid_line_inv[line] / 20
        )
    else:
        return model.v_mp_abschreibung[line, year] == 0


'''CLUSTER CONSTRAINTS!'''


def high_2030_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_hp[line] > 2040:
        _data = model.high
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_high_2030[_cluster] == model.v_bd_early_hp_2030[line]
    else:
        return py.Constraint.Skip


def high_2035_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_hp[line] > 2040:
        _data = model.high
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_high_2035[_cluster] == model.v_bd_early_hp_2035[line]
    else:
        return py.Constraint.Skip


def high_2040_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_hp[line] > 2040:
        _data = model.high
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_high_2040[_cluster] == model.v_bd_early_hp_2040[line]
    else:
        return py.Constraint.Skip


def mid_2030_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_mp[line] > 2040:
        _data = model.mid
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_mid_2030[_cluster] == model.v_bd_early_mp_2030[line]
    else:
        return py.Constraint.Skip


def mid_2035_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_mp[line] > 2040:
        _data = model.mid
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_mid_2035[_cluster] == model.v_bd_early_mp_2035[line]
    else:
        return py.Constraint.Skip


def mid_2040_cluster_and_line_equal(model, line):
    if model.par_year_of_inv_mp[line] > 2040:
        _data = model.mid
        _cluster = _data.at[line, "cluster_km"]
        return model.bd_cluster_mid_2040[_cluster] == model.v_bd_early_mp_2040[line]
    else:
        return py.Constraint.Skip


def c_completely_discharged_storage_2039(model, storage, year, month):
    # if year >= 2040:
    #     return model.var_storage_soc[storage, year, month] == 0
    # else:
    #     return py.Constraint.Skip
    if (year == 2039) and (month == 12):
        return model.var_storage_soc[storage, year, month] == 0
    else:
        return py.Constraint.Skip


def c_frei_werdende_kapazitäten_für_h2_von_netzebene1(model, line, year, month):
    _data = model.high
    _cluster = _data.at[line, "cluster_km"]

    if _cluster == 20:
        if year >= 2030:
            return model.var_transported_high[line, year, month] == 0
        else:
            return py.Constraint.Skip
    elif _cluster == 25:
        if year >= 2035:
            return model.var_transported_high[line, year, month] == 0
        else:
            return py.Constraint.Skip
    else:
        return py.Constraint.Skip


def c_frei_werdende_kapazitäten_für_h2_von_netzebene2(model, line, year, month):
    _data = model.mid
    _cluster = _data.at[line, "cluster_km"]

    if _cluster in [55, 446, 143]:
        if year >= 2030:
            return model.var_transported_mid[line, year, month] == 0
        else:
            return py.Constraint.Skip

    elif _cluster in [90, 341]:
        if year >= 2035:
            return model.var_transported_mid[line, year, month] == 0
        else:
            return py.Constraint.Skip
    else:
        return py.Constraint.Skip


def c_freiwerdender_h2_speicher_gampern(model, node, year, month):
    if (node == 'Gampern') and (year >= 2030):
        return model.var_storage_soc[node, year, month] == 0
    else:
        return py.Constraint.Skip


def c_no_early_decom_high_30(model, cluster):
    if cluster == 20:
        return model.bd_cluster_high_2030[cluster] == 1
    else:
        return model.bd_cluster_high_2030[cluster] == 0


def c_no_early_decom_high_35(model, cluster):
    if cluster == 25:
        return model.bd_cluster_high_2035[cluster] == 1
    else:
        return model.bd_cluster_high_2035[cluster] == 0


def c_no_early_decom_mid_30(model, cluster):
    if cluster in [55, 446, 143]:
        return model.bd_cluster_mid_2030[cluster] == 1
    else:
        return model.bd_cluster_mid_2030[cluster] == 0


def c_no_early_decom_mid_35(model, cluster):
    if cluster in [90, 341]:
        return model.bd_cluster_mid_2035[cluster] == 1
    else:
        return model.bd_cluster_mid_2035[cluster] == 0


def add(model=None):

    """ADD CONSTRAINTS TO MODEL INSTANCE"""
    model.con_capex = py.Constraint(
        model.set_year,
        rule=cal_capex_per_year,
        doc="CHECKED: Kalkulatorische Zinsen = WACC x Buchwert"
    )
    model.con_fixed = py.Constraint(
        model.set_year,
        rule=cal_total_fixed_costs_per_year,
        doc="CHECLED: Betriebskosten: = Summe (Fernleitung, Hochdruck, Mitteldruck)"
    )
    model.con_fixed_tra = py.Constraint(
        model.set_year,
        rule=cal_fixed_costs_tra,
        doc="CHECKED: Betriebskosten Fernleitung = Para x Gesamtkapazität"
    )
    model.con_fixed_high = py.Constraint(
        model.set_year,
        rule=cal_fixed_costs_high,
        doc="CHECKED: Fix_High = c_fix x Total capacity"
    )
    model.con_fixed_mid = py.Constraint(
        model.set_year,
        rule=cal_fixed_costs_mid,
        doc="CHECKED: Fix_Mid = c_fix x Total capacity"
    )

    model.con_total_tra_cap = py.Constraint(
        model.set_year,
        rule=cal_total_tra_capacity,
        doc="CHECKED: Calculate total transmission pipeline capacity"
    )
    model.con_total_high_cap = py.Constraint(
        model.set_year,
        rule=cal_total_high_capacity,
        doc="CHECKED: Calculate total high-pressure pipeline capacity"
    )
    model.con_total_mid_cap = py.Constraint(
        model.set_year,
        rule=cal_total_mid_capacity,
        doc="CHECKED: Calculate total mid-pressure pipeline capacity",
    )

    model.con_total_tra_cap_line = py.Constraint(
        model.set_year,
        model.set_line_tra,
        rule=cal_cap_per_tra_line,
        doc="CHECKED: Total pipeline capacity = Initial + Refurbished",
    )
    model.con_total_high_cap_line = py.Constraint(
        model.set_year,
        model.set_line_high,
        rule=cal_cap_per_hp_line,
        doc="CHECKED: Total pipeline capacity = Initial + Refurbished",
    )
    model.con_total_mid_cap_line = py.Constraint(
        model.set_year,
        model.set_line_mid,
        rule=cal_cap_per_mp_line,
        doc="CHECKED: Total pipeline capacity = Initial + Refurbished",
    )

    model.con_total_book_val = py.Constraint(
        model.set_year,
        rule=cal_total_book_value_per_year,
        doc="CHECKED: Book-Value = BV_Tra + BV_High + BV_Mid",
    )
    model.con_book_value_tra = py.Constraint(
        model.set_year,
        rule=cal_book_value_tra_per_year,
        doc="CHECKED: Total (Transmission) Book Value",
    )
    model.con_book_value_high = py.Constraint(
        model.set_year,
        rule=cal_book_value_high_per_year,
        doc="CHECKED: Total (High-Pressure) Book Value",
    )
    model.con_book_value_mid = py.Constraint(
        model.set_year,
        rule=cal_book_value_mid_per_year,
        doc="CHECKED: Total (Mid-Pressure) Book Value",
    )

    model.con_book_value_tra_line = py.Constraint(
        model.set_year,
        model.set_line_tra,
        rule=cal_book_value_tra_line,
        doc="CHECKED: Transmission: Book value of pipeline = Existing + Refurbished",
    )
    model.con_book_value_high_line = py.Constraint(
        model.set_year,
        model.set_line_high,
        rule=cal_book_value_high_line,
        doc="CHECKED: High-Pressure: Book value of pipeline = Existing + Refurbished",
    )
    model.con_book_value_mid_line = py.Constraint(
        model.set_year,
        model.set_line_mid,
        rule=cal_book_value_mid_line,
        doc="CHECKED: Mid-Pressure: Book value of pipeline = Existing + Refurbished",
    )

    model.con_inv_tra_line = py.Constraint(
        model.set_line_tra,
        rule=cal_investment_costs_per_tra_line,
        doc="CHECKED: Transmission: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )
    model.con_inv_high_line = py.Constraint(
        model.set_line_high,
        rule=cal_investment_costs_per_high_line,
        doc="CHECKED: High-Pressure: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )
    model.con_inv_mid_line = py.Constraint(
        model.set_line_mid,
        rule=cal_investment_costs_per_mid_line,
        doc="CHECKED: Mid-Pressure: Ref. Investment = [EUR/MW/km] x Length x Capacity",
    )

    model.con_gamma_inv_tra_bounds = py.Constraint(
        model.set_line_tra,
        model.set_year,
        rule=set_bounds_of_gamma_inv_transmission,
        doc="CHECKED: Transmision: Refurbished Capacity. Before investment year 0; after constant.",
    )
    model.con_gamma_inv_high_bounds = py.Constraint(
        model.set_line_high,
        model.set_year,
        rule=set_bounds_of_gamma_inv_high,
        doc="CHECKED: High-Pressure: Refurbished Capacity. Before investment year 0; after constant.",
    )
    model.con_gamma_inv_mid_bounds = py.Constraint(
        model.set_line_mid,
        model.set_year,
        rule=set_bounds_of_gamma_inv_mid,
        doc="CHECKED: Mid-Pressure: Refurbished Capacity. Before investment year 0; after constant.",
    )

    model.con_total_export_per_tra_node = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=export_from_transmission_node,
        doc="CHECKED: Transmission: Total export from one node (sum up all relevant pipelines).",
    )
    model.con_total_export_per_high_node = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=export_from_high_node,
        doc="CHECKED: High-Pressure: Total export from one node (sum up all relevant pipelines).",
    )
    model.con_total_export_per_mid_node = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=export_from_mid_node,
        doc="CHECKED: Mid-Pressure: Total export from one node (sum up all relevant pipelines).",
    )

    model.con_total_import_per_tra_node = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=import_from_transmission_node,
        doc="CHECKED: Transmission: Total import to one node (sum up all relevant pipelines).",
    )
    model.con_total_import_per_high_node = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=import_from_high_node,
        doc="CHECKED: High-Pressure: Total import to one node (sum up all relevant pipelines).",
    )
    model.con_total_import_per_mid_node = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=import_from_mid_node,
        doc="CHECKED: Mid-Pressure: Total import to one node (sum up all relevant pipelines).",
    )

    model.con_positive_capacity_bound_tra = py.Constraint(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_tra_line,
        doc="CHECKED: Transmission: transported amount <= Pipeline capacity; Constraint 14.1; Direction 1.",
    )
    model.con_positive_capacity_bound_high = py.Constraint(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_high_line,
        doc="CHECKED: High-Pressure: transported amount <= Pipeline capacity; Constraint 14.2; Direction 1.",
    )
    model.con_positive_capacity_bound_mid = py.Constraint(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        rule=positive_bound_per_mid_line,
        doc="CHECKED: Mid-Pressure: transported amount <= Pipeline capacity; Constraint 14.3; Direction 1.",
    )
    model.con_negative_capacity_bound_tra = py.Constraint(
        model.set_line_tra,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_tra_line,
        doc="CHECKED: Transmission: transported <= Pipeline capacity; Constraint 15.1; Direction 2.",
    )
    model.con_negative_capacity_bound_high = py.Constraint(
        model.set_line_high,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_high_line,
        doc="CHECKED: High-Pressure: transported amount <= Pipeline capacity; Constraint 15.2; Direction 2.",
    )
    model.con_negative_capacity_bound_mid = py.Constraint(
        model.set_line_mid,
        model.set_year,
        model.set_time_unit,
        rule=negative_bound_per_mid_line,
        doc="CHECKED: Mid-Pressure: transported amount <= Pipeline capacity; Constraint 15.3; Direction 2.",
    )

    model.c_gas_balance_tra = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_constraint_transmission,
        doc="CHECKED: Transmission: Gas balance at one node; Constraint 16.1.",
    )
    model.c_gas_balance_hp = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_high_pressure,
        doc="CHECKED: High-Pressure: Gas balance at one node; Constraint 16.2.",
    )
    model.c_gas_balance_mp = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_mid_pressure,
        doc="CHECKED: Mid-Pressure: Gas balance at one node; Constraint 16.3.",
    )

    model.c_soc_upper_bound = py.Constraint(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        rule=state_of_charge_upper_bound,
        doc="CHECKED: High-Pressure: Max gas storage capacity at one node; Constraint 19b.",
    )
    model.c_soc_in_and_out = py.Constraint(
        model.set_storage,
        model.set_year,
        model.set_time_unit,
        rule=gas_balance_con_storage,
        doc="CHECKED: High-Pressure: State of charge for gas storage at one node; Constraint 19a.",
    )

    model.c_rev_high = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=revenues_high_pressure_level,
        doc="CHECKED: High-Pressure: Revenues = (Supplied) Demand x Factor; Constraint 20.1.",
    )
    model.c_rev_mid = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=revenues_mid_pressure_level,
        doc="CHECKED: Mid-Pressure: Revenues = (Supplied) Demand x Factor; Constraint 20.2.",
    )
    model.c_rev_year = py.Constraint(
        model.set_year,
        rule=revenues_per_year,
        doc="CHECKED: Total Revenues = Sum(Revenues) for all pressure levels; Constraint 21.",
    )
    model.c_equal_tra_demand = py.Constraint(
        model.set_compressor,
        model.set_year,
        model.set_time_unit,
        rule=meet_tra_gas_demand,
        doc="CHECKED: Transmission: Gas demand must be covered.",
    )
    model.c_limit_high_demand = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=demand_upper_bound_high,
        doc="CHECKED: Upper limit of the high-pressure gas demand covered is set by the corresponding input parameter.",
    )
    model.c_limit_mid_demand = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=demand_upper_bound_mid,
        doc="CHECKED: Upper limit of the mid-pressure gas demand covered is set by the corresponding input parameter.",
    )
    model.c_limit_tra_source = py.Constraint(
        model.set_compressor,
        model.set_year,
        rule=max_annual_source_per_node_tra,
        doc="CHECKED: Transmission: Upper limit of annual gas injected at one node.",
    )
    model.c_limit_high_source = py.Constraint(
        model.set_node_hp,
        model.set_year,
        rule=max_annual_source_per_node_high,
        doc="CHECKED: High-Pressure: Upper limit of annual gas injected at one node.",
    )
    model.c_limit_mid_source = py.Constraint(
        model.set_node_mp,
        model.set_year,
        rule=max_annual_source_per_node_mid,
        doc="CHECKED: Mid-Pressure: Upper limit of annual gas injected at one node.",
    )

    model.c_gas_purchase = py.Constraint(
        model.set_year,
        rule=total_spendings_per_year,
        doc="CHECKED: Costs for delivering gas from the transmission into the high-pressure network level.",
    )

    model.c_value_of_lost_load_per_year = py.Constraint(
        model.set_year,
        rule=total_value_of_lost_load,
        doc="CHECKED: Total value of lost load for both high-pressure and mid-pressure gas demands per year.",
    )
    model.c_value_of_lost_load_high = py.Constraint(
        model.set_node_hp,
        model.set_year,
        model.set_time_unit,
        rule=value_of_lost_load_high,
        doc="CHECKED: VoLL at High-Pressure per Node, Year, and Month = Cost Parameter x Gas Demand Not Supplied.",
    )
    model.c_value_of_lost_load_mid = py.Constraint(
        model.set_node_mp,
        model.set_year,
        model.set_time_unit,
        rule=value_of_lost_load_mid,
        doc="CHECKED: VoLL at Mid-Pressure per Node, Year, and Month = Cost Parameter x Gas Demand Not Supplied.",
    )
    model.c_lump_tra = py.Constraint(model.set_line_tra, rule=lumpiness_tra, doc='CHECKED')
    model.c_lump_high = py.Constraint(model.set_line_high, rule=lumpiness_high, doc='CHECKED')
    model.c_lump_mid = py.Constraint(model.set_line_mid, rule=lumpiness_mid, doc='CHECKED')

    model.link_bdv_and_cap_tra = py.Constraint(model.set_line_tra, rule=link_bdv_and_cap_tra)
    model.link_bdv_and_cap_high = py.Constraint(model.set_line_high, rule=link_bdv_and_cap_high)
    model.link_bdv_and_cap_mid = py.Constraint(model.set_line_mid, rule=link_bdv_and_cap_mid)

    model.c_green_gas = py.Constraint(
        model.set_delivery_tra_hp,
        model.set_year,
        model.set_time_unit,
        rule=green_gas_constraint,
        doc='CHECKED'
    )

    model.con_VoLL_hp = py.Constraint(
        model.set_node_hp,
        model.set_year,
        rule=con_quantity_src_not_used_hp,
        doc="CHECKED: VoLL at High-Pressure [EUR / year] = 60 EUR / MWh * (Potential - Used)",
    )
    model.con_VoLL_mp = py.Constraint(
        model.set_node_mp,
        model.set_year,
        rule=con_quantity_src_not_used_mp,
        doc="CHECKED: VoLL at Mid-Pressure [EUR / year] = 60 EUR / MWh * (Potential - Used)",
    )
    model.con_cost_src_not_per_year = py.Constraint(
        model.set_year, rule=con_src_not_year, doc='CHECKED'
    )

    """CONSTRAINTS FÜR FRÜHZEITIGE STILLLEGUNG"""
    model.con_early_decom_hp_1 = py.Constraint(
        model.set_line_high, model.set_year, rule=early_decom_hp, doc='CHECKED'
    )

    model.con_early_decom_mp_1 = py.Constraint(
        model.set_line_mid, model.set_year, rule=early_decom_mp, doc='CHECKED'
    )

    model.con_early_decom_hp_2 = py.Constraint(
        model.set_line_high, rule=early_decom_binary_sum_1_high, doc='CHECKED'
    )

    model.con_early_decom_mp_2 = py.Constraint(
        model.set_line_mid, rule=early_decom_binary_sum_1_mid, doc='CHECKED'
    )
    # _________________________________________
    # CHECKED
    # _________________________________________
    """ABSCHREIBUNG"""
    model.con_total_abschreibung = py.Constraint(
        model.set_year, rule=gesamte_abschreibung_pro_jahr, doc='CHECKED'
    )
    model.con_fernleitung_abschreibung = py.Constraint(
        model.set_line_tra, model.set_year, rule=tra_abschreibung_pro_leitung, doc='CHECKED'
    )
    model.con_high_abschreibung = py.Constraint(
        model.set_line_high, model.set_year, rule=hp_abschreibung_pro_leitung, doc='CHECKED'
    )
    model.con_mid_abschreibung = py.Constraint(
        model.set_line_mid, model.set_year, rule=mp_abschreibung_pro_leitung, doc='CHECKED'
    )
    model.c_set_early_20xx_mid_to_zero = py.Constraint(
        model.set_line_mid, model.set_year, rule=set_early_20xx_mid_to_zero, doc='CHECKED'
    )
    model.c_set_early_20xx_high_to_zero = py.Constraint(
        model.set_line_high, model.set_year, rule=set_early_20xx_high_to_zero, doc='CHECKED'
    )

    """CLUSTER CONSTRAINTS"""
    model.c_high_2030_cluster_and_line_equal = py.Constraint(
        model.set_line_high, rule=high_2030_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_high_2035_cluster_and_line_equal = py.Constraint(
        model.set_line_high, rule=high_2035_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_high_2040_cluster_and_line_equal = py.Constraint(
        model.set_line_high, rule=high_2040_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_mid_2030_cluster_and_line_equal = py.Constraint(
        model.set_line_mid, rule=mid_2030_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_mid_2035_cluster_and_line_equal = py.Constraint(
        model.set_line_mid, rule=mid_2035_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_mid_2040_cluster_and_line_equal = py.Constraint(
        model.set_line_mid, rule=mid_2040_cluster_and_line_equal, doc='CHECKED'
    )
    model.c_max_monthly_source_high_node = py.Constraint(
        model.set_node_hp, model.set_year, model.set_time_unit, rule=max_monthly_source_high_node
    )
    model.c_max_monthly_source_mid_node = py.Constraint(
        model.set_node_mp, model.set_year, model.set_time_unit, rule=max_monthly_source_mid_node
    )
    model.c_completely_discharged_storage_2039 = py.Constraint(
        model.set_storage, model.set_year, model.set_time_unit, rule=c_completely_discharged_storage_2039
    )
    model.c_frei_werdende_kapazitäten_für_h2_von_netzebene1 = py.Constraint(
        model.set_line_high, model.set_year, model.set_time_unit,
        rule=c_frei_werdende_kapazitäten_für_h2_von_netzebene1
    )
    model.c_frei_werdende_kapazitäten_für_h2_von_netzebene2 = py.Constraint(
        model.set_line_mid, model.set_year, model.set_time_unit, rule=c_frei_werdende_kapazitäten_für_h2_von_netzebene2
    )
    model.c_freiwerdender_h2_speicher_gampern = py.Constraint(
        model.set_node_hp, model.set_year, model.set_time_unit, rule=c_freiwerdender_h2_speicher_gampern,
        doc='Methanspeicher GAMPERN wird ab 2030 für H2 verwendet.'
    )
    model.c_no_early_decom_high_30 = py.Constraint(model.set_high_cluster, rule=c_no_early_decom_high_30)
    model.c_no_early_decom_high_35 = py.Constraint(model.set_high_cluster, rule=c_no_early_decom_high_35)
    model.c_no_early_decom_mid_30 = py.Constraint(model.set_mid_cluster, rule=c_no_early_decom_mid_30)
    model.c_no_early_decom_mid_35 = py.Constraint(model.set_mid_cluster, rule=c_no_early_decom_mid_35)

    # LIMIT THE METHANE DEMAND THAT IS NOT COVERED BY 40,000 MWH PER NODE AT MAX.
    model.c_limit_demand_not_supplied_high_2040 = py.Constraint(
        model.set_node_hp,
        model.set_year,
        rule=limit_demand_not_supplied_high_2040,
        doc='Innsbruck excluded'
    )
    model.c_limit_demand_not_supplied_mid_2040 = py.Constraint(
        model.set_node_mp,
        model.set_year,
        rule=limit_demand_not_supplied_mid_2040,
        doc='Innsbruck excluded.'
    )
    return
