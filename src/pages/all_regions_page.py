import taipy.gui.builder as tgb

from callbacks import compute_region_data_callback

with tgb.Page() as all_regions_page:
    tgb.text(
        "# AOC Wine production | **{selected_year}** Campaign | All Regions", mode="md"
    )
    tgb.selector(
        "{selected_year}",
        lov="{year_list_for_selector}",
        on_change=compute_region_data_callback,
        dropdown=True,
        label="Choose Year",
    )

    with tgb.layout("1 1 1"):
        with tgb.part("card-bg"):
            tgb.text("## **Total:**", mode="md")
            tgb.text("### {int(total_production/10)} Million Liters", mode="md")
        with tgb.part("card-bg"):
            tgb.text("## **Red / Rosé:**", mode="md")
            tgb.text("### {int(red_rose_production / 10)} Million Liters", mode="md")
        with tgb.part("card-bg"):
            tgb.text("## **White:**", mode="md")
            tgb.text("### {int(white_production / 10)} Million Liters", mode="md")

    tgb.text("## Production | **by {selected_area}**", mode="md")
    tgb.toggle(
        "{selected_area}",
        lov="{area_type_list}",
        on_change=compute_region_data_callback,
    )
    with tgb.layout("1 1 "):
        tgb.chart(
            "{df_wine_year[df_wine_year['wine_type'] == 'RED AND ROSE']}",
            type="bar",
            properties="{property_barchart_red_rose}",
            layout="{bar_chart_layout}",
            height="800px",
        )
        tgb.chart(
            "{df_wine_year[df_wine_year['wine_type'] == 'WHITE']}",
            type="bar",
            properties="{property_barchart_white}",
            layout="{bar_chart_layout}",
            height="800px",
        )

    tgb.text(
        "## Production Maps| **{selected_year}**", mode="md", class_name="color-primary"
    )
    with tgb.layout("1 1 "):
        tgb.chart(
            "{df_map_red}",
            type="scattermapbox",
            lat="latitude",
            lon="longitude",
            marker="{marker_map_red}",
            layout="{layout_map_red}",
            text="text",
            mode="markers",
            height="600px",
            options="{options_map}",
        )
        tgb.chart(
            "{df_map_white}",
            type="scattermapbox",
            lat="latitude",
            lon="longitude",
            marker="{marker_map_white}",
            layout="{layout_map_white}",
            text="text",
            mode="markers",
            height="600px",
            options="{options_map}",
        )

    tgb.table(
        "{df_wine_production}",
        height="400px",
        width="100%",
        filter__AOC=True,
        filter__Region=True,
        filter__wine_type=True,
    )
