import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Read the data
df = pd.read_csv('district_wise.csv')

# Data cleaning
# Remove rows with missing income data
df_clean = df[df['INCOME'] != 'Data Not Available'].copy()
df_clean['INCOME'] = pd.to_numeric(df_clean['INCOME'])

# Extract year for sorting (handle different year formats)
def extract_year(year_str):
    if pd.isna(year_str) or year_str == '-':
        return None
    year_str = str(year_str).split('(')[0].strip()
    if '-' in year_str:
        return int(year_str.split('-')[0])
    return int(year_str)

df_clean['Year_Numeric'] = df_clean['YEAR'].apply(extract_year)

# Sort by income
df_sorted = df_clean.sort_values('INCOME', ascending=True)

# 1. Horizontal Bar Chart - District-wise Income Comparison
fig1 = go.Figure()

# Color scale based on income
colors = px.colors.sequential.Viridis
color_scale = np.interp(df_sorted['INCOME'], 
                         (df_sorted['INCOME'].min(), df_sorted['INCOME'].max()), 
                         (0, len(colors)-1)).astype(int)

fig1.add_trace(go.Bar(
    y=df_sorted['DISTRICT'],
    x=df_sorted['INCOME'],
    orientation='h',
    marker=dict(
        color=df_sorted['INCOME'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="Income (₹)")
    ),
    text=[f"₹{val/1000:.0f}K<br>{year}" for val, year in zip(df_sorted['INCOME'], df_sorted['YEAR'])],
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Income: ₹%{x:,.0f}<br><extra></extra>'
))

fig1.update_layout(
    title='District-wise Income in Delhi NCR',
    xaxis_title='Income (₹)',
    yaxis_title='District',
    height=800,
    template='plotly_white',
    showlegend=False,
    font=dict(size=12)
)

fig1.write_html('district_income_bar_chart.html')
print("Created: district_income_bar_chart.html")

# 2. Pie Chart - Income Distribution by District
fig2 = go.Figure()

fig2.add_trace(go.Pie(
    labels=df_sorted['DISTRICT'],
    values=df_sorted['INCOME'],
    hole=0.3,
    textinfo='label+percent',
    hovertemplate='<b>%{label}</b><br>Income: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
))

fig2.update_layout(
    title='Income Distribution by District in Delhi NCR',
    template='plotly_white',
    height=700
)

fig2.write_html('district_income_pie_chart.html')
print("Created: district_income_pie_chart.html")

# 3. Income Categories
def categorize_income(income):
    if income < 70000:
        return 'Low (<70K)'
    elif income < 150000:
        return 'Medium (70K-150K)'
    elif income < 500000:
        return 'High (150K-500K)'
    else:
        return 'Very High (>500K)'

df_clean['Income_Category'] = df_clean['INCOME'].apply(categorize_income)
category_counts = df_clean['Income_Category'].value_counts()

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=category_counts.index,
    y=category_counts.values,
    marker=dict(
        color=['#FF6B6B', '#FFA06B', '#FFD93D', '#6BCF7F'],
    ),
    text=category_counts.values,
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Districts: %{y}<extra></extra>'
))

fig3.update_layout(
    title='Districts by Income Category',
    xaxis_title='Income Category',
    yaxis_title='Number of Districts',
    template='plotly_white',
    height=500
)

fig3.write_html('income_categories.html')
print("Created: income_categories.html")

# 4. Top 10 Districts by Income
top_10 = df_sorted.tail(10)

fig4 = go.Figure()

fig4.add_trace(go.Bar(
    x=top_10['DISTRICT'],
    y=top_10['INCOME'],
    marker=dict(
        color=top_10['INCOME'],
        colorscale='Plasma',
        showscale=True,
        colorbar=dict(title="Income (₹)")
    ),
    text=[f"₹{val/1000:.0f}K" for val in top_10['INCOME']],
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Income: ₹%{y:,.0f}<br><extra></extra>'
))

fig4.update_layout(
    title='Top 10 Districts by Income in Delhi NCR',
    xaxis_title='District',
    yaxis_title='Income (₹)',
    template='plotly_white',
    height=600,
    xaxis_tickangle=-45
)

fig4.write_html('top_10_districts.html')
print("Created: top_10_districts.html")

# 5. Income by Year (Timeline)
df_year = df_clean.groupby('Year_Numeric')['INCOME'].mean().reset_index()
df_year = df_year.sort_values('Year_Numeric')

fig5 = go.Figure()

fig5.add_trace(go.Scatter(
    x=df_year['Year_Numeric'],
    y=df_year['INCOME'],
    mode='lines+markers',
    marker=dict(size=12, color='#FF6B6B'),
    line=dict(width=3, color='#FF6B6B'),
    hovertemplate='Year: %{x}<br>Avg Income: ₹%{y:,.0f}<extra></extra>'
))

fig5.update_layout(
    title='Average Income Trend Over Years (Delhi NCR)',
    xaxis_title='Year',
    yaxis_title='Average Income (₹)',
    template='plotly_white',
    height=500
)

fig5.write_html('income_timeline.html')
print("Created: income_timeline.html")

# 6. Comprehensive Dashboard
fig6 = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Top 5 Districts by Income', 
                    'Income Distribution',
                    'Income Categories', 
                    'Average Income by Year'),
    specs=[[{'type': 'bar'}, {'type': 'pie'}],
           [{'type': 'bar'}, {'type': 'scatter'}]]
)

# Top 5 districts
top_5 = df_sorted.tail(5)
fig6.add_trace(
    go.Bar(x=top_5['DISTRICT'], y=top_5['INCOME'], 
           marker_color='lightblue',
           name='Top 5'),
    row=1, col=1
)

# Pie chart
fig6.add_trace(
    go.Pie(labels=df_sorted.tail(8)['DISTRICT'], 
           values=df_sorted.tail(8)['INCOME'],
           name='Distribution'),
    row=1, col=2
)

# Categories
fig6.add_trace(
    go.Bar(x=category_counts.index, y=category_counts.values,
           marker_color='lightgreen',
           name='Categories'),
    row=2, col=1
)

# Timeline
fig6.add_trace(
    go.Scatter(x=df_year['Year_Numeric'], y=df_year['INCOME'],
               mode='lines+markers',
               marker=dict(size=8),
               name='Trend'),
    row=2, col=2
)

fig6.update_layout(
    title_text='Delhi NCR District Income Analysis Dashboard',
    height=900,
    showlegend=False,
    template='plotly_white'
)

fig6.write_html('income_dashboard.html')
print("Created: income_dashboard.html")

# 7. Summary Statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
print(f"Total Districts (with data): {len(df_clean)}")
print(f"Highest Income: ₹{df_clean['INCOME'].max():,.0f} ({df_clean[df_clean['INCOME'] == df_clean['INCOME'].max()]['DISTRICT'].values[0]})")
print(f"Lowest Income: ₹{df_clean['INCOME'].min():,.0f} ({df_clean[df_clean['INCOME'] == df_clean['INCOME'].min()]['DISTRICT'].values[0]})")
print(f"Average Income: ₹{df_clean['INCOME'].mean():,.0f}")
print(f"Median Income: ₹{df_clean['INCOME'].median():,.0f}")
print(f"Standard Deviation: ₹{df_clean['INCOME'].std():,.0f}")
print("="*60)

print("\nAll visualizations created successfully!")
print("Open the HTML files in your browser to view the interactive charts.")
