from taipy import Config

from algorithms import add_basic_stats, add_geometry

# Data nodes:
wine_production_node_config = Config.configure_csv_data_node(
    id="wine_production",
    default_path="data/wine_harvest_france_aoc_09_19.csv",
)
wine_production_with_stats_node_config = Config.configure_data_node(
    id="wine_production_with_stats",
)
geometry_node_config = Config.configure_json_data_node(
    id="geometry",
    default_path="data/french_wine_bassin_centroids.geojson",
)
wine_production_with_geometry_node_config = Config.configure_data_node(
    id="wine_production_with_geometry",
)

# Tasks:
add_wine_stats_task = Config.configure_task(
    id="add_wine_stats",
    function=add_basic_stats,
    input=wine_production_node_config,
    output=wine_production_with_stats_node_config,
    skippable=False,
)
add_geometry_task = Config.configure_task(
    id="add_geometry",
    function=add_geometry,
    input=[wine_production_with_stats_node_config, geometry_node_config],
    output=wine_production_with_geometry_node_config,
    skippable=False,
)

# Scenario:
sc_wine_scenario = Config.configure_scenario(
    id="sc_wine",
    task_configs=[add_wine_stats_task, add_geometry_task],
)

Config.export("./config/config.toml")
