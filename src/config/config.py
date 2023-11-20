import taipy.core as tp
from taipy import Config

# Loading of the TOML
Config.load("config/taipy-config.toml")
tp.Core().run()

# Get the scenario configuration
scenario_cfg = Config.scenarios["SC_WINE"]

sc_wine = tp.create_scenario(scenario_cfg)
sc_wine.submit()

df_wine_production = sc_wine.WINE_PRODUCTION_WITH_STATS.read()
df_wine_with_geometry = sc_wine.WINE_PRODUCTION_WITH_GEOMETRY.read()
