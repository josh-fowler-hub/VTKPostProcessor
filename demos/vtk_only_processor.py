#!/usr/bin/env python3

import vtk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

class VTKOnlyProcessor:
    """
    CFD Post-processor using only VTK (no PyVista) with alternative visualization backends
    """
    
    def __init__(self, file_path):
        """Load VTK file using pure VTK library"""
        self.file_path = file_path
        self.reader = None
        self.data = None
        
        # Try to load the file based on extension
        if file_path.endswith('.vtm'):
            self.reader = vtk.vtkXMLMultiBlockDataReader()
        elif file_path.endswith('.vtu'):
            self.reader = vtk.vtkXMLUnstructuredGridReader()
        elif file_path.endswith('.vtp'):
            self.reader = vtk.vtkXMLPolyDataReader()
        elif file_path.endswith('.vtk'):
            self.reader = vtk.vtkUnstructuredGridReader()
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        self.reader.SetFileName(file_path)
        self.reader.Update()
        self.data = self.reader.GetOutput()
        
        print(f"Loaded VTK file: {file_path}")
        if hasattr(self.data, 'GetNumberOfBlocks'):
            print(f"  Number of blocks: {self.data.GetNumberOfBlocks()}")
        
    def get_block_data(self, block_id=0):
        """Get data from a specific block (for multiblock) or main dataset"""
        if hasattr(self.data, 'GetBlock'):
            # Multiblock dataset
            block = self.data.GetBlock(block_id)
            if block is None:
                raise ValueError(f"Block {block_id} is empty")
            return block
        else:
            # Single dataset
            return self.data
    
    def extract_field_data(self, block_id=0, field_name='p', data_type='cell'):
        """Extract coordinates and field data from VTK dataset"""
        block = self.get_block_data(block_id)
        
        # Get coordinates
        points = block.GetPoints()
        n_points = points.GetNumberOfPoints()
        coords = np.zeros((n_points, 3))
        for i in range(n_points):
            coords[i] = points.GetPoint(i)
        
        # Get field data
        if data_type == 'cell':
            data_arrays = block.GetCellData()
            n_elements = block.GetNumberOfCells()
            
            # Get cell centers for coordinates
            centers = vtk.vtkCellCenters()
            centers.SetInputData(block)
            centers.Update()
            center_points = centers.GetOutput().GetPoints()
            coords = np.zeros((n_elements, 3))
            for i in range(n_elements):
                coords[i] = center_points.GetPoint(i)
        else:
            data_arrays = block.GetPointData()
            n_elements = n_points
        
        # Find the field
        field_array = data_arrays.GetArray(field_name)
        if field_array is None:
            available_fields = [data_arrays.GetArrayName(i) for i in range(data_arrays.GetNumberOfArrays())]
            raise ValueError(f"Field '{field_name}' not found. Available: {available_fields}")
        
        # Extract field values
        field_values = np.zeros(n_elements)
        for i in range(n_elements):
            field_values[i] = field_array.GetValue(i)
        
        return coords, field_values
    
    def list_fields(self, block_id=0):
        """List available fields in the dataset"""
        block = self.get_block_data(block_id)
        
        # Cell data fields
        cell_data = block.GetCellData()
        cell_fields = [cell_data.GetArrayName(i) for i in range(cell_data.GetNumberOfArrays())]
        
        # Point data fields
        point_data = block.GetPointData()
        point_fields = [point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays())]
        
        print(f"Block {block_id} fields:")
        print(f"  Cell data: {cell_fields}")
        print(f"  Point data: {point_fields}")
        
        return {'cell': cell_fields, 'point': point_fields}
    
    def contour_matplotlib(self, field_name='p', block_id=0, data_type='cell', n_contours=15):
        """Create 2D contour plot using matplotlib"""
        print(f"Creating matplotlib contour for field '{field_name}'...")
        
        # Extract data
        coords, field_values = self.extract_field_data(block_id, field_name, data_type)
        
        # Project to 2D (X-Y plane)
        x = coords[:, 0]
        y = coords[:, 1]
        
        print(f"Data points: {len(x)}")
        print(f"X range: {x.min():.3f} to {x.max():.3f}")
        print(f"Y range: {y.min():.3f} to {y.max():.3f}")
        print(f"{field_name} range: {field_values.min():.3f} to {field_values.max():.3f}")
        
        # Create regular grid
        resolution = 150
        xi = np.linspace(x.min(), x.max(), resolution)
        yi = np.linspace(y.min(), y.max(), resolution)
        Xi, Yi = np.meshgrid(xi, yi)
        
        # Interpolate to grid
        Zi = griddata((x, y), field_values, (Xi, Yi), method='linear')
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Filled contours
        contourf = ax.contourf(Xi, Yi, Zi, levels=n_contours, cmap='viridis', alpha=0.8)
        
        # Contour lines
        contour = ax.contour(Xi, Yi, Zi, levels=n_contours, colors='black', alpha=0.4, linewidths=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(contourf, ax=ax)
        cbar.set_label(field_name)
        
        # Labels and title
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Contour Plot: {field_name} (Block {block_id}, {data_type} data)')
        ax.set_aspect('equal')
        
        # Save
        output_file = f'vtk_contour_{field_name}_block_{block_id}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Contour plot saved: {output_file}")
        return output_file
    
    def contour_plotly(self, field_name='p', block_id=0, data_type='cell'):
        """Create 3D scatter plot using plotly"""
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        print(f"Creating plotly 3D plot for field '{field_name}'...")
        
        # Extract data
        coords, field_values = self.extract_field_data(block_id, field_name, data_type)
        
        # Sample for performance
        if len(coords) > 15000:
            indices = np.random.choice(len(coords), 15000, replace=False)
            coords = coords[indices]
            field_values = field_values[indices]
        
        print(f"Plotting {len(coords)} points")
        
        # Create 3D scatter
        fig = go.Figure(data=go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='markers',
            marker=dict(
                size=2,
                color=field_values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=field_name)
            ),
            text=[f'{field_name}: {val:.3f}' for val in field_values],
            hovertemplate='<b>%{text}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'3D Visualization: {field_name} (Block {block_id})',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            width=1000,
            height=800
        )
        
        # Save
        output_file = f'vtk_3d_{field_name}_block_{block_id}.html'
        pyo.plot(fig, filename=output_file, auto_open=False)
        
        print(f"✓ 3D plot saved: {output_file}")
        return output_file

def test_vtk_processor():
    """Test the VTK-only processor with your data"""
    print("Testing VTK-Only Processor")
    print("=" * 40)
    
    try:
        # Load your data
        processor = VTKOnlyProcessor('inner_surface.vtm')
        
        # List available fields
        fields = processor.list_fields(block_id=0)
        
        if fields['cell']:
            test_field = fields['cell'][0]  # Use first available cell field
            print(f"\nTesting with field: {test_field}")
            
            # Test matplotlib contour
            print("\n1. Testing matplotlib contour...")
            try:
                result = processor.contour_matplotlib(test_field, block_id=0, data_type='cell')
                print(f"✓ Success: {result}")
            except Exception as e:
                print(f"✗ Failed: {e}")
            
            # Test plotly 3D
            print("\n2. Testing plotly 3D...")
            try:
                result = processor.contour_plotly(test_field, block_id=0, data_type='cell')
                print(f"✓ Success: {result}")
            except Exception as e:
                print(f"✗ Failed: {e}")
        
        else:
            print("No cell data fields available for testing")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vtk_processor()