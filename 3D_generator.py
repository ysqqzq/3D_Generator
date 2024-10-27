import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata

# Read the data file
csv_file_path = 'data_indice.csv'  # Replace with the actual file path
data = pd.read_csv(csv_file_path)
data_split = data.iloc[:, 0].str.split(',', expand=True)
data_split.columns = ['Index', 'X', 'Y', 'Z']

data_split['X'] = pd.to_numeric(data_split['X'], errors='coerce')
data_split['Y'] = pd.to_numeric(data_split['Y'], errors='coerce')
data_split['Z'] = pd.to_numeric(data_split['Z'], errors='coerce')

# Group data by index prefix
grouped_data = {f"{i}_": data_split[data_split['Index'].str.startswith(f"{i}_")]
                for i in range(1, 10)}

def generate_scatter_plot(selected_groups):
    fig = go.Figure()
    colors = ['rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,165,0)', 
              'rgb(238,130,238)', 'rgb(75,0,130)', 'rgb(255,255,0)', 'rgb(0,255,255)', 'rgb(128,0,0)']
    
    for i, group in enumerate(selected_groups):
        group_data = grouped_data[group]
        
        fig.add_trace(go.Scatter3d(
            x=group_data['X'], y=group_data['Y'], z=group_data['Z'],
            mode='markers+text' if len(selected_groups) == 1 else 'markers',
            text=group_data['Index'] if len(selected_groups) == 1 else None,
            marker=dict(color=colors[i], size=5),
            name=f"Group {group}"
        ))

    fig.update_layout(title='3D Scatter Plot',
                      scene=dict(
                          xaxis_title='CSM',
                          yaxis_title='PR RW',
                          zaxis_title='SCR'
                      ))

    return fig

def generate_mesh_plot_with_points(selected_groups):
    fig = go.Figure()
    
    for i, group in enumerate(selected_groups):
        group_data = grouped_data[group]
        
        # Add the 3D mesh
        fig.add_trace(go.Mesh3d(
            x=group_data['X'],
            y=group_data['Y'],
            z=group_data['Z'],
            opacity=0.5,
            color='blue',
            name=f"Group {group}"
        ))

        # Add scatter points
        fig.add_trace(go.Scatter3d(
            x=group_data['X'],
            y=group_data['Y'],
            z=group_data['Z'],
            mode='markers+text',
            text=group_data['Index'],
            marker=dict(size=5, color='rgb(255,0,0)'),
            name=f"Points of Group {group}"
        ))

    fig.update_layout(title='3D Mesh Plot with Points',
                      scene=dict(
                          xaxis_title='CSM',
                          yaxis_title='PR RW',
                          zaxis_title='SCR'
                      ))

    return fig

def generate_contour_plot(selected_groups):
    fig = go.Figure()
    
    for i, group in enumerate(selected_groups):
        group_data = grouped_data[group]
        
        # Create a grid for contour plot
        xi = np.linspace(group_data['X'].min(), group_data['X'].max(), 100)
        yi = np.linspace(group_data['Y'].min(), group_data['Y'].max(), 100)
        xi, yi = np.meshgrid(xi, yi)
        zi = griddata((group_data['X'], group_data['Y']), group_data['Z'], (xi, yi), method='cubic')
        
        # Add contour and scatter points
        fig.add_trace(go.Contour(
            x=xi[0],
            y=yi[:, 0],
            z=zi,
            colorscale='Viridis',
            name=f"Group {group}"
        ))

        fig.add_trace(go.Scatter(
            x=group_data['X'],
            y=group_data['Y'],
            mode='markers+text',
            text=group_data['Index'],
            marker=dict(color='red', size=8),
            name=f"Points of Group {group}"
        ))

    fig.update_layout(title='3D Contour Plot with Points',
                      xaxis_title='CSM',
                      yaxis_title='PR RW')

    return fig

# Streamlit app title
st.title("3D Plot Generator")

# Show multiselect box for group selection
selected_groups = st.multiselect("Select Groups", list(grouped_data.keys()))

# Select plot type
plot_type = st.selectbox("Select Plot Type", ["3D Scatter Plot", "3D Mesh Plot with Points", "3D Contour Plot"])

if st.button("Generate Plot"):
    if selected_groups:
        if plot_type == "3D Scatter Plot":
            fig = generate_scatter_plot(selected_groups)
        elif plot_type == "3D Mesh Plot with Points":
            fig = generate_mesh_plot_with_points(selected_groups)
        elif plot_type == "3D Contour Plot":
            fig = generate_contour_plot(selected_groups)

        # Display the generated plot
        st.plotly_chart(fig)
    else:
        st.error("Please select at least one group.")
