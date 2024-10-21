import pandas as pd
import plotly.express as px
import glob
import json
import sys
import math
import plotly.graph_objects as go
yaxes_offset = 1000
def gate_bound_asymptotic(n, k):
    l =  math.ceil(k/2)
    bound =   n * (math.log2(k)*math.log2(k)) / k
    return int(math.ceil(bound))

def upper_gate_bound(n, k):
    l =  math.ceil(k/2)
    p = int(math.log2(l))
    bound = 2 *( (2*n + k) * (math.log2(k)**2) + 2*n*(k+1))*(k + math.log2(k))
    # bound = 2 *((2*n + 2*k + k*p + 1)*p + n*(k+1))*(2*l+p)
    bound = bound / (k*(k+1))
    return int(math.ceil(bound))

def lower_gate_bound(n, k):
    bound = n*math.log(n)/k
    return int(math.ceil(bound))

# Function to create a stacked bar chart for a given k
def stacked_bar_chart_k(df, k, output_dir='.', n=None):
    df_k = df[df['k'] == k]
    if n is not None:
        df_k = df_k[df_k['n'].isin(n)]
    df_k.to_csv('k.csv')
    df_k = pd.read_csv('k.csv')
    # fig = px.bar(wide_df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    fig = px.bar(
        df_k, x='n',
        y=['and', 'or', 'maj', 'not'],
        title=f'Stacked Bar Chart for k={k}',
        labels={'value': '#Gates', 'variable': 'Logic Gates'},
        pattern_shape="variable",
        template="simple_white"
        # category_orders={'n': sorted(df_k['n'].unique())}
    )
    # fig.update_traces(texttemplate="%{y}")
    fig.update_xaxes(type='category')
    fig.update_layout(yaxis=dict(range=[0, max(df_k['bound'].max(), df_k['sum'].max()) + yaxes_offset]))

    fig.update_layout(
    legend=dict(
        x=.1,
        y=.95,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
    )
    )
    # Create the line chart trace with markers only, large size, and value labels
    line_trace = go.Scatter(
        x=df_k['n'],
        y=df_k['bound'],
        mode='markers+text',  # Ensure markers and text are both plotted
        name='Upper Bound',
        marker=dict(
            color='mediumseagreen',
            size=12,  # Large marker size
            symbol='x'  # Marker symbol 'x'
        ),
        text=df_k['bound'],  # Display values of the markers
        textposition='top center'  # Position of the text relative to markers
    )
    # Add the line chart trace to the figure
    fig.add_trace(line_trace)

    line_trace = go.Scatter(
        x=df_k['n'],
        y=df_k['lbound'],
        mode='markers+text',  # Ensure markers and text are both plotted
        name='Lower Bound',
        marker=dict(
            color='firebrick',
            size=12,  # Large marker size
            symbol='hexagon2-dot'  # Marker symbol 'x'
        ),
        text=df_k['lbound'],  # Display values of the markers
        textposition='top center'  # Position of the text relative to markers
    )
    # Add the line chart trace to the figure
    fig.add_trace(line_trace)


    fig.write_image(f"{output_dir}/stacked_bar_chart_k_{k}.pdf")
    fig.show()


# Function to create a stacked bar chart for a given n
def stacked_bar_chart_n(df, n, output_dir='.', k=None):
    df_k = df[df['n'] == n]
    if k is not None:
        df_k = df_k[df_k['k'].isin(k)]
    df_k.to_csv('n.csv')
    df_k = pd.read_csv('n.csv')
    # fig = px.bar(wide_df, x="nation", y=["gold", "silver", "bronze"], title="Wide-Form Input")
    fig = px.bar(
        df_k, x='k',
        y=['and', 'or', 'maj', 'not'],
        title=f'Stacked Bar Chart for n={n}',
        labels={'value': '#Gates', 'variable': 'Logic Gates'},
        pattern_shape="variable",
        template="simple_white"
        # category_orders={'n': sorted(df_k['n'].unique())}
    )
    fig.update_xaxes(type='category')

    fig.update_layout(yaxis=dict(range=[0, max(df_k['bound'].max(), df_k['sum'].max()) + yaxes_offset]))
    # fig.update_traces(texttemplate="%{y}")
    fig.update_layout(
    legend=dict(
        x=.8,
        y=.95,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
    )
    )

    # Create the line chart trace with markers only, large size, and value labels
    line_trace = go.Scatter(
        x=df_k['k'],
        y=df_k['bound'],
        mode='markers+text',  # Ensure markers and text are both plotted
        name='Upper Bound',
        marker=dict(
            color='mediumseagreen',
            size=12,  # Large marker size
            symbol='x'  # Marker symbol 'x'
        ),
        text=df_k['bound'],  # Display values of the markers
        textposition='top center'  # Position of the text relative to markers
    )
    # Add the line chart trace to the figure
    fig.add_trace(line_trace)
    # Create the line chart trace with markers only, large size, and value labels
    line_trace = go.Scatter(
        x=df_k['k'],
        y=df_k['lbound'],
        mode='markers+text',  # Ensure markers and text are both plotted
        name='Lower Bound',
        marker=dict(
            color='firebrick',
            size=12,  # Large marker size
            symbol='hexagon2-dot'  # Marker symbol 'x'
        ),
        text=df_k['lbound'],  # Display values of the markers
        textposition='top center'  # Position of the text relative to markers
    )
    # Add the line chart trace to the figure
    fig.add_trace(line_trace)
    fig.write_image(f"{output_dir}/stacked_bar_chart_k_{k}.pdf")
    fig.show()

# Function to create a line plot for each k with sum of logicsynthesis columns
def line_plot_sum_k(df, output_dir='.'):
    df = df[df['k'].isin({5,9,17,51,101})]
    fig = px.line(
        df, x='n', y='sum',color='k',
        # title='Line Plot of Sum of Logic Synthesis Values for each k',
        labels={'sum': '#Gates', 'n': 'n'},
        markers=True,
        symbol=df['k'],
        template="simple_white"
    )

    # # Melt the DataFrame to long format for Plotly Express
    # df_melted = df.melt(id_vars=['n', 'k'], value_vars=['sum'],
    #                     var_name='Metric', value_name='Values')

    # # Create a plot using Plotly Express
    # fig = px.line(df_melted, x='n', y='Values', color='k', line_dash='Metric',
    #             labels={'Values': 'Values', 'Metric': 'Metric'},
    #             title='Gates and Bound vs n for each k',
    #                     template="simple_white"
    #     )

    fig.update_traces(mode='lines', marker_line_width=2, marker_size=20)
    fig.update_xaxes(type='category')
    fig.update_layout(yaxis=dict(range=[1, max(df['bound'].max(), df['sum'].max())]))
    fig.update_layout(
    legend=dict(
        x=.1,
        y=.9,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
    )
    )
    fig.write_image(f"{output_dir}/line_plot_sum_k.pdf")
    fig.show()


def dict_to_dataframe(data):
  """
  Converts a dictionary to a pandas DataFrame, handling entries with different lengths.

  Args:
      data: A list of dictionaries where each dictionary represents a row in the DataFrame.

  Returns:
      A pandas DataFrame created from the list of dictionaries.
  """

  # Get all keys from all dictionaries
  all_keys = set().union(*[d.keys() for d in data])

  # Create a DataFrame with columns from all keys and fill with None
  df = pd.DataFrame.from_dict({k: [None] * len(data) for k in all_keys})

  # Fill the DataFrame with data from each dictionary
  for i, d in enumerate(data):
    for k, v in d.items():
      df.loc[i, k] = v
  return df

if __name__ == "__main__":
    # Use glob to find all CSV files matching the pattern
    with open('tcad.json') as f:
        data = json.load(f)

    print(data[0])
    df = dict_to_dataframe(data)
    # df = df[pd.to_datetime(df['timestamp']).dt.date == pd.Timestamp.today().date()]
    df.to_csv('test.csv')
    # df = pd.concat(df_list, ignore_index=True)

    # Rename columns for better legend labels
    df.rename(columns={
        'sls.and': 'and',
        'sls.or': 'or',
        'sls.maj': 'maj',
        'sls.not': 'not',
    }, inplace=True)
    # df['k'] = 2*df['c'] - 1
    # Example usage
    df['bound'] = df.apply(lambda row: upper_gate_bound(row['n'], row['k']), axis=1)
    df['lbound'] = df.apply(lambda row: lower_gate_bound(row['n'], row['k']), axis=1)

    df['sum'] = df[['and', 'or', 'maj', 'not']].sum(axis=1)
    df.to_csv('raw_data.csv')

    k_value = 9
    n_value = 201

    # print(list(df['k'].unique()))
    # print(list(df['n'].unique()))

    output_dir = '.'  # Define your output directory here if needed

    # stacked_bar_chart_k(df, k_value, output_dir, [17,51,101,201,511])
    # n_value = 511
    n_value = 1001
    stacked_bar_chart_n(df, n_value, output_dir, [5,9,17,51,101])
    # line_plot_sum_k(df, output_dir)
