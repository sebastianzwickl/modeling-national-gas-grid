import pandas as pd
import utils
import constraints
import report
from pathlib import Path
import datetime

print('Scenarios: [1] Grüne Gase; [2] Grünes Methan; [3] Dezentrale Grüne Gase; [4] Elektrifizierung')
_x = input('Select Scenario: ')
_key = int(_x)

_dict = {
    1: 'gg',
    2: 'gm',
    3: 'dgg',
    4: 'elek'
}

_scenario = _dict[_key]
print('Scenario short tag: {}'.format(_scenario))

start_time = datetime.datetime.now()
print(start_time.strftime("%A, %H:%M"))

"""READ IN SHAPEFILES"""
_trans = utils.read_shapefile(path="transmission", name="transmission.shp")
_high = utils.read_shapefile(path="high", name="high.shp")
_mid = utils.read_shapefile(path="mid", name="mid.shp")
print("Done: Read in Shapefiles")

"""READ IN DATA"""
_path = Path("data")

# This is a modification of the initial code for the project "Gas Studie 2040".
_dem_str = "DEMAND_methane_MODELRUN_"+_scenario+".xlsx"
_demand = pd.read_excel(_path / _dem_str)
_demand_high = _demand.loc[_demand.Type == "High-Pressure"]
_demand_mid = _demand.loc[_demand.Type == "Mid-Pressure"]
_tra_dem_str = "TRANSIT_export_"+_scenario+".xlsx"
_demand_tra = pd.read_excel(_path / _tra_dem_str)
_pipeline_eco = pd.read_excel(_path / "INPUT_Pipelines_Economic.xlsx")
_pipeline_tec = pd.read_excel(_path / "INPUT_Pipelines_Technical_NEW_v2.xlsx")
_refurbishment = pd.read_excel(_path / "INPUT_Refurbishment.xlsx")
_source = pd.read_excel(_path / "INPUT_Source.xlsx")
_storage = pd.read_excel(_path / "INPUT_Storage_Technical.xlsx")
_time_dev = pd.read_excel(_path / "INPUT_Time_Resolution.xlsx")
_prices = pd.read_excel(_path / "INPUT_Prices.xlsx")

# CHANGES IN THE CODE FOR "GAS-STUDIE-2040"
_src_str = "SOURCE_methane_MODELRUN_FINAL"+_scenario+".xlsx"
_local_gen = pd.read_excel(_path / _src_str)
_imp_src = "TRANSIT_import_"+_scenario+".xlsx"
_feasible = pd.read_excel(_path / _imp_src)

"""NODES OF THE NETWORK"""
_nodes = utils.get_nodes_from_lines(
    transmission=_trans, high_pressure=_high, mid_pressure=_mid
)
print("Done: Create Nodes of Model")


"""PYOMO.CONCRETEMODEL()"""
model = utils.create_model()

model.transmission = _trans
model.high = _high
model.mid = _mid

utils.add_import_and_export_lines_per_node(model=model)

model.demand_tra = _demand_tra
model.demand_high = _demand_high
model.demand_mid = _demand_mid
model.pipeline_economic = _pipeline_eco
model.pipeline_technical = _pipeline_tec
model.refurbishment = _refurbishment
model.source = _source
model.storage = _storage
model.temporal_demand = _time_dev
model.prices = _prices
model.generation = _local_gen
model.feasible = _feasible
utils.add_nodal_sets(model=model, nodes=_nodes)


utils.add_line_sets(model=model, data=[_trans, _high, _mid])
utils.add_time_horizon(model=model, year=2065, temporal=12)
utils.add_cluster_sets(model=model)
print("Done: Add Sets")

# print('High-Pressure Nodes')
list_high = []
for element in model.set_node_hp:
    list_high.append(element)
# print('Mid-Pressure Nodes')
list_mid = []
for element in model.set_node_mp:
    list_mid.append(element)


series_high = pd.Series(list_high)
series_mid = pd.Series(list_mid)
df = pd.DataFrame({'High': series_high, 'Mid': series_mid})

utils.add_decision_variables(model=model)
print("Done: Add Decision Variables")

utils.add_parameter_to_model(model=model)
print("Done: Add Parameters")

constraints.add(model=model)
print("Done: Add Constraints")
utils.add_objective_function(model=model)
print("Done: Add Objective Function")

model.c_limit_demand_not_supplied_high_2040.deactivate()
model.c_limit_demand_not_supplied_mid_2040.deactivate()

if _scenario == 'gm':
    print('Deactivate Green Gas Constraint!')
    model.c_green_gas.deactivate()

print('Done: Deactivate constraints')

# """PRINT AND DISPLAY THE MODEL"""
# utils.print_model(model)


# DISPLAY TIME TO INITIALIZE THE MODEL
initialize_time = datetime.datetime.now() - start_time
print(
    "Time to initialize the model in minutes: ",
    int(initialize_time.total_seconds() / 60),
)

"""START TO SOLVE THE MODEL"""
Solver = utils.set_solver_for_the_model(model)
# eliminate_fixed_vars.apply_to(model)
# print('DONE: eliminate_fixed_vars.apply_to(model)')
# model.check_model()
# print('DONE: model.check_model()')
# model.validate_dual_unboundness()
# print('DONE: model.validate_dual_unboundness()')
solution = Solver.solve(model, tee=True, warmstart=True)
solution.write()
model.objective.display()


"""REPORT RESULTS IN OUTPUT FILES"""
report.write_results_to_folder(
    model, _scenario
)
