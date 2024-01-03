from datetime import datetime
import os
import pandas as pd
import numpy as np
import pyomo.environ as py


def write_IAMC(output_df, model, scenario, region, variable, unit, time, values):
    if isinstance(values, list):
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            }
        )
    else:
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            },
            index=[0],
        )
    output_df = pd.concat([output_df, _df], axis=0)
    # output_df = output_df.append(_df)
    return output_df


def get_values_from_model(variable, index=None):
    value = []
    # key = dict()
    if type(index) == list:
        if len(index) == 2:
            for i1 in index[0]:
                for i2 in index[1]:
                    value.append(np.around(py.value(variable[i1, i2]), 3))
                    # key[(i1, i2)] = np.around(py.value(variable[i1, i2]), 3)
        elif len(index) == 3:
            for i1 in index[0]:
                for i2 in index[1]:
                    for i3 in index[2]:
                        value.append(np.around(py.value(variable[i1, i2, i3]), 3))
                        # key[(i1, i2, i3)] = np.around(py.value(variable[i1, i2, i3]), 3)
    return value


def write_results_to_folder(model=None, scenario=None):
    time = datetime.now().strftime("%Y%m%dT%H%M")
    path = os.path.join("solution", "{}-{}".format(scenario, time))

    if not os.path.exists(path):
        os.makedirs(path)

    df_out = pd.DataFrame()
    _scenario = scenario
    _model = model.name
    # (1) ZIELFUNKTIONSWERT; (2) KALKULATORISCHE ZINSEN; (3) LAUFENDE KOSTEN; (4) BUCHWERT; (5) INVESTITIONEN
    _value = np.around(py.value(model.objective), 0)
    df_out = write_IAMC(
        df_out, _model, _scenario, "Österreich", "NPV", "EUR", "2025", _value
    )

    for year in model.set_year:
        _capital = np.around(model.var_capex[year](), 1)
        _opex = np.around(model.var_opex[year](), 1)
        _buchwert = np.around(model.var_pi[year](), 1)
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            "Österreich",
            "Kapitalkosten (Buchwerte x WACC)",
            "EUR",
            year,
            _capital,
        )
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            "Österreich",
            "Opex (Fixkosten)",
            "EUR",
            year,
            _opex,
        )
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            "Österreich",
            "Buchwert (Gesamt)",
            "EUR",
            year,
            _buchwert,
        )
    for _l in model.set_line_tra:
        _y = model.par_year_of_inv_tra[_l]
        _value = model.var_pi_tra_line_inv[_l]()
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            _l,
            "Transmission|Investitionskosten",
            "EUR",
            _y,
            _value,
        )
    for _l in model.set_line_high:
        _y = model.par_year_of_inv_hp[_l]
        _value = model.var_pi_high_line_inv[_l]()
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            _l,
            "High-Pressure|Investitionskosten",
            "EUR",
            _y,
            _value,
        )
    for _l in model.set_line_mid:
        _y = model.par_year_of_inv_mp[_l]
        _value = model.var_pi_mid_line_inv[_l]()
        df_out = write_IAMC(
            df_out,
            _model,
            _scenario,
            _l,
            "Mid-Pressure|Investitionskosten",
            "EUR",
            _y,
            _value,
        )
    df_out.to_excel(os.path.join(path, "Values.xlsx"), index=False)
    #
    #
    #
    #
    # DISPATCH VON DREI REPRÄSENTATIVEN GEMEINDEN: (1) TIMELKAM; (2) DESSELBRUNN; (3) GAMPERN
    output_iamc = pd.DataFrame()
    _region = ["Hohenberg", "Lilienfeld"]
    year = [2040]
    for _re in _region:
        for _y in year:
            for _m in model.set_time_unit:
                _demand = model.var_demand_mid[_re, _y, _m]()
                output_iamc = write_IAMC(
                    output_iamc,
                    _model,
                    _y,
                    _re,
                    "METHANE|DEMAND SUPPLIED",
                    "MWh",
                    _m,
                    _demand,
                )
                _not_supplied = model.var_demand_not_supplied_mid[_re, _y, _m]()
                output_iamc = write_IAMC(
                    output_iamc,
                    _model,
                    _y,
                    _re,
                    "METHANE|DEMAND NOT SUPPLIED",
                    "MWh",
                    _m,
                    _not_supplied,
                )
                source = model.var_source_mid[_re, _y, _m]()
                output_iamc = write_IAMC(
                    output_iamc,
                    _model,
                    _y,
                    _re,
                    "METHANE|SOURCE|LOCAL|USED",
                    "MWh",
                    _m,
                    source,
                )
                var_import = (
                    model.var_import_mid[_re, _y, _m]()
                    * model.par_total_peak_factor[_m]
                )
                output_iamc = write_IAMC(
                    output_iamc,
                    _model,
                    _y,
                    _re,
                    "METHANE|IMPORT",
                    "MWh",
                    _m,
                    var_import,
                )
                var_export = (
                    model.var_export_mid[_re, _y, _m]()
                    * model.par_total_peak_factor[_m]
                )
                output_iamc = write_IAMC(
                    output_iamc,
                    _model,
                    _y,
                    _re,
                    "METHANE|EXPORT",
                    "MWh",
                    _m,
                    var_export,
                )
    output_iamc.to_excel(
        os.path.join(path, "Dispatch_from_Mid_Node_Hohenberg.xlsx"), index=False
    )
    #
    #
    #
    #
    # MAX. TRANSPORT CAPACITY PER TRANSMISSION, HIGH-, AND MID-PRESSURE NETWORK LEVEL
    """WRITE LINE CAPACITIES TO IAMC FORMAT"""
    df_out = pd.DataFrame()
    for tline in model.set_line_tra:
        for year in model.set_year:
            df_out = write_IAMC(
                df_out,
                _model,
                _scenario,
                tline,
                "Transmission|Pipeline capacity",
                "MW",
                year,
                py.value(model.var_gamma_tra_line[year, tline]),
            )
    for hline in model.set_line_high:
        for year in model.set_year:
            df_out = write_IAMC(
                df_out,
                _model,
                _scenario,
                hline,
                "High-Pressure|Pipeline capacity",
                "MW",
                year,
                py.value(model.var_gamma_high_line[year, hline]),
            )
    for mline in model.set_line_mid:
        for year in model.set_year:
            df_out = write_IAMC(
                df_out,
                _model,
                _scenario,
                mline,
                "Mid-Pressure|Pipeline capacity",
                "MW",
                year,
                py.value(model.var_gamma_mid_line[year, mline]),
            )
    df_out.to_excel(os.path.join(path, "Pipelines_Capacity.xlsx"), index=False)

    # # LEITUNGSLÄNGEN
    # _out = pd.DataFrame()
    # for tline in model.set_line_tra:
    #     _out = write_IAMC(
    #         _out,
    #         _model,
    #         _scenario,
    #         tline,
    #         "Transmission|Line length",
    #         "Km",
    #         2025,
    #         model.par_tra_length[tline],
    #     )
    #
    # for high_line in model.set_line_high:
    #     _out = write_IAMC(
    #         _out,
    #         _model,
    #         _scenario,
    #         high_line,
    #         "High-Pressure|Line length",
    #         "Km",
    #         2025,
    #         model.par_high_length[high_line],
    #     )
    #
    # for mid_line in model.set_line_mid:
    #     _out = write_IAMC(
    #         _out,
    #         _model,
    #         _scenario,
    #         mid_line,
    #         "Mid-Pressure|Line length",
    #         "Km",
    #         2025,
    #         model.par_mid_length[mid_line],
    #     )
    #
    # _out.to_excel(os.path.join(path, "PAR_LINELENGTH_in_KM.xlsx"), index=False)

    # BENCHMARKING OF THE WHOLE METHANE NETWORK (i.e., Gesamtnetz)
    _out = pd.DataFrame()
    for _year in [2030, 2035, 2040]:
        _GWxhxkm_tra = 0
        for tline in model.set_line_tra:
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_tra[tline, _year, month])
                _GWxhxkm_tra += np.absolute(_val) * model.par_tra_length[tline] * 720
                _out = write_IAMC(
                    _out,
                    _model,
                    _scenario,
                    tline,
                    "Transmission|GWhkm",
                    "GW*h*km",
                    _year,
                    np.round(_GWxhxkm_tra / 1000, 0),
                )
        _GWxhxkm_high = 0
        for hline in model.set_line_high:
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_high[hline, _year, month])
                _GWxhxkm_high += np.absolute(_val) * model.par_high_length[hline] * 720
                _out = write_IAMC(
                    _out,
                    _model,
                    _scenario,
                    hline,
                    "High-Pressure|GWhkm",
                    "GW*h*km",
                    _year,
                    np.round(_GWxhxkm_high / 1000, 0),
                )
        _GWxhxkm_mid = 0
        for mline in model.set_line_mid:
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_mid[mline, _year, month])
                _GWxhxkm_mid += np.absolute(_val) * model.par_mid_length[mline] * 720
                _out = write_IAMC(
                    _out,
                    _model,
                    _scenario,
                    mline,
                    "Mid-Pressure|GWhkm",
                    "GW*h*km",
                    _year,
                    np.round(_GWxhxkm_mid / 1000, 0),
                )
    _out.to_excel(os.path.join(path, "Whole_Network_GWhkm.xlsx"), index=False)

    # UTILIZATION RATE OF METHANE PIPELINES
    _out = pd.DataFrame()
    for _year in [2030, 2035, 2040]:
        for t_line in model.set_line_tra:
            full_value = py.value(model.var_gamma_tra_line[_year, t_line]) * 720 * 12
            if full_value > 0:
                _used = 0
                for month in model.set_time_unit:
                    _val = py.value(model.var_transported_tra[t_line, _year, month])
                    _used += np.absolute(_val) * 720
                _rate = np.round((_used / full_value) * 100, 1)
            else:
                _rate = None
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                t_line,
                "Transmission|Pipeline|Utilization",
                "%",
                _year,
                _rate,
            )

        for h_line in model.set_line_high:
            full_value = py.value(model.var_gamma_high_line[_year, h_line]) * 720 * 12
            if full_value > 0:
                _used = 0
                for month in model.set_time_unit:
                    _val = py.value(model.var_transported_high[h_line, _year, month])
                    _used += np.absolute(_val) * 720
                _rate = np.round((_used / full_value) * 100, 1)
            else:
                _rate = None
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                h_line,
                "High-Pressure|Pipeline|Utilization",
                "%",
                _year,
                _rate,
            )

        for m_line in model.set_line_mid:
            full_value = py.value(model.var_gamma_mid_line[_year, m_line]) * 720 * 12
            if full_value > 0:
                _used = 0
                for month in model.set_time_unit:
                    _val = py.value(model.var_transported_mid[m_line, _year, month])
                    _used += np.absolute(_val) * 720
                _rate = np.round((_used / full_value) * 100, 1)
            else:
                _rate = None
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                m_line,
                "Mid-Pressure|Pipeline|Utilization",
                "%",
                _year,
                _rate,
            )
    _out.to_excel(
        os.path.join(path, "Utilization_in_percent_per_year.xlsx"), index=False
    )

    # Auslastung der Fernleitung auf Basis der Jahresdauerlinie
    for _year in [2030, 2035, 2040]:
        _out = pd.DataFrame()
        for t_line in model.set_line_tra:
            full_value = py.value(model.var_gamma_tra_line[_year, t_line]) * 720
            for month in model.set_time_unit:
                if full_value > 0:
                    _val = np.absolute(
                        py.value(model.var_transported_tra[t_line, _year, month]) * 720
                    )
                    _rate = np.round((_val / full_value) * 100, 1)
                else:
                    _rate = None

                _out = write_IAMC(
                    _out,
                    _model,
                    _scenario,
                    t_line,
                    "Transmission|Pipeline|Utilization",
                    "%",
                    month,
                    _rate,
                )

        _string = "720h_Blocks_Transmission_" + str(_year) + ".xlsx"
        _out.to_excel(os.path.join(path, _string), index=False)

    """WRITE MAXIMUM DISPATCH CAPACITY TO IAMC FORMAT"""
    _out = pd.DataFrame()
    for tline in model.set_line_tra:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_tra[tline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(
            _out,
            _model,
            _scenario,
            tline,
            "Transmission|Pipeline capacity|Max",
            "MW",
            2025,
            _max,
        )

    for hline in model.set_line_high:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_high[hline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(
            _out,
            _model,
            _scenario,
            hline,
            "High-Pressure|Pipeline capacity|Max",
            "MW",
            2025,
            _max,
        )

    for mline in model.set_line_mid:
        _max = 0
        for month in model.set_time_unit:
            _val = py.value(model.var_transported_mid[mline, 2025, month])
            if np.absolute(_val) > _max:
                _max = np.absolute(_val)
        _out = write_IAMC(
            _out,
            _model,
            _scenario,
            mline,
            "Mid-Pressure|Pipeline capacity|Max",
            "MW",
            2025,
            _max,
        )
    _out.to_excel(os.path.join(path, "InitCapacities2025.xlsx"), index=False)

    #
    #
    #
    #

    _out = pd.DataFrame()
    for year in [2025, 2030, 2035, 2040, 2045]:
        for node in model.set_node_hp:
            _yearly = sum(
                py.value(model.var_demand_not_supplied_high[node, year, month])
                for month in model.set_time_unit
            )
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                node,
                "High-Pressure|Not Supplied|Per Year",
                "MWh",
                year,
                _yearly,
            )
        for node in model.set_node_mp:
            _value = sum(
                py.value(model.var_demand_not_supplied_mid[node, year, month])
                for month in model.set_time_unit
            )
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                node,
                "Mid-Pressure|Not Supplied|Per Year",
                "MWh",
                year,
                _value,
            )
    _out.to_excel(
        os.path.join(path, "methane_demand_not_supplied.xlsx"), index=False
    )

    """Obtain available capacities of methane network for hydrogen transportation."""
    _out = pd.DataFrame()
    for _lines, _variable, _name, _cap in [
        (
            model.set_line_tra,
            model.var_transported_tra,
            "Transmission|Capacity|Hydrogen",
            model.var_gamma_tra_line,
        ),
        (
            model.set_line_high,
            model.var_transported_high,
            "High-Pressure|Capacity|Hydrogen",
            model.var_gamma_high_line,
        ),
        (
            model.set_line_mid,
            model.var_transported_mid,
            "Mid-Pressure|Capacity|Hydrogen",
            model.var_gamma_mid_line,
        ),
    ]:
        for _y in [2030, 2035, 2040]:
            for _line in _lines:
                _max = 0
                for _month in model.set_time_unit:
                    _val = py.value(_variable[_line, _y, _month])
                    if np.absolute(_val) > _max:
                        _max = np.absolute(_val)
                _capacity = py.value(_cap[2025, _line])
                _out = write_IAMC(
                    _out, _model, _scenario, _line, _name, "MW", _y, _capacity - _max
                )
    _out.to_excel(
        os.path.join(path, "Available_Hydrogen_Capacities_2030_35_40.xlsx"), index=False
    )

    """INDICATE PIPELINES THAT EXIST BUT ARE NOT USED ANYMORE!"""
    """WRITE MAXIMUM DISPATCH CAPACITY TO IAMC FORMAT"""
    _out = pd.DataFrame()
    for year in [2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040]:
        for tline in model.set_line_tra:
            _max = 0
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_tra[tline, year, month])
                if np.absolute(_val) > _max:
                    _max = np.absolute(_val)
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                tline,
                "Transmission|Methane Transported|Max",
                "MW",
                year,
                _max,
            )

        for hline in model.set_line_high:
            _max = 0
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_high[hline, year, month])
                if np.absolute(_val) > _max:
                    _max = np.absolute(_val)
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                hline,
                "High-Pressure|Methane Transported|Max",
                "MW",
                year,
                _max,
            )

        for mline in model.set_line_mid:
            _max = 0
            for month in model.set_time_unit:
                _val = py.value(model.var_transported_mid[mline, year, month])
                if np.absolute(_val) > _max:
                    _max = np.absolute(_val)
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                mline,
                "Mid-Pressure|Methane Transported|Max",
                "MW",
                year,
                _max,
            )
    _out.to_excel(os.path.join(path, "methane_transported_max.xlsx"), index=False)

    '''SOURCE-RELATED VALUE OF LOST LOAD TO OUTPUT FILE'''
    _out = pd.DataFrame()
    for year in [2025, 2030, 2035, 2040, 2045]:
        for node in model.set_node_hp:
            _source_per_year_var = sum(
                py.value(model.var_source_high[node, year, month])
                for month in model.set_time_unit
            )
            _source_per_year_par = model.par_source_hp[node, year]
            _not_used_source = _source_per_year_par - _source_per_year_var
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                node,
                "High-Pressure|Methane|Source|Not Used",
                "MWh",
                year,
                _not_used_source
            )
        for node in model.set_node_mp:
            _source_per_year_var = sum(
                py.value(model.var_source_mid[node, year, month])
                for month in model.set_time_unit
            )
            _source_per_year_par = model.par_source_mp[node, year]
            _not_used_source = _source_per_year_par - _source_per_year_var
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                node,
                "Mid-Pressure|Methane|Source|Not Used",
                "MWh",
                year,
                _not_used_source
            )

    _out.to_excel(
        os.path.join(path, "methane_source_not_used.xlsx"), index=False
    )

    # RE-COMPRESSION (2040)
    _out = pd.DataFrame()
    _year = 2040
    for node in model.set_delivery_hp_mp:
        _max = 0
        for month in model.set_time_unit:
            _value = py.value(model.var_del_high_mid[node, _year, month])
            if _value < _max:
                _max = _value
        if _max != 0:
            _out = write_IAMC(
                _out,
                _model,
                _scenario,
                node,
                "RE-COMPRESSION|MID-PRESSURE",
                "MWh",
                _year,
                _max
            )
        else:
            pass

    _sum = 0
    for node in model.set_delivery_hp_mp:
        for month in model.set_time_unit:
            _value = py.value(model.var_del_high_mid[node, _year, month])
            if _value < 0:
                _sum += _value
            else:
                pass
    _out = write_IAMC(
        _out,
        _model,
        _scenario,
        'Austria|Network|Total',
        "RE-COMPRESSION|MID-PRESSURE|ANNUAL",
        "MWh",
        _year,
        _sum
    )

    _out.to_excel(os.path.join(path, "max_recompression_per_month_in_2040_in_MWh.xlsx"), index=False)

    return
