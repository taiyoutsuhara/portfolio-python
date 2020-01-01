# app.layout = html.Div([
#     html.H1('Service Comparison Dashboard'),
#     html.H4("Input value described in Available Combinations. "
#                     "When zero is input, comparisons are not conducted."),
#     dcc.Tabs(id="tabs", value='tab-1-information', children=[
#         dcc.Tab(label='Information', value='tab-1-information'),
#         dcc.Tab(label='Comparison', value='tab-2-comparison'),
#         dcc.Tab(label='Ranking', value='tab-3-ranking'),
#     ]),
#     html.Div(id='service-comparison-dashboard')
# ])
#
# @app.callback(Output('service-comparison-dashboard', 'children'), [Input('tabs', 'value')])
# def render_content(tab):
#     if tab == 'tab-1-information':
#         return html.Div([
#             html.H3('Service Description'),
#             dash_table.DataTable(
#                 id='Information',
#                 columns=[{"name": i, "id": i} for i in description_of_service_types.columns],
#                 data=description_of_service_types.to_dict('records')
#             )
#         ])
#     elif tab == 'tab-2-comparison':
#         return html.Div([
#             html.H3('Available Combinations'),
#             dash_table.DataTable(
#                 id='Information',
#                 columns=[{"name": i, "id": i} for i in data_frame_of_selectable_patterns.columns],
#                 data=data_frame_of_selectable_patterns.to_dict('records')
#             )
#         ])
#     elif tab == 'tab-3-ranking':
#         return html.Div([
#             html.H4("Input value described in Available Combinations. "
#                     "When zero is input, comparisons are not conducted."),
#             html.Label('1st, 2nd, or 3rd Comparison'),
#             dcc.Input(id="1st-comparison",
#                       type="number",
#                       min=0, max=last_number_at_select, value=0,
#                       placeholder="1st Comparison"),
#             dcc.Input(id="2nd-comparison",
#                       type="number",
#                       min=0, max=last_number_at_select, value=0,
#                       placeholder="2nd Comparison"),
#             dcc.Input(id="3rd-comparison",
#                       type="number",
#                       min=0, max=last_number_at_select, value=0,
#                       placeholder="3rd Comparison"),
#             dcc.Graph(
#                 id='example-graph',
#                 figure={
#                     'data': [
#                         {'x': code_of_service_types_ex_non_use,
#                          'y': data_for_dash[],
#                          'type': 'bar', 'name': '1st'},
#                         {'x': code_of_service_types_ex_non_use,
#                          'y': data_for_dash[],
#                          'type': 'bar', 'name': '2nd'},
#                         {'x': code_of_service_types_ex_non_use,
#                          'y': data_for_dash[],
#                          'type': 'bar', 'name': '3rd'}],
#                     'layout': {
#                     }
#                 }
#             )
#         ])
#
