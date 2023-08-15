from solara.components.file_drop import FileInfo
import textwrap
import pandas as pd
import solara

@solara.component
def Page():

    content, set_content = solara.use_state([])  # Use an empty list to store dictionary array
    selected_food_values, set_selected_food_values = solara.use_state([])  # To keep track of selected checkboxes
    option, set_option = solara.use_state("bars")
    click_data, set_click_data = solara.use_state(None)
    mouseover_data, set_mouseover_data = solara.use_state(None)
    mouseout_data, set_mouseout_data = solara.use_state(None)

    def process_file(file: FileInfo):
        global df  # Declare df as a global variable
        df = pd.read_excel(file["file_obj"])  # Read Excel file into a DataFrame
        dict_array = df.to_dict(orient="records")  # Convert DataFrame to dictionary array
        set_content(dict_array)
        create_chart(option, df)

    def on_action_column(column_name):
        # Implement your logic for column action here
        print(f"Column action on: {column_name}")

    def on_action_cell(row_index, column_name):
        # Implement your logic for cell action here
        if column_name == "food":
            food_value = df.at[row_index, "food"]
            price_value = df.at[row_index, "price"]
            print(f"Cell action on: Row {row_index}, Food: {food_value}, Price: {price_value}")

    def create_checkboxes(df):
        unique_food_values = df["food"].unique()
        with solara.Row():  # Use Row to display checkboxes horizontally
            for food_value in unique_food_values:
                checkbox_label = f"food_checkbox_{food_value}"
                checkbox_state = food_value in selected_food_values
                solara.Checkbox(label=food_value, value=checkbox_state, on_value=lambda checked: update_selected_food_values(checked, food_value))

    def create_chart_data(df):
        chart_data = []
        for index, row in df.iterrows():
            chart_data.append({"name": row["food"], "value": row["price"]})
        return chart_data

    def create_chart(option, df):
        chart_option = {
            "title": {"text": "Food Prices"},
            "tooltip": {},
            "legend": {"data": ["price"]},
            "xAxis": {"type": "category"},
            "yAxis": {},
            "series": [
                {
                    "name": "price",
                    "type": "bar",
                    "data": create_chart_data(df),
                    "universalTransition": True,
                }
            ],
        }
        solara.FigureEcharts(option=chart_option, on_click=set_click_data, on_mouseover=set_mouseover_data, on_mouseout=set_mouseout_data)

    def update_selected_food_values(checked, food_value):
        # Update the list of selected checkboxes
        if checked:
            set_selected_food_values(selected_food_values + [food_value])
        else:
            set_selected_food_values([value for value in selected_food_values if value != food_value])

        # Update the chart based on the selected checkboxes
        update_chart()

    def update_chart():
        selected_data = [data for data in create_chart_data(df) if data["name"] in selected_food_values]
        chart_option = {
            "series": [
                {
                    "name": "price",
                    "type": "bar",
                    "data": selected_data,
                    "universalTransition": True,
                }
            ],
        }
        solara.update_component(option_id, chart_option)

    with solara.Column(margin=10):
        solara.FileDrop(
            label="input excel",
            on_file=process_file,
            lazy=True
        )

        if content:
            column_actions = [solara.ColumnAction(icon="mdi-sunglasses", name="User column action", on_click=on_action_column)]
            cell_actions = [solara.CellAction(icon="mdi-white-balance-sunny", name="User cell action", on_click=on_action_cell)]

            option_id = create_chart(option, df)  # Get the component ID for the chart
            create_checkboxes(df)  # Pass df as an argument
            df_component = solara.DataFrame(df, column_actions=column_actions, cell_actions=cell_actions)
            df_component
