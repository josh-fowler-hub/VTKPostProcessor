import vtk
try:
    from vtk.util import numpy_support
except ImportError:
    # Fallback for older VTK versions
    import vtk.util.numpy_support as numpy_support
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

class CFDPostProcessor:
    def __init__(self, file_path):
        """Load VTK file using pure VTK library"""
        self.file_path = file_path
        self.reader = None
        self.dataset = None
        self.data = []
        
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
        self.dataset = self.reader.GetOutput()
        
        # Handle multiblock vs single block
        if hasattr(self.dataset, 'GetNumberOfBlocks'):
            # Multiblock dataset
            self.data = []
            self.block_names = []
            for i in range(self.dataset.GetNumberOfBlocks()):
                block = self.dataset.GetBlock(i)
                if block is not None:
                    self.data.append(block)
                    # Try to get actual block name from metadata
                    meta_data = self.dataset.GetMetaData(i)
                    if meta_data and meta_data.Has(vtk.vtkCompositeDataSet.NAME()):
                        block_name = meta_data.Get(vtk.vtkCompositeDataSet.NAME())
                        self.block_names.append(block_name)
                    else:
                        self.block_names.append(f"Block_{i}")
            print(f"Loaded multiblock dataset with {len(self.data)} blocks")
            print(f"Block names: {self.block_names}")
            
            # Combine all blocks for mesh property
            if self.data:
                self.mesh = self.data[0]  # Use first block as primary mesh
            else:
                self.mesh = None
        else:
            # Single dataset
            self.data = [self.dataset]
            self.block_names = ["main"]
            self.mesh = self.dataset
            print("Loaded single block dataset")
    
    def get_block_names(self, verbose=True):
        """Get names of all blocks in the dataset"""
        if verbose:
            print(f"Available blocks: {self.block_names}")
        return self.block_names
    
    def get_block_index(self, block_name):
        """Convert block name to index"""
        if block_name in self.block_names:
            return self.block_names.index(block_name)
        else:
            raise ValueError(f"Block '{block_name}' not found. Available blocks: {self.block_names}")
    
    def _resolve_blocks(self, block_name=None, block_id=None):
        """
        Helper method to resolve block specification into a list of (block_name, block_index) tuples
        
        Args:
            block_name: None (all blocks), str (single block), or list (multiple blocks)
            block_id: int (single block by index) - only used if block_name is None
            
        Returns:
            List of (block_name, block_index) tuples
        """
        if block_name is None:
            if block_id is not None:
                # Single block by ID
                return [(self.block_names[block_id], block_id)]
            else:
                # All blocks
                return [(name, idx) for idx, name in enumerate(self.block_names)]
        elif isinstance(block_name, str):
            # Single block by name
            idx = self.get_block_index(block_name)
            return [(block_name, idx)]
        elif isinstance(block_name, list):
            # Multiple blocks by name
            return [(name, self.get_block_index(name)) for name in block_name]
        else:
            raise ValueError(f"Invalid block_name type: {type(block_name)}. Use None, str, or list.")
    
    def get_variable_names(self, block_name=None, block_index=None, verbose=True):
        """Get variable names from specified block (by name or index)"""
        # Handle block specification
        if block_name is not None:
            block_idx = self.get_block_index(block_name)
        elif block_index is not None:
            block_idx = block_index
        else:
            block_idx = 0  # Default to first block
        
        if block_idx >= len(self.data):
            raise ValueError(f"Block index {block_idx} out of range")
        
        block = self.data[block_idx]
        
        # Cell data fields
        cell_data = block.GetCellData()
        cell_fields = [cell_data.GetArrayName(i) for i in range(cell_data.GetNumberOfArrays())]
        
        # Point data fields
        point_data = block.GetPointData()
        point_fields = [point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays())]
        
        if verbose:
            block_display = block_name if block_name else f"Block {block_idx} ({self.block_names[block_idx]})"
            print(f"{block_display} fields:")
            print(f"  Cell data: {cell_fields}")
            print(f"  Point data: {point_fields}")
        
        return {"point_data": point_fields, "cell_data": cell_fields}
    
    def extract_field_data(self, field_name='p', data_type='cell', block_name=None, block_id=None):
        """Extract coordinates and field data from VTK dataset (using block name or ID)"""
        # Handle block specification
        if block_name is not None:
            block_idx = self.get_block_index(block_name)
        elif block_id is not None:
            block_idx = block_id
        else:
            block_idx = 0  # Default to first block
        
        if block_idx >= len(self.data):
            raise ValueError(f"Block index {block_idx} out of range")
        
        block = self.data[block_idx]
        
        # Get coordinates and field data
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
            n_elements = block.GetNumberOfPoints()
            points = block.GetPoints()
            coords = np.zeros((n_elements, 3))
            for i in range(n_elements):
                coords[i] = points.GetPoint(i)
        
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
    
    def slice_and_average(self, axis='y', num_slices=100, data_type='cell', block_name=None, block_id=None):
        """Slice the dataset and compute averages - VTK version (using block name or ID)"""
        # Get bounds from specified block
        if not self.data:
            return pd.DataFrame()
        
        # Handle block specification
        if block_name is not None:
            block_idx = self.get_block_index(block_name)
            blocks_to_process = [(block_name, block_idx)]
        elif block_id is not None:
            blocks_to_process = [(self.block_names[block_id], block_id)]
        else:
            # Process all blocks and combine data
            blocks_to_process = [(name, idx) for idx, name in enumerate(self.block_names)]
        
        # For multiple blocks, find global bounds across all blocks
        if len(blocks_to_process) > 1:
            # Find global min/max across all blocks
            global_min = float('inf')
            global_max = float('-inf')
            axis_index = {'x': 0, 'y': 2, 'z': 4}[axis]
            
            for block_display_name, block_idx in blocks_to_process:
                block = self.data[block_idx]
                bounds = block.GetBounds()
                block_min = bounds[axis_index]
                block_max = bounds[axis_index + 1]
                
                if block_min < global_min:
                    global_min = block_min
                if block_max > global_max:
                    global_max = block_max
            
            print(f"Processing {num_slices} slices along {axis} axis globally from {global_min:.3f} to {global_max:.3f}")
            
            global_range = global_max - global_min
            if global_range == 0:
                return pd.DataFrame()
                
            slice_thickness = global_range / num_slices
            
            # Get all field names from all blocks (union of all fields)
            all_field_names = set()
            for block_display_name, block_idx in blocks_to_process:
                fields_info = self.get_variable_names(block_name=block_display_name, block_index=block_idx, verbose=False)
                field_names = fields_info['cell_data'] if data_type == 'cell' else fields_info['point_data']
                all_field_names.update(field_names)
            
            all_field_names = list(all_field_names)
            print(f"Available fields across all blocks: {len(all_field_names)} fields")
            
            all_results = []
            
            # Create global slices
            for i in range(num_slices):
                lower = global_min + i * slice_thickness
                upper = lower + slice_thickness
                mid = (lower + upper) / 2
                
                # Collect data from all blocks for this slice
                slice_data = {f'{axis}_mid': mid}
                field_values_in_slice = {field: [] for field in all_field_names}
                
                # Extract data from all blocks for this global slice
                for block_display_name, block_idx in blocks_to_process:
                    # Get field data for this block
                    for field_name in all_field_names:
                        try:
                            coords, values = self.extract_field_data(field_name, data_type, block_name=block_display_name, block_id=block_idx)
                            if values is not None and len(values) > 0:
                                # Filter points in this slice
                                axis_coord_index = {'x': 0, 'y': 1, 'z': 2}[axis]
                                in_slice = (coords[:, axis_coord_index] >= lower) & (coords[:, axis_coord_index] <= upper)
                                
                                if np.sum(in_slice) > 0:
                                    slice_values = values[in_slice]
                                    field_values_in_slice[field_name].extend(slice_values)
                        except:
                            # Field not available in this block
                            continue
                
                # Compute averages for all fields across all blocks in this slice
                for field_name in all_field_names:
                    if field_values_in_slice[field_name]:
                        slice_data[f'{field_name}_avg'] = np.mean(field_values_in_slice[field_name])
                    else:
                        slice_data[f'{field_name}_avg'] = np.nan
                
                all_results.append(slice_data)
                
                # Print progress
                if (i + 1) % 20 == 0:
                    print(f"  Processed {i + 1}/{num_slices} global slices")
            
            # Create dataframe from global slice results
            if all_results:
                df = pd.DataFrame(all_results)
                print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
                return df.sort_values(f'{axis}_mid')
            else:
                return pd.DataFrame()
        
        # Single block processing (original logic)
        all_results = []
        
        for block_display_name, block_idx in blocks_to_process:
            # Work with this specific block
            block = self.data[block_idx]
            
            bounds = block.GetBounds()  # [xmin, xmax, ymin, ymax, zmin, zmax]
            
            axis_index = {'x': 0, 'y': 2, 'z': 4}[axis]
            min_val = bounds[axis_index]
            max_val = bounds[axis_index + 1]
            
            y_range = max_val - min_val
            if y_range == 0:
                continue  # Skip blocks with no range in this axis
                
            slice_thickness = y_range / num_slices
            
            # Get all field names for this block
            fields_info = self.get_variable_names(block_name=block_display_name, block_index=block_idx, verbose=False)
            field_names = fields_info['cell_data'] if data_type == 'cell' else fields_info['point_data']
            
            if len(blocks_to_process) == 1:
                print(f"Processing {num_slices} slices along {axis} axis for {block_display_name}...")
                print(f"Available fields: {field_names}")
            else:
                print(f"Processing {num_slices} slices along {axis} axis for {block_display_name}...")
            
            for i in range(num_slices):
                lower = min_val + i * slice_thickness
                upper = lower + slice_thickness
                mid = (lower + upper) / 2
                
                # Extract data for this slice
                coords, _ = self.extract_field_data(field_names[0], data_type, block_name=block_display_name, block_id=block_idx)
                
                # Filter points in this slice
                axis_coord_index = {'x': 0, 'y': 1, 'z': 2}[axis]
                in_slice = (coords[:, axis_coord_index] >= lower) & (coords[:, axis_coord_index] <= upper)
                
                if np.sum(in_slice) > 0:
                    slice_data = {f'{axis}_mid': mid}
                    
                    # Compute averages for all fields
                    for field_name in field_names:
                        coords, values = self.extract_field_data(field_name, data_type, block_name=block_display_name, block_id=block_idx)
                        if values is not None and len(values) > 0:
                            slice_values = values[in_slice]
                            if len(slice_values) > 0:
                                slice_data[f'{field_name}_avg'] = np.mean(slice_values)
                            else:
                                slice_data[f'{field_name}_avg'] = np.nan
                    
                    all_results.append(slice_data)
                
                # Print progress only for single block processing
                if len(blocks_to_process) == 1 and (i + 1) % 20 == 0:
                    print(f"  Processed {i + 1}/{num_slices} slices")
        
        # Create dataframe from all results
        if all_results:
            df = pd.DataFrame(all_results)
            
            # If we processed multiple blocks, group by coordinate and average again
            if len(blocks_to_process) > 1:
                coord_col = f'{axis}_mid'
                # Group by coordinate bins and average across all blocks
                grouped_cols = [col for col in df.columns if col != coord_col]
                df = df.groupby(coord_col)[grouped_cols].mean().reset_index()
            
            if len(blocks_to_process) == 1:
                print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            
            return df.sort_values(f'{axis}_mid')
        else:
            return pd.DataFrame()
    
    def compute_slice_averages(self, coordinate='y', num_slices=100, data_type='cell', block_name=None, block_id=None):
        """Alias for slice_and_average for consistency"""
        return self.slice_and_average(axis=coordinate, num_slices=num_slices, data_type=data_type, 
                                    block_name=block_name, block_id=block_id)
    
    def load_averaged_datasets(self, coordinate='y', num_slices=100, data_type='cell', block_name=None, block_id=None):
        """
        Load slice-averaged datasets for specified blocks
        
        Args:
            coordinate: 'x', 'y', or 'z' slicing direction
            num_slices: Number of slices to create
            data_type: 'cell' or 'point'
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            Dict of {block_name: DataFrame} for multiple blocks, or single DataFrame for one block
        """
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        
        if len(blocks_to_process) == 1:
            # Single block - return DataFrame directly
            block_display, block_idx = blocks_to_process[0]
            print(f"Loading averaged dataset for {block_display}...")
            df = self.slice_and_average(axis=coordinate, num_slices=num_slices, data_type=data_type,
                                      block_name=block_display, block_id=block_idx)
            return df
        else:
            # Multiple blocks - return dictionary
            datasets = {}
            for block_display, block_idx in blocks_to_process:
                try:
                    print(f"Loading averaged dataset for {block_display}...")
                    df = self.slice_and_average(axis=coordinate, num_slices=num_slices, data_type=data_type,
                                              block_name=block_display, block_id=block_idx)
                    if not df.empty:
                        datasets[block_display] = df
                        print(f"  ✓ Loaded {len(df)} averaged data points")
                    else:
                        print(f"  ✗ No data found for {block_display}")
                except Exception as e:
                    print(f"  ✗ Failed to load data for {block_display}: {e}")
                    continue
            
            return datasets
    
    def plot_contour_matplotlib(self, field_name='p', data_type='cell', n_contours=15, save_path=None, block_name=None, block_id=None):
        """
        Create 2D contour plot using matplotlib
        
        Args:
            field_name: Variable to plot
            data_type: 'cell' or 'point'
            n_contours: Number of contour levels
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            List of saved file paths
        """
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        saved_files = []
        
        for block_display, block_idx in blocks_to_process:
            print(f"Creating matplotlib contour for field '{field_name}' from {block_display}...")
            
            try:
                # Extract data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                # Project to 2D (X-Y plane)
                x = coords[:, 0]
                y = coords[:, 1]
                
                print(f"  Data points: {len(x)}")
                print(f"  X range: {x.min():.3f} to {x.max():.3f}")
                print(f"  Y range: {y.min():.3f} to {y.max():.3f}")
                print(f"  {field_name} range: {field_values.min():.3f} to {field_values.max():.3f}")
                
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
                ax.set_title(f'Contour Plot: {field_name} ({block_display}, {data_type} data)')
                ax.set_aspect('equal')
                
                # Save
                if save_path is None:
                    file_path = f'contour_{field_name}_{block_display.replace(" ", "_")}.png'
                else:
                    # If multiple blocks, modify the save_path
                    if len(blocks_to_process) > 1:
                        base, ext = save_path.rsplit('.', 1)
                        file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                    else:
                        file_path = save_path
                        
                plt.savefig(file_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"  ✓ Contour plot saved: {file_path}")
                saved_files.append(file_path)
                
            except Exception as e:
                print(f"  ✗ Failed to create contour for {block_display}: {e}")
                continue
        
        return saved_files
    
    def plot_contour_plotly(self, field_name='p', data_type='cell', save_path=None, block_name=None, block_id=None):
        """Create 3D scatter plot using plotly (using block name or ID)"""
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        # Handle block specification
        if block_name is not None:
            block_idx = self.get_block_index(block_name)
            block_display = block_name
        elif block_id is not None:
            block_idx = block_id
            block_display = f"Block {block_id} ({self.block_names[block_id]})"
        else:
            block_idx = 0  # Default to first block
            block_display = f"Block 0 ({self.block_names[0]})"
        
        print(f"Creating plotly 3D plot for field '{field_name}' from {block_display}...")
        
        # Extract data
        coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_name, block_id=block_idx)
        
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
            title=f'3D Visualization: {field_name} ({block_display})',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            width=1000,
            height=800
        )
        
        # Save
        if save_path is None:
            save_path = f'3d_{field_name}_{block_display.replace(" ", "_")}.html'
        pyo.plot(fig, filename=save_path, auto_open=False)
        
        print(f"✓ 3D plot saved: {save_path}")
        return save_path
    
    def plot_contour_plotly_surface(self, field_name='p', data_type='cell', save_path=None, block_name=None, block_id=None):
        """
        Create 3D surface plot using plotly
        
        Args:
            field_name: Variable to plot
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            List of saved file paths
        """
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        saved_files = []
        
        for block_display, block_idx in blocks_to_process:
            print(f"Creating plotly 3D surface for field '{field_name}' from {block_display}...")
            
            try:
                # Extract data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                # Project to 2D for surface (use X-Y plane, Z will be the field value)
                x = coords[:, 0]
                y = coords[:, 1]
                z = field_values
                
                # Create regular grid for surface
                resolution = 50  # Adjust for surface resolution
                xi = np.linspace(x.min(), x.max(), resolution)
                yi = np.linspace(y.min(), y.max(), resolution)
                Xi, Yi = np.meshgrid(xi, yi)
                
                # Interpolate field values to grid
                Zi = griddata((x, y), z, (Xi, Yi), method='linear')
                
                # Create surface plot
                fig = go.Figure(data=go.Surface(
                    x=Xi,
                    y=Yi,
                    z=Zi,
                    colorscale='Viridis',
                    colorbar=dict(title=field_name)
                ))
                
                fig.update_layout(
                    title=f'3D Surface: {field_name} ({block_display})',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title=field_name,
                        camera=dict(
                            eye=dict(x=1.5, y=1.5, z=1.5)
                        )
                    ),
                    width=1000,
                    height=800
                )
                
                # Save
                if save_path is None:
                    file_path = f'3d_surface_{field_name}_{block_display.replace(" ", "_")}.html'
                else:
                    # If multiple blocks, modify the save_path
                    if len(blocks_to_process) > 1:
                        base, ext = save_path.rsplit('.', 1)
                        file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                    else:
                        file_path = save_path
                        
                pyo.plot(fig, filename=file_path, auto_open=False)
                
                print(f"  ✓ 3D surface plot saved: {file_path}")
                saved_files.append(file_path)
                
            except Exception as e:
                print(f"  ✗ Failed to create 3D surface for {block_display}: {e}")
                continue
        
        return saved_files
    
    def plot_surface_contours_plotly(self, field_name='p', data_type='cell', save_path=None, block_name=None, block_id=None, projection_axis='z'):
        """
        Create 2D contour plots projected on coordinate surfaces using plotly
        
        Args:
            field_name: Variable to plot
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            projection_axis: Axis to use as contour levels ('x', 'y', or 'z')
            
        Returns:
            List of saved file paths
        """
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        saved_files = []
        
        for block_display, block_idx in blocks_to_process:
            print(f"Creating surface contours for field '{field_name}' from {block_display}...")
            
            try:
                # Extract data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                # Determine coordinate mapping
                coord_map = {'x': 0, 'y': 1, 'z': 2}
                proj_idx = coord_map[projection_axis]
                
                # Create projection - project to surface perpendicular to projection_axis
                if projection_axis == 'z':
                    # Project to X-Y plane
                    x = coords[:, 0]
                    y = coords[:, 1]
                    z_contour = field_values
                    x_label, y_label = 'X', 'Y'
                elif projection_axis == 'y':
                    # Project to X-Z plane
                    x = coords[:, 0]
                    y = coords[:, 2]
                    z_contour = field_values
                    x_label, y_label = 'X', 'Z'
                else:  # projection_axis == 'x'
                    # Project to Y-Z plane
                    x = coords[:, 1]
                    y = coords[:, 2]
                    z_contour = field_values
                    x_label, y_label = 'Y', 'Z'
                
                # Create regular grid for contours
                resolution = 100
                xi = np.linspace(x.min(), x.max(), resolution)
                yi = np.linspace(y.min(), y.max(), resolution)
                Xi, Yi = np.meshgrid(xi, yi)
                
                # Interpolate field values to grid
                Zi = griddata((x, y), z_contour, (Xi, Yi), method='linear')
                
                # Create contour plot
                fig = go.Figure(data=go.Contour(
                    x=xi,
                    y=yi,
                    z=Zi,
                    colorscale='Viridis',
                    contours=dict(
                        showlabels=True,
                        labelfont=dict(size=12, color='white')
                    ),
                    colorbar=dict(title=field_name)
                ))
                
                fig.update_layout(
                    title=f'Surface Contours: {field_name} ({block_display}) - {projection_axis.upper()}-projection',
                    xaxis_title=x_label,
                    yaxis_title=y_label,
                    width=800,
                    height=600
                )
                
                # Save
                if save_path is None:
                    file_path = f'surface_contour_{field_name}_{projection_axis}proj_{block_display.replace(" ", "_")}.html'
                else:
                    # If multiple blocks, modify the save_path
                    if len(blocks_to_process) > 1:
                        base, ext = save_path.rsplit('.', 1)
                        file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                    else:
                        file_path = save_path
                        
                pyo.plot(fig, filename=file_path, auto_open=False)
                
                print(f"  ✓ Surface contour plot saved: {file_path}")
                saved_files.append(file_path)
                
            except Exception as e:
                print(f"  ✗ Failed to create surface contours for {block_display}: {e}")
                continue
        
        return saved_files
    
    def plot_geometry_surface_contours(self, field_name='p', data_type='cell', save_path=None, block_name=None, block_id=None):
        """
        Create 3D surface contour plots showing field values on actual geometry surfaces
        
        Args:
            field_name: Variable to plot
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            List of saved file paths
        """
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        saved_files = []
        
        for block_display, block_idx in blocks_to_process:
            print(f"Creating geometry surface contours for field '{field_name}' from {block_display}...")
            
            try:
                # Get the VTK block
                block = self.data[block_idx]
                
                # Extract coordinates and field data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                if data_type == 'cell':
                    # For cell data, we need to get cell centers and connectivity
                    # Extract the surface of the 3D mesh
                    surface_filter = vtk.vtkDataSetSurfaceFilter()
                    surface_filter.SetInputData(block)
                    surface_filter.Update()
                    surface = surface_filter.GetOutput()
                    
                    # Get surface points
                    points = surface.GetPoints()
                    n_points = points.GetNumberOfPoints()
                    surface_coords = np.zeros((n_points, 3))
                    
                    for i in range(n_points):
                        point = points.GetPoint(i)
                        surface_coords[i] = [point[0], point[1], point[2]]
                    
                    # Get surface cells and field values
                    n_cells = surface.GetNumberOfCells()
                    faces = []
                    surface_field_values = []
                    
                    # Get field data array
                    if data_type == 'cell':
                        field_array = block.GetCellData().GetArray(field_name)
                    else:
                        field_array = block.GetPointData().GetArray(field_name)
                    
                    # Extract triangular faces and corresponding field values
                    for i in range(n_cells):
                        cell = surface.GetCell(i)
                        if cell.GetNumberOfPoints() == 3:  # Triangle
                            face = [cell.GetPointId(j) for j in range(3)]
                            faces.append(face)
                            
                            # For cell data on surface, we need to map back to original cell
                            # This is simplified - in practice you might need more sophisticated mapping
                            if i < len(field_values):
                                surface_field_values.append(field_values[i])
                            else:
                                surface_field_values.append(field_values[0])  # Default value
                        elif cell.GetNumberOfPoints() == 4:  # Quad - split into triangles
                            # Split quad into two triangles
                            face1 = [cell.GetPointId(0), cell.GetPointId(1), cell.GetPointId(2)]
                            face2 = [cell.GetPointId(0), cell.GetPointId(2), cell.GetPointId(3)]
                            faces.extend([face1, face2])
                            
                            # Same field value for both triangles
                            val = field_values[i] if i < len(field_values) else field_values[0]
                            surface_field_values.extend([val, val])
                    
                    # Create the mesh plot
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=surface_coords[:, 0],
                            y=surface_coords[:, 1], 
                            z=surface_coords[:, 2],
                            i=[face[0] for face in faces],
                            j=[face[1] for face in faces],
                            k=[face[2] for face in faces],
                            intensity=surface_field_values,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title=field_name),
                            name=f'{field_name} on {block_display}'
                        )
                    ])
                    
                else:  # point data
                    # For point data, it's more straightforward
                    surface_filter = vtk.vtkDataSetSurfaceFilter()
                    surface_filter.SetInputData(block)
                    surface_filter.Update()
                    surface = surface_filter.GetOutput()
                    
                    # Get surface points
                    points = surface.GetPoints()
                    n_points = points.GetNumberOfPoints()
                    surface_coords = np.zeros((n_points, 3))
                    
                    for i in range(n_points):
                        point = points.GetPoint(i)
                        surface_coords[i] = [point[0], point[1], point[2]]
                    
                    # Get surface cells (faces)
                    n_cells = surface.GetNumberOfCells()
                    faces = []
                    
                    for i in range(n_cells):
                        cell = surface.GetCell(i)
                        if cell.GetNumberOfPoints() == 3:  # Triangle
                            face = [cell.GetPointId(j) for j in range(3)]
                            faces.append(face)
                        elif cell.GetNumberOfPoints() == 4:  # Quad - split into triangles
                            face1 = [cell.GetPointId(0), cell.GetPointId(1), cell.GetPointId(2)]
                            face2 = [cell.GetPointId(0), cell.GetPointId(2), cell.GetPointId(3)]
                            faces.extend([face1, face2])
                    
                    # Map field values to surface points
                    surface_field_values = field_values[:n_points] if len(field_values) >= n_points else np.pad(field_values, (0, n_points - len(field_values)), 'edge')
                    
                    # Create the mesh plot
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=surface_coords[:, 0],
                            y=surface_coords[:, 1], 
                            z=surface_coords[:, 2],
                            i=[face[0] for face in faces],
                            j=[face[1] for face in faces],
                            k=[face[2] for face in faces],
                            intensity=surface_field_values,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title=field_name),
                            name=f'{field_name} on {block_display}'
                        )
                    ])
                
                # Update layout
                fig.update_layout(
                    title=f'Geometry Surface Contours: {field_name} ({block_display})',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z',
                        camera=dict(
                            eye=dict(x=1.5, y=1.5, z=1.5)
                        ),
                        aspectmode='data'
                    ),
                    width=1000,
                    height=800
                )
                
                # Save
                if save_path is None:
                    file_path = f'geometry_surface_contour_{field_name}_{block_display.replace(" ", "_")}.html'
                else:
                    # If multiple blocks, modify the save_path
                    if len(blocks_to_process) > 1:
                        base, ext = save_path.rsplit('.', 1)
                        file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                    else:
                        file_path = save_path
                        
                pyo.plot(fig, filename=file_path, auto_open=False)
                
                print(f"  ✓ Geometry surface contour plot saved: {file_path}")
                saved_files.append(file_path)
                
            except Exception as e:
                print(f"  ✗ Failed to create geometry surface contours for {block_display}: {e}")
                continue
        
        return saved_files
    
    def plot_geometry_surface_contours_combined(self, field_name='p', data_type='cell', save_path=None, block_name=None, block_id=None, camera_view='isometric'):
        """
        Create a single 3D surface contour plot combining all specified blocks
        
        Args:
            field_name: Variable to plot
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            camera_view: Camera orientation - 'isometric', 'front', 'side', 'top', 'custom', or dict with camera settings
            
        Returns:
            Dict with 'html' and 'png' file paths
        """
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
        except ImportError:
            raise ImportError("Plotly not available")
        
        # Define camera positions for different views
        def get_camera_position(view_type):
            """Get camera position for different standard views
            
            Coordinate system: +Y=Up, -Y=Down, +X=Right, -X=Left, +Z=Front, -Z=Back
            """
            camera_positions = {
                'isometric': dict(eye=dict(x=1.25, y=1.25, z=1.25), up=dict(x=0, y=1, z=0)),  # Standard isometric: right-up-front
                'front': dict(eye=dict(x=0, y=0, z=2.5), up=dict(x=0, y=1, z=0)),     # Front view (looking from +Z toward -Z)
                'back': dict(eye=dict(x=0, y=0, z=-2.5), up=dict(x=0, y=1, z=0)),     # Back view (looking from -Z toward +Z)
                'side': dict(eye=dict(x=2.5, y=0, z=0), up=dict(x=0, y=1, z=0)),      # Side view (looking from +X toward -X)
                'right': dict(eye=dict(x=2.5, y=0, z=0), up=dict(x=0, y=1, z=0)),     # Right side view (looking from +X toward -X)
                'left': dict(eye=dict(x=-2.5, y=0, z=0), up=dict(x=0, y=1, z=0)),     # Left side view (looking from -X toward +X)
                'top': dict(eye=dict(x=0, y=2.5, z=0), up=dict(x=0, y=0, z=1)),       # Top view (looking from +Y down toward -Y, +Z is up)
                'bottom': dict(eye=dict(x=0, y=-2.5, z=0), up=dict(x=0, y=0, z=-1)),   # Bottom view (looking from -Y up toward +Y, -Z is up)
                'perspective': dict(eye=dict(x=1.5, y=1.5, z=1.5), up=dict(x=0, y=1, z=0)),  # Perspective: right-up-front
                'close_isometric': dict(eye=dict(x=0.8, y=0.8, z=0.8), up=dict(x=0, y=1, z=0)),  # Closer isometric: right-up-front
                'far_isometric': dict(eye=dict(x=2.0, y=2.0, z=2.0), up=dict(x=0, y=1, z=0)),   # Farther isometric: right-up-front
            }
            return camera_positions.get(view_type, camera_positions['isometric'])
        
        # Set camera position
        if isinstance(camera_view, dict):
            camera_settings = camera_view
        else:
            camera_settings = get_camera_position(camera_view)
        
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        
        print(f"Creating combined geometry surface contours for field '{field_name}' from {len(blocks_to_process)} blocks...")
        print(f"Using camera view: {camera_view}")
        
        # Create figure with all blocks
        fig = go.Figure()
        
        # Track min/max values across all blocks for consistent color scale
        all_field_values = []
        
        for block_display, block_idx in blocks_to_process:
            try:
                # Get the VTK block
                block = self.data[block_idx]
                
                # Extract coordinates and field data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                print(f"    Block {block_display}: Original data has {len(field_values)} {data_type} values")
                print(f"    Block type: {type(block).__name__}")
                print(f"    Block cells: {block.GetNumberOfCells()}, points: {block.GetNumberOfPoints()}")
                
                # Debug: List all available arrays
                cell_data = block.GetCellData()
                point_data = block.GetPointData()
                print(f"    Available cell arrays: {[cell_data.GetArrayName(i) for i in range(cell_data.GetNumberOfArrays())]}")
                print(f"    Available point arrays: {[point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays())]}")
                
                if data_type == 'cell':
                    # ROBUST APPROACH: Use point data for surface visualization
                    # This avoids the complex cell-to-surface mapping issues
                    
                    # First convert cell data to point data for proper surface mapping
                    cell_to_point = vtk.vtkCellDataToPointData()
                    cell_to_point.SetInputData(block)
                    cell_to_point.PassCellDataOn()  # Keep cell data too
                    cell_to_point.Update()
                    point_data_block = cell_to_point.GetOutput()
                    
                    print(f"    Converted cell data to point data for surface mapping")
                    
                    # Now extract surface from the point data version
                    geometry_filter = vtk.vtkGeometryFilter()
                    geometry_filter.SetInputData(point_data_block)
                    geometry_filter.Update()
                    surface = geometry_filter.GetOutput()
                    
                    print(f"    Surface extraction: {surface.GetNumberOfCells()} cells, {surface.GetNumberOfPoints()} points")
                    
                    # Get surface points
                    points = surface.GetPoints()
                    n_points = points.GetNumberOfPoints()
                    surface_coords = np.zeros((n_points, 3))
                    
                    for i in range(n_points):
                        point = points.GetPoint(i)
                        surface_coords[i] = [point[0], point[1], point[2]]
                    
                    # Get the field data from point data (converted from cell data)
                    surface_point_data = surface.GetPointData()
                    surface_field_array = surface_point_data.GetArray(field_name)
                    
                    if surface_field_array is not None:
                        print(f"    SUCCESS: Field '{field_name}' found on surface points with {surface_field_array.GetNumberOfTuples()} values")
                        # Extract field values from surface points
                        surface_field_values = np.zeros(n_points)
                        for i in range(n_points):
                            surface_field_values[i] = surface_field_array.GetValue(i)
                        
                        # Extract faces - for point data we assign values to vertices
                        n_cells = surface.GetNumberOfCells()
                        faces = []
                        
                        for i in range(n_cells):
                            cell = surface.GetCell(i)
                            n_cell_points = cell.GetNumberOfPoints()
                            
                            if n_cell_points == 3:  # Triangle
                                face = [cell.GetPointId(j) for j in range(3)]
                                faces.append(face)
                            elif n_cell_points == 4:  # Quad - split into triangles
                                face1 = [cell.GetPointId(0), cell.GetPointId(1), cell.GetPointId(2)]
                                face2 = [cell.GetPointId(0), cell.GetPointId(2), cell.GetPointId(3)]
                                faces.extend([face1, face2])
                            elif n_cell_points > 4:  # Polygon - triangulate from first vertex
                                for j in range(1, n_cell_points - 1):
                                    face = [cell.GetPointId(0), cell.GetPointId(j), cell.GetPointId(j + 1)]
                                    faces.append(face)
                        
                        # For point data, we use the surface_field_values directly (assigned to vertices)
                        final_field_values = surface_field_values
                        all_field_values.extend(final_field_values)
                        print(f"    Final: {len(faces)} faces, {len(final_field_values)} point values")
                        print(f"    Field value range: {min(final_field_values):.6f} to {max(final_field_values):.6f}")
                        
                    else:
                        print(f"    ERROR: Field '{field_name}' not found on surface points!")
                        surface_point_data_names = [surface_point_data.GetArrayName(i) for i in range(surface_point_data.GetNumberOfArrays())]
                        print(f"    Available surface point arrays: {surface_point_data_names}")
                        # Skip this block if field is not available
                        continue
                    
                    if len(faces) == 0:
                        print(f"    WARNING: No faces extracted for {block_display}")
                        continue
                    
                else:  # point data
                    # Extract the surface of the 3D mesh
                    surface_filter = vtk.vtkDataSetSurfaceFilter()
                    surface_filter.SetInputData(block)
                    surface_filter.Update()
                    surface = surface_filter.GetOutput()
                    
                    # Get surface points
                    points = surface.GetPoints()
                    n_points = points.GetNumberOfPoints()
                    surface_coords = np.zeros((n_points, 3))
                    
                    for i in range(n_points):
                        point = points.GetPoint(i)
                        surface_coords[i] = [point[0], point[1], point[2]]
                    
                    # Get surface cells (faces)
                    n_cells = surface.GetNumberOfCells()
                    faces = []
                    
                    for i in range(n_cells):
                        cell = surface.GetCell(i)
                        if cell.GetNumberOfPoints() == 3:  # Triangle
                            face = [cell.GetPointId(j) for j in range(3)]
                            faces.append(face)
                        elif cell.GetNumberOfPoints() == 4:  # Quad - split into triangles
                            face1 = [cell.GetPointId(0), cell.GetPointId(1), cell.GetPointId(2)]
                            face2 = [cell.GetPointId(0), cell.GetPointId(2), cell.GetPointId(3)]
                            faces.extend([face1, face2])
                    
                    # Map field values to surface points
                    final_field_values = field_values[:n_points] if len(field_values) >= n_points else np.pad(field_values, (0, n_points - len(field_values)), 'edge')
                    all_field_values.extend(final_field_values)
                
                # Add this block to the figure
                fig.add_trace(go.Mesh3d(
                    x=surface_coords[:, 0],
                    y=surface_coords[:, 1], 
                    z=surface_coords[:, 2],
                    i=[face[0] for face in faces],
                    j=[face[1] for face in faces],
                    k=[face[2] for face in faces],
                    intensity=final_field_values,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title=field_name),
                    name=block_display,
                    cmin=min(all_field_values) if all_field_values else None,
                    cmax=max(all_field_values) if all_field_values else None
                ))
                
                print(f"  ✓ Added {block_display} to combined plot")
                
            except Exception as e:
                print(f"  ✗ Failed to add {block_display} to combined plot: {e}")
                continue
        
        if not fig.data:
            raise ValueError("No blocks could be processed successfully")
        
        # Set consistent color scale for all blocks
        if all_field_values:
            field_min, field_max = min(all_field_values), max(all_field_values)
            for trace in fig.data:
                trace.cmin = field_min
                trace.cmax = field_max
        
        # Update layout
        block_list = [block_display for block_display, _ in blocks_to_process]
        title_blocks = "All Blocks" if len(block_list) > 3 else ", ".join(block_list)
        
        fig.update_layout(
            title=f'Combined Geometry Surface Contours: {field_name} ({title_blocks})',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                camera=camera_settings,
                aspectmode='data'
            ),
            width=1200,
            height=900
        )
        
        # Save HTML
        if save_path is None:
            html_path = f'geometry_surface_contour_combined_{field_name}_all_blocks.html'
        else:
            html_path = save_path
        
        pyo.plot(fig, filename=html_path, auto_open=False)
        print(f"  ✓ Combined geometry surface contour plot saved: {html_path}")
        
        # Also save as PNG for PowerPoint compatibility
        try:
            # Generate PNG filename from HTML filename
            if html_path.endswith('.html'):
                png_path = html_path.replace('.html', '.png')
            else:
                png_path = f'{html_path}.png'
            
            # Try to save as PNG using kaleido (if available)
            try:
                fig.write_image(png_path, width=1200, height=900, scale=2)
                print(f"  ✓ PNG file saved: {png_path}")
                return {'html': html_path, 'png': png_path}
            except Exception as e:
                print(f"  ⚠ PNG export failed: {e}")
                print(f"    Install 'kaleido' package for PNG export: pip install kaleido")
                return {'html': html_path, 'png': None}
                
        except Exception as e:
            print(f"  ⚠ PNG export error: {e}")
            return {'html': html_path, 'png': None}
    
    def export_html_to_png(self, html_file_path, png_file_path=None, width=1200, height=900, scale=2):
        """
        Convert existing HTML Plotly files to PNG for PowerPoint compatibility
        
        Args:
            html_file_path: Path to existing HTML file
            png_file_path: Output PNG path (if None, auto-generated)
            width: Image width in pixels
            height: Image height in pixels
            scale: Scale factor for higher resolution
            
        Returns:
            PNG file path if successful, None if failed
        """
        try:
            import plotly.io as pio
            import plotly.graph_objects as go
            from plotly.offline import plot
            import json
        except ImportError:
            print("Plotly not available for PNG export")
            return None
        
        if not os.path.exists(html_file_path):
            print(f"HTML file not found: {html_file_path}")
            return None
        
        # Generate PNG filename if not provided
        if png_file_path is None:
            if html_file_path.endswith('.html'):
                png_file_path = html_file_path.replace('.html', '.png')
            else:
                png_file_path = f'{html_file_path}.png'
        
        try:
            # Read the HTML file and extract the Plotly figure
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract JSON data from HTML (this is a simplified approach)
            # For a more robust solution, you might need to parse the HTML more carefully
            start_marker = 'Plotly.newPlot('
            end_marker = ',{"responsive":true}'
            
            start_idx = html_content.find(start_marker)
            if start_idx == -1:
                raise ValueError("Could not find Plotly data in HTML file")
            
            # This is a simplified extraction - for production use, consider using BeautifulSoup
            print(f"  ⚠ For robust HTML to PNG conversion, recommend using:")
            print(f"    1. Save both HTML and PNG during plot creation")
            print(f"    2. Use browser automation tools like Selenium")
            print(f"    3. Use plotly.graph_objects.Figure.write_image() during creation")
            
            return None
            
        except Exception as e:
            print(f"  ✗ Failed to convert {html_file_path} to PNG: {e}")
            print(f"    Install 'kaleido' package: pip install kaleido")
            print(f"    Or use the combined method which saves both HTML and PNG")
            return None
    
    def batch_convert_html_to_png(self, html_directory, png_directory=None):
        """
        Convert all HTML files in a directory to PNG
        
        Args:
            html_directory: Directory containing HTML files
            png_directory: Output directory for PNG files (if None, same as HTML dir)
            
        Returns:
            List of successfully converted files
        """
        if png_directory is None:
            png_directory = html_directory
        
        if not os.path.exists(html_directory):
            print(f"Directory not found: {html_directory}")
            return []
        
        os.makedirs(png_directory, exist_ok=True)
        
        html_files = [f for f in os.listdir(html_directory) if f.endswith('.html')]
        converted_files = []
        
        print(f"Converting {len(html_files)} HTML files to PNG...")
        
        for html_file in html_files:
            html_path = os.path.join(html_directory, html_file)
            png_file = html_file.replace('.html', '.png')
            png_path = os.path.join(png_directory, png_file)
            
            result = self.export_html_to_png(html_path, png_path)
            if result:
                converted_files.append(result)
        
        print(f"Successfully converted {len(converted_files)} files")
        return converted_files
    
    def plot_line_vs_coordinate(self, field_name='p', coordinate='y', data_type='cell', save_path=None, block_name=None, block_id=None):
        """
        Create line plot of field vs coordinate
        
        Args:
            field_name: Variable to plot
            coordinate: 'x', 'y', or 'z' coordinate
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            List of saved file paths
        """
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        saved_files = []
        
        for block_display, block_idx in blocks_to_process:
            print(f"Creating line plot for field '{field_name}' vs {coordinate} from {block_display}...")
            
            try:
                # Extract data
                coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_display, block_id=block_idx)
                
                # Get coordinate values
                coord_index = {'x': 0, 'y': 1, 'z': 2}[coordinate]
                coord_values = coords[:, coord_index]
                
                # Sort by coordinate for better line plot
                sort_indices = np.argsort(coord_values)
                sorted_coords = coord_values[sort_indices]
                sorted_values = field_values[sort_indices]
                
                print(f"Data points: {len(sorted_coords)}")
                print(f"{coordinate} range: {sorted_coords.min():.3f} to {sorted_coords.max():.3f}")
                print(f"{field_name} range: {sorted_values.min():.3f} to {sorted_values.max():.3f}")
                
                # Create plot
                plt.figure(figsize=(10, 6))
                plt.plot(sorted_coords, sorted_values, 'b-', alpha=0.7, linewidth=1, label=f'{field_name} ({block_display})')
                
                plt.xlabel(coordinate.upper())
                plt.ylabel(field_name)
                plt.title(f'Line Plot: {field_name} vs {coordinate.upper()} ({block_display})')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Save
                if save_path is None:
                    file_path = f'line_{field_name}_vs_{coordinate}_{block_display.replace(" ", "_")}.png'
                else:
                    # If multiple blocks, modify the save_path
                    if len(blocks_to_process) > 1:
                        base, ext = save_path.rsplit('.', 1)
                        file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                    else:
                        file_path = save_path
                        
                plt.savefig(file_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"  ✓ Line plot saved: {file_path}")
                saved_files.append(file_path)
                
            except Exception as e:
                print(f"  ✗ Failed to create line plot for {block_display}: {e}")
                continue
        
        return saved_files
    
    def plot_averaged_lines(self, dataframe=None, field_names=None, coordinate='y', save_path=None, block_name=None, block_id=None):
        """
        Create line plots from slice-averaged data
        
        Args:
            dataframe: DataFrame with averaged data (if None, computes from blocks)
            field_names: List of field names to plot
            coordinate: 'x', 'y', or 'z' coordinate
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            List of saved file paths
        """
        if dataframe is not None:
            # Single dataframe provided
            if dataframe.empty:
                print("No data to plot")
                return []
            
            if field_names is None:
                # Get all columns that end with '_avg'
                field_names = [col for col in dataframe.columns if col.endswith('_avg')]
            
            coord_col = f'{coordinate}_mid'
            if coord_col not in dataframe.columns:
                print(f"Coordinate column '{coord_col}' not found in dataframe")
                return []
            
            display_name = block_name if block_name else "Data"
            print(f"Creating averaged line plots for {len(field_names)} fields from {display_name}...")
            
            plt.figure(figsize=(12, 8))
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(field_names)))
            
            for i, field_name in enumerate(field_names):
                if field_name in dataframe.columns:
                    # Remove NaN values for cleaner plots
                    clean_data = dataframe.dropna(subset=[coord_col, field_name])
                    if not clean_data.empty:
                        plt.plot(clean_data[coord_col], clean_data[field_name], 
                               'o-', color=colors[i], alpha=0.8, linewidth=2, markersize=4,
                               label=field_name.replace('_avg', ''))
            
            plt.xlabel(f'{coordinate.upper()} Coordinate')
            plt.ylabel('Averaged Field Values')
            plt.title(f'Slice-Averaged Fields vs {coordinate.upper()} ({display_name})')
            plt.grid(True, alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Save
            if save_path is None:
                save_path = f'averaged_lines_vs_{coordinate}_{display_name.replace(" ", "_")}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Averaged line plot saved: {save_path}")
            return [save_path]
        
        else:
            # Generate from blocks
            blocks_to_process = self._resolve_blocks(block_name, block_id)
            saved_files = []
            
            for block_display, block_idx in blocks_to_process:
                try:
                    # Compute averaged data
                    df = self.compute_slice_averages(coordinate=coordinate, block_name=block_display, block_id=block_idx)
                    
                    # Recursively call with the dataframe
                    result = self.plot_averaged_lines(dataframe=df, field_names=field_names, 
                                                    coordinate=coordinate, save_path=None, 
                                                    block_name=block_display)
                    saved_files.extend(result)
                    
                except Exception as e:
                    print(f"  ✗ Failed to create averaged lines for {block_display}: {e}")
                    continue
            
            return saved_files
    
    def plot_overlay_averaged_lines(self, dataframes_dict=None, field_name=None, coordinate='y', save_path=None, block_name=None, block_id=None):
        """
        Create overlay plot from multiple averaged dataframes
        
        Args:
            dataframes_dict: Dict of {block_name: dataframe} (if None, computes from blocks)
            field_name: Field to plot
            coordinate: 'x', 'y', or 'z' coordinate
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            Saved file path
        """
        if dataframes_dict is not None:
            # Dataframes provided directly
            coord_col = f'{coordinate}_mid'
            field_col = f'{field_name}_avg'
            
            plt.figure(figsize=(12, 8))
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(dataframes_dict)))
            
            for i, (block_name, df) in enumerate(dataframes_dict.items()):
                if not df.empty and field_col in df.columns:
                    clean_data = df.dropna(subset=[coord_col, field_col])
                    if not clean_data.empty:
                        plt.plot(clean_data[coord_col], clean_data[field_col], 
                               'o-', color=colors[i], alpha=0.8, linewidth=2, markersize=4,
                               label=f'{field_name} ({block_name})')
            
            plt.xlabel(f'{coordinate.upper()} Coordinate')
            plt.ylabel(f'{field_name} (Averaged)')
            plt.title(f'Slice-Averaged {field_name} vs {coordinate.upper()} - All Blocks')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save
            if save_path is None:
                save_path = f'overlay_averaged_{field_name}_vs_{coordinate}.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Averaged overlay plot saved: {save_path}")
            return save_path
        
        else:
            # Generate from blocks
            if field_name is None:
                raise ValueError("field_name must be provided when generating from blocks")
                
            blocks_to_process = self._resolve_blocks(block_name, block_id)
            
            # Compute averaged data for all blocks
            dataframes_dict = {}
            for block_display, block_idx in blocks_to_process:
                try:
                    df = self.compute_slice_averages(coordinate=coordinate, block_name=block_display, block_id=block_idx)
                    if not df.empty:
                        dataframes_dict[block_display] = df
                except Exception as e:
                    print(f"  ✗ Failed to compute averages for {block_display}: {e}")
                    continue
            
            # Recursively call with the dataframes
            if dataframes_dict:
                return self.plot_overlay_averaged_lines(dataframes_dict=dataframes_dict, 
                                                      field_name=field_name, 
                                                      coordinate=coordinate, 
                                                      save_path=save_path)
            else:
                print("No valid data found for overlay plot")
                return None
    
    def plot_overlay_lines(self, field_names=None, coordinate='y', data_type='cell', save_path=None, block_names=None):
        """Create overlayed line plots for multiple fields/blocks"""
        if field_names is None:
            # Get all available fields from first block
            vars_info = self.get_variable_names(block_name=self.block_names[0], verbose=False)
            field_names = vars_info['cell_data'] if data_type == 'cell' else vars_info['point_data']
        
        if block_names is None:
            block_names = self.block_names
        
        coord_index = {'x': 0, 'y': 1, 'z': 2}[coordinate]
        
        plt.figure(figsize=(12, 8))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(field_names) * len(block_names)))
        color_idx = 0
        
        for block_name in block_names:
            try:
                # Get available fields for this block
                block_vars = self.get_variable_names(block_name=block_name, verbose=False)
                available_fields = block_vars['cell_data'] if data_type == 'cell' else block_vars['point_data']
                
                for field_name in field_names:
                    if field_name in available_fields:
                        try:
                            # Extract data
                            coords, field_values = self.extract_field_data(field_name, data_type, block_name=block_name)
                            
                            # Get coordinate values and sort
                            coord_values = coords[:, coord_index]
                            sort_indices = np.argsort(coord_values)
                            sorted_coords = coord_values[sort_indices]
                            sorted_values = field_values[sort_indices]
                            
                            # Plot
                            plt.plot(sorted_coords, sorted_values, 
                                   color=colors[color_idx], alpha=0.7, linewidth=1.5,
                                   label=f'{field_name} ({block_name})')
                            color_idx += 1
                            
                        except Exception as e:
                            print(f"Failed to plot {field_name} from {block_name}: {e}")
                            continue
            except Exception as e:
                print(f"Failed to process block {block_name}: {e}")
                continue
        
        plt.xlabel(coordinate.upper())
        plt.ylabel('Field Values')
        plt.title(f'Overlay Plot: Multiple Fields vs {coordinate.upper()}')
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Save
        if save_path is None:
            save_path = f'overlay_fields_vs_{coordinate}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Overlay plot saved: {save_path}")
        return save_path
    
    def plot_flexible_lines(self, x_var, y_var, datasets=None, coordinate='y', num_slices=100, 
                           data_type='cell', save_path=None, block_name=None, block_id=None, 
                           x_label=None, y_label=None, title=None):
        """
        Create flexible line plots with custom X and Y variables
        
        Args:
            x_var: X-axis variable name (e.g., 'y_mid', 'p_avg', 'U_avg')
            y_var: Y-axis variable name (e.g., 'p_avg', 'T_avg', 'U_avg')
            datasets: Pre-loaded datasets dict/DataFrame (if None, loads from blocks)
            coordinate: Slicing direction for averaging ('x', 'y', 'z')
            num_slices: Number of slices for averaging
            data_type: 'cell' or 'point'
            save_path: Output path (if None, auto-generated)
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            x_label: Custom X-axis label
            y_label: Custom Y-axis label
            title: Custom plot title
            
        Returns:
            List of saved file paths
        """
        
        # Load datasets if not provided
        if datasets is None:
            print("Loading averaged datasets...")
            datasets = self.load_averaged_datasets(coordinate=coordinate, num_slices=num_slices,
                                                 data_type=data_type, block_name=block_name, 
                                                 block_id=block_id)
        
        # Handle single DataFrame vs dictionary of DataFrames
        if isinstance(datasets, pd.DataFrame):
            # Single dataset
            datasets = {"Data": datasets}
        
        if not datasets:
            print("No datasets available for plotting")
            return []
        
        saved_files = []
        
        # Create individual plots for each dataset
        for block_display, df in datasets.items():
            if df.empty:
                print(f"No data for {block_display}")
                continue
                
            # Check if variables exist in dataframe
            if x_var not in df.columns:
                print(f"X variable '{x_var}' not found in {block_display}. Available: {list(df.columns)}")
                continue
            if y_var not in df.columns:
                print(f"Y variable '{y_var}' not found in {block_display}. Available: {list(df.columns)}")
                continue
            
            print(f"Creating flexible line plot: {y_var} vs {x_var} for {block_display}...")
            
            # Remove NaN values
            clean_data = df.dropna(subset=[x_var, y_var])
            if clean_data.empty:
                print(f"  No valid data points for {block_display}")
                continue
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.plot(clean_data[x_var], clean_data[y_var], 'o-', linewidth=2, markersize=4, alpha=0.8,
                    label=f'{y_var} ({block_display})')
            
            # Labels and titles
            x_axis_label = x_label if x_label else x_var.replace('_', ' ').title()
            y_axis_label = y_label if y_label else y_var.replace('_', ' ').title()
            plot_title = title if title else f'{y_axis_label} vs {x_axis_label} ({block_display})'
            
            plt.xlabel(x_axis_label)
            plt.ylabel(y_axis_label)
            plt.title(plot_title)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Data range info
            print(f"  Data points: {len(clean_data)}")
            print(f"  {x_var} range: {clean_data[x_var].min():.3f} to {clean_data[x_var].max():.3f}")
            print(f"  {y_var} range: {clean_data[y_var].min():.3f} to {clean_data[y_var].max():.3f}")
            
            # Save individual plot
            if save_path is None:
                file_path = f'flexible_line_{y_var}_vs_{x_var}_{block_display.replace(" ", "_")}.png'
            else:
                if len(datasets) > 1:
                    base, ext = save_path.rsplit('.', 1)
                    file_path = f'{base}_{block_display.replace(" ", "_")}.{ext}'
                else:
                    file_path = save_path
            
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ Flexible line plot saved: {file_path}")
            saved_files.append(file_path)
        
        # Create overlay plot if multiple datasets
        if len(datasets) > 1:
            print(f"Creating overlay plot: {y_var} vs {x_var} for all blocks...")
            
            plt.figure(figsize=(12, 8))
            colors = plt.cm.tab10(np.linspace(0, 1, len(datasets)))
            
            for i, (block_display, df) in enumerate(datasets.items()):
                if not df.empty and x_var in df.columns and y_var in df.columns:
                    clean_data = df.dropna(subset=[x_var, y_var])
                    if not clean_data.empty:
                        plt.plot(clean_data[x_var], clean_data[y_var], 'o-', color=colors[i],
                               linewidth=2, markersize=4, alpha=0.8, label=f'{block_display}')
            
            # Labels and titles for overlay
            x_axis_label = x_label if x_label else x_var.replace('_', ' ').title()
            y_axis_label = y_label if y_label else y_var.replace('_', ' ').title()
            plot_title = title if title else f'{y_axis_label} vs {x_axis_label} - All Blocks'
            
            plt.xlabel(x_axis_label)
            plt.ylabel(y_axis_label)
            plt.title(plot_title)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save overlay plot
            overlay_path = f'flexible_overlay_{y_var}_vs_{x_var}.png'
            plt.savefig(overlay_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ Overlay plot saved: {overlay_path}")
            saved_files.append(overlay_path)
        
        return saved_files
    
    def list_averaged_variables(self, coordinate='y', num_slices=10, data_type='cell', block_name=None, block_id=None):
        """
        List available variables in averaged datasets
        
        Args:
            coordinate: Slicing direction for averaging ('x', 'y', 'z')
            num_slices: Number of slices for averaging (small number for quick check)
            data_type: 'cell' or 'point'
            block_name: None (all blocks), str (single), or list (multiple)
            block_id: Block index (only used if block_name is None)
            
        Returns:
            Dict of {block_name: list_of_variables} or single list for one block
        """
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        
        if len(blocks_to_process) == 1:
            # Single block
            block_display, block_idx = blocks_to_process[0]
            print(f"Getting available variables for {block_display}...")
            
            # Get a small sample to check variables
            df = self.slice_and_average(axis=coordinate, num_slices=num_slices, data_type=data_type,
                                      block_name=block_display, block_id=block_idx)
            
            if not df.empty:
                variables = list(df.columns)
                print(f"Available variables ({len(variables)}): {variables}")
                return variables
            else:
                print("No data found")
                return []
        else:
            # Multiple blocks
            all_variables = {}
            for block_display, block_idx in blocks_to_process:
                try:
                    print(f"Getting available variables for {block_display}...")
                    df = self.slice_and_average(axis=coordinate, num_slices=num_slices, data_type=data_type,
                                              block_name=block_display, block_id=block_idx)
                    
                    if not df.empty:
                        variables = list(df.columns)
                        all_variables[block_display] = variables
                        print(f"  Variables ({len(variables)}): {variables}")
                    else:
                        print(f"  No data found for {block_display}")
                        all_variables[block_display] = []
                        
                except Exception as e:
                    print(f"  Error getting variables for {block_display}: {e}")
                    all_variables[block_display] = []
            
            return all_variables
    
    def plot_sliced_bar_chart(self, field_name, axis='y', num_slices=20, data_type='cell', 
                              block_name=None, block_id=None, save_path=None, 
                              chart_title=None, show_percentages=True, show_totals=True):
        """
        Create bar chart showing field distribution along specified axis with integrated slicing
        
        Args:
            field_name: Name of the field to analyze (e.g., 'heat_flux', 'pressure', 'temperature')
            axis: Axis along which to slice ('x', 'y', or 'z')
            num_slices: Number of slices to create
            data_type: 'cell' or 'point' data
            block_name: Block name(s) to process (None for all, str for single, list for multiple)
            block_id: Block ID if using ID instead of name
            save_path: Path to save the plot
            chart_title: Custom title for the chart
            show_percentages: Show percentage of total for each slice (good for heat flux)
            show_totals: Whether to show total field values
            
        Returns:
            Dictionary with results including DataFrame and plot path
        """
        import matplotlib.pyplot as plt
        import numpy as np
        
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        
        print(f"Creating sliced bar chart for field '{field_name}' along {axis}-axis...")
        print(f"Processing {len(blocks_to_process)} blocks with {num_slices} slices each")
        
        # Collect data from all blocks by calling slice_and_average directly
        all_slice_data = []
        block_totals = {}
        
        for block_display, block_idx in blocks_to_process:
            try:
                print(f"\nProcessing block: {block_display}")
                
                # Call slice_and_average directly to get fresh data
                df = self.slice_and_average(axis=axis, num_slices=num_slices, data_type=data_type,
                                          block_name=block_display, block_id=block_idx)
                
                if df.empty:
                    print(f"  No data found for {block_display}")
                    continue
                
                # Check if field exists
                field_col = f'{field_name}_avg'
                if field_col not in df.columns:
                    print(f"  Field '{field_name}' not found in {block_display}")
                    print(f"  Available fields: {[col.replace('_avg', '') for col in df.columns if col.endswith('_avg')]}")
                    continue
                
                # Add block identification and calculate values
                df['block_name'] = block_display
                df['field_value'] = df[field_col]
                
                # Calculate total for this block
                total_field_value = df[field_col].sum()
                block_totals[block_display] = total_field_value
                
                # Calculate percentages if requested
                if show_percentages and total_field_value > 0:
                    df['percentage'] = (df[field_col] / total_field_value) * 100
                else:
                    df['percentage'] = 0
                
                all_slice_data.append(df)
                print(f"  ✓ Processed {len(df)} slices, Total {field_name}: {total_field_value:.2e}")
                
            except Exception as e:
                print(f"  ✗ Failed to process {block_display}: {e}")
                continue
        
        if not all_slice_data:
            raise ValueError(f"No valid data found for {field_name} bar chart")
        
        # Combine all data
        combined_df = pd.concat(all_slice_data, ignore_index=True)
        
        # Determine what to plot: percentages for heat flux, raw values for others
        use_percentages = show_percentages and field_name.lower() in ['heat_flux', 'heat_transfer_rate', 'thermal_flux']
        
        # Create the bar chart
        plt.figure(figsize=(14, 8))
        
        # If multiple blocks, create grouped bar chart
        if len(blocks_to_process) > 1:
            # Get unique slice positions and block names
            axis_col = f'{axis}_mid'
            field_col = f'{field_name}_avg'
            slice_positions = sorted(combined_df[axis_col].unique())
            block_names_list = [block_display for block_display, _ in blocks_to_process]
            
            # Set up bar positions - calculate spatial bar width
            slice_positions = sorted(combined_df[axis_col].unique())
            if len(slice_positions) > 1:
                spatial_bar_width = slice_positions[1] - slice_positions[0]  # Actual slice thickness
            else:
                spatial_bar_width = 1.0
            
            # For multiple blocks, use grouped bars within each slice
            block_names_list = [block_display for block_display, _ in blocks_to_process]
            individual_bar_width = spatial_bar_width * 0.8 / len(block_names_list)  # Leave some space between groups
            offset_start = -(len(block_names_list) - 1) * individual_bar_width / 2
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(block_names_list)))
            
            for i, (block_display, _) in enumerate(blocks_to_process):
                block_data = combined_df[combined_df['block_name'] == block_display]
                if not block_data.empty:
                    # Align data with slice positions
                    if use_percentages:
                        plot_values = []
                        for pos in slice_positions:
                            matching_rows = block_data[block_data[axis_col] == pos]
                            if not matching_rows.empty:
                                value = matching_rows[field_col].iloc[0]
                                percentage = (value / block_totals[block_display]) * 100 if block_totals[block_display] != 0 else 0
                                plot_values.append(percentage)
                            else:
                                plot_values.append(0)
                        y_label = f'{field_name.replace("_", " ").title()} (%)'
                    else:
                        plot_values = []
                        for pos in slice_positions:
                            matching_rows = block_data[block_data[axis_col] == pos]
                            if not matching_rows.empty:
                                plot_values.append(matching_rows[field_col].iloc[0])
                            else:
                                plot_values.append(0)
                        y_label = f'{field_name.replace("_", " ").title()}'
                    
                    # Calculate bar positions for this block
                    bar_positions = np.array(slice_positions) + offset_start + i * individual_bar_width
                    
                    plt.bar(bar_positions, plot_values, individual_bar_width, 
                           label=f'{block_display} (Total: {block_totals[block_display]:.2e})',
                           color=colors[i], alpha=0.8)
            
            plt.xlabel(f'{axis.upper()} Position')
            plt.ylabel(y_label)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
        else:
            # Single block - simple bar chart
            axis_col = f'{axis}_mid'
            field_col = f'{field_name}_avg'
            block_display, _ = blocks_to_process[0]
            
            # Calculate proper bar width based on slice thickness
            positions = sorted(combined_df[axis_col])
            if len(positions) > 1:
                bar_width = positions[1] - positions[0]  # Use actual slice thickness
            else:
                bar_width = 1.0  # Fallback if only one slice
            
            if use_percentages:
                # Calculate percentages from field values
                field_values = combined_df[field_col]
                total_value = field_values.sum()
                percentages = (field_values / total_value * 100) if total_value != 0 else field_values * 0
                plt.bar(combined_df[axis_col], percentages, width=bar_width,
                       alpha=0.7, color='steelblue', edgecolor='navy')
                y_label = f'{field_name.replace("_", " ").title()} (%)'
            else:
                plt.bar(combined_df[axis_col], combined_df[field_col], width=bar_width,
                       alpha=0.7, color='steelblue', edgecolor='navy')
                y_label = f'{field_name.replace("_", " ").title()}'
            
            plt.xlabel(f'{axis.upper()} Position')
            plt.ylabel(y_label)
            plt.xticks(rotation=45)
        
        # Set title
        if chart_title:
            title = chart_title
        else:
            percentage_text = " (% Distribution)" if use_percentages else ""
            if len(blocks_to_process) > 1:
                title = f'{field_name.replace("_", " ").title()} Distribution{percentage_text} - All Blocks'
            else:
                title = f'{field_name.replace("_", " ").title()} Distribution{percentage_text} - {blocks_to_process[0][0]}'
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Add totals text if requested
        if show_totals and len(blocks_to_process) > 1:
            total_text = f"Total {field_name.replace('_', ' ').title()} by Block:\n"
            for block_name, total in block_totals.items():
                total_text += f"{block_name}: {total:.2e}\n"
            plt.figtext(0.02, 0.02, total_text, fontsize=9, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7))
        
        # Save plot
        if save_path is None:
            percentage_suffix = "_percentages" if use_percentages else ""
            if len(blocks_to_process) > 1:
                save_path = f'sliced_bar_chart_{field_name}_all_blocks_{axis}axis{percentage_suffix}.png'
            else:
                save_path = f'sliced_bar_chart_{field_name}_{blocks_to_process[0][0]}_{axis}axis{percentage_suffix}.png'
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Sliced bar chart saved: {save_path}")
        
        # Prepare results
        results = {
            'plot_path': save_path,
            'data': combined_df,
            'block_totals': block_totals,
            'total_value': sum(block_totals.values()),
            'num_slices': num_slices,
            'axis': axis,
            'field_name': field_name,
            'used_percentages': use_percentages
        }
        
        # Print summary
        print(f"\n=== Sliced Bar Chart Analysis Summary ===")
        print(f"Field: {field_name}")
        print(f"Analysis axis: {axis}")
        print(f"Number of slices: {num_slices}")
        print(f"Display mode: {'Percentages' if use_percentages else 'Raw values'}")
        print(f"Blocks processed: {len(blocks_to_process)}")
        if show_totals:
            print(f"\nTotal {field_name} by block:")
            for block_name, total in block_totals.items():
                print(f"  {block_name}: {total:.6e}")
            print(f"Grand total: {sum(block_totals.values()):.6e}")
        
        return results
    
    def plot_block_comparison_chart(self, field_name, output_dir='plots', save_png=True, 
                                   save_html=True, block_spec=None, show_totals=True,
                                   use_percentages=False):
        """
        Plot bar chart comparing total field values across blocks.
        
        Parameters:
        - field_name: Field to analyze (e.g., 'heat_flux')
        - output_dir: Directory to save plots
        - save_png: Whether to save PNG file
        - save_html: Whether to save HTML file
        - block_spec: Block specification (None for all, name for single, list for multiple)
        - show_totals: Whether to print totals
        - use_percentages: Whether to display values as percentages of total
        
        Returns:
        - Dictionary with block totals
        """
        import plotly.graph_objects as go
        import os
        import numpy as np
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Auto-determine percentage mode for heat flux fields
        auto_use_percentages = field_name.lower() in ['heat_flux', 'heat_transfer_rate', 'thermal_flux']
        if auto_use_percentages and not use_percentages:
            use_percentages = True
            print(f"Auto-enabled percentage mode for '{field_name}' field")
        
        # Get all available blocks
        all_blocks = self.get_block_names(verbose=False)
        
        # Determine which blocks to process
        if block_spec is None:
            blocks_to_process = all_blocks
        elif isinstance(block_spec, str):
            blocks_to_process = [block_spec] if block_spec in all_blocks else []
        elif isinstance(block_spec, list):
            blocks_to_process = [block for block in block_spec if block in all_blocks]
        else:
            blocks_to_process = all_blocks
        
        if not blocks_to_process:
            print("No valid blocks found to process")
            return {}
        
        # Calculate total field values per block
        block_totals = {}
        
        for block_name in blocks_to_process:
            try:
                # Get block by name using existing method
                block_index = self.get_block_index(block_name)
                if block_index is None:
                    print(f"Warning: Block '{block_name}' not found")
                    continue
                
                block_data = self.dataset.GetBlock(block_index)
                if block_data is None:
                    print(f"Warning: Block data for '{block_name}' is None")
                    continue
                
                # Get field array
                field_array = None
                
                # Check point data first
                point_data = block_data.GetPointData()
                if point_data.HasArray(field_name):
                    field_array = point_data.GetArray(field_name)
                    print(f"Found '{field_name}' in point data for block '{block_name}'")
                else:
                    # Check cell data
                    cell_data = block_data.GetCellData()
                    if cell_data.HasArray(field_name):
                        field_array = cell_data.GetArray(field_name)
                        print(f"Found '{field_name}' in cell data for block '{block_name}'")
                
                if field_array is None:
                    print(f"Warning: Field '{field_name}' not found in block '{block_name}'")
                    continue
                
                # Convert VTK array to numpy array
                if hasattr(field_array, 'GetNumberOfTuples'):
                    field_values = np.array([field_array.GetValue(i) for i in range(field_array.GetNumberOfTuples())])
                else:
                    field_values = np.array(field_array)
                
                # Calculate total for this block
                total_value = np.sum(field_values)
                block_totals[block_name] = total_value
                
            except Exception as e:
                print(f"Error processing block '{block_name}': {e}")
                continue
        
        if not block_totals:
            print("No data found for any blocks")
            return {}
        
        # Calculate percentages if requested
        grand_total = sum(block_totals.values())
        
        if use_percentages:
            # For heat flux (often negative), use absolute values for percentage calculation
            if field_name.lower() in ['heat_flux', 'heat_transfer_rate', 'thermal_flux']:
                # Use absolute values for meaningful percentages
                abs_totals = {block: abs(value) for block, value in block_totals.items()}
                abs_grand_total = sum(abs_totals.values())
                if abs_grand_total > 0:
                    display_values = {block: (abs_value/abs_grand_total)*100 for block, abs_value in abs_totals.items()}
                    y_label = f'{field_name} (% of Total Magnitude)'
                    title_suffix = '(% of Total Magnitude)'
                else:
                    display_values = {block: 0 for block in block_totals.keys()}
                    y_label = f'{field_name} (%)'
                    title_suffix = '(% of Total)'
            else:
                # For positive fields, use regular percentage calculation
                if grand_total > 0:
                    display_values = {block: (value/grand_total)*100 for block, value in block_totals.items()}
                else:
                    display_values = {block: 0 for block in block_totals.keys()}
                y_label = f'{field_name} (%)'
                title_suffix = '(% of Total)'
        else:
            display_values = block_totals
            y_label = field_name
            title_suffix = '(Total Values)'
        
        # Create bar chart
        block_names = list(display_values.keys())
        values = list(display_values.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=block_names,
                y=values,
                marker_color='steelblue',
                text=[f'{val:.2e}' if not use_percentages else f'{val:.1f}%' for val in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title=f'{field_name} Comparison by Block {title_suffix}',
            xaxis_title='Block Name',
            yaxis_title=y_label,
            template='plotly_white',
            showlegend=False,
            height=600,
            margin=dict(t=60, b=60, l=80, r=40)
        )
        
        # Save files
        base_filename = f"block_comparison_{field_name.replace(' ', '_').lower()}"
        
        if save_html:
            html_path = os.path.join(output_dir, f"{base_filename}.html")
            fig.write_html(html_path)
            print(f"HTML saved: {html_path}")
        
        if save_png:
            png_path = os.path.join(output_dir, f"{base_filename}.png")
            try:
                fig.write_image(png_path, width=1200, height=800, scale=2)
                print(f"PNG saved: {png_path}")
            except Exception as e:
                print(f"Could not save PNG: {e}")
                print("Make sure kaleido is installed: pip install kaleido")
        
        # Print summary
        print(f"\n=== Block Comparison Results for {field_name} ===")
        print(f"Display mode: {'Percentages' if use_percentages else 'Raw values'}")
        print(f"Blocks processed: {len(block_totals)}")
        
        if show_totals:
            print(f"\nTotal {field_name} by block:")
            for block_name, total in block_totals.items():
                if use_percentages:
                    percentage = (total/grand_total)*100 if grand_total > 0 else 0
                    print(f"  {block_name}: {total:.6e} ({percentage:.1f}%)")
                else:
                    print(f"  {block_name}: {total:.6e}")
            print(f"Grand total: {grand_total:.6e}")
        
        return block_totals
    
    def save_averages(self, df, filename):
        """Save DataFrame to CSV"""
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    def integrate_field(self, field_name, data_type='cell', block_name=None, block_id=None, weight_field=None):
        """
        Integrate a field over all cells or points in the specified block(s).
        For heat_flux, use face area; for other fields, use volume or area as appropriate.
        Args:
            field_name: Name of the field to integrate (e.g., 'heat_flux')
            data_type: 'cell' or 'point'
            block_name: None (all blocks), str (single block), or list (multiple blocks)
            block_id: Block index (only used if block_name is None)
            weight_field: Name of the weighting field ('face_area_magnitude', 'cell_volume', etc.)
        Returns:
            Total integrated value (float)
        """
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        total = 0.0
        print(f"\nIntegrating field '{field_name}' over {len(blocks_to_process)} blocks...")
        for block_display, block_idx in blocks_to_process:
            block = self.data[block_idx]
            block_total = 0.0
            if data_type == 'cell':
                data_arrays = block.GetCellData()
                n_elements = block.GetNumberOfCells()
                field_array = data_arrays.GetArray(field_name)
                if field_array is None:
                    print(f"Field '{field_name}' not found in cell data for block '{block_display}'")
                    continue
                print(f"  Block '{block_display}': {n_elements} cells")
                if weight_field:
                    weight_array = data_arrays.GetArray(weight_field)
                    if weight_array is not None:
                        print(f"    Using weight field '{weight_field}' from data arrays")
                        for i in range(n_elements):
                            val = field_array.GetValue(i)
                            weight = weight_array.GetValue(i)
                            block_total += val * weight
                    elif weight_field == 'face_area_magnitude':
                        # Compute face area from mesh geometry for each cell
                        print(f"    '{weight_field}' not found in cell data for block '{block_display}', computing from geometry...")
                        total_computed_area = 0.0
                        
                        # Check if these are surface cells or volume cells
                        sample_cell = block.GetCell(0) if n_elements > 0 else None
                        if sample_cell:
                            cell_type = sample_cell.GetCellType()
                            print(f"    Cell type: {cell_type} ({self._get_cell_type_name(cell_type)})")
                            
                            if cell_type in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD, vtk.VTK_POLYGON]:
                                # Surface cells - compute area directly
                                print(f"    Processing surface cells...")
                                for i in range(n_elements):
                                    cell = block.GetCell(i)
                                    area = self._compute_cell_area(cell)
                                    val = field_array.GetValue(i)
                                    block_total += val * area
                                    total_computed_area += area
                            else:
                                # Volume cells - we need to extract boundary faces
                                print(f"    Volume cells detected - extracting boundary surface...")
                                # Extract boundary surface using VTK
                                geometry_filter = vtk.vtkGeometryFilter()
                                geometry_filter.SetInputData(block)
                                geometry_filter.Update()
                                surface = geometry_filter.GetOutput()
                                
                                print(f"    Extracted surface has {surface.GetNumberOfCells()} faces")
                                
                                # Now integrate over surface cells
                                surface_cell_data = surface.GetCellData()
                                surface_field_array = surface_cell_data.GetArray(field_name)
                                
                                if surface_field_array is not None:
                                    for i in range(surface.GetNumberOfCells()):
                                        cell = surface.GetCell(i)
                                        area = self._compute_cell_area(cell)
                                        val = surface_field_array.GetValue(i)
                                        block_total += val * area
                                        total_computed_area += area
                                else:
                                    print(f"    Warning: {field_name} not found on extracted surface, using volume data")
                                    # Fallback: use average area per volume cell
                                    bounds = block.GetBounds()
                                    total_volume = (bounds[1]-bounds[0])*(bounds[3]-bounds[2])*(bounds[5]-bounds[4])
                                    avg_area_per_cell = total_volume / n_elements
                                    
                                    for i in range(n_elements):
                                        val = field_array.GetValue(i)
                                        block_total += val * avg_area_per_cell
                                        total_computed_area += avg_area_per_cell
                        
                        print(f"    Computed total area: {total_computed_area:.6e}")
                    else:
                        print(f"'{weight_field}' not found in cell data for block '{block_display}' (required for integration)")
                        continue
                else:
                    # If no weight_field, just sum the field values
                    print(f"    No weight field specified, summing raw values")
                    for i in range(n_elements):
                        block_total += field_array.GetValue(i)
            else:
                data_arrays = block.GetPointData()
                n_elements = block.GetNumberOfPoints()
                field_array = data_arrays.GetArray(field_name)
                if field_array is None:
                    print(f"Field '{field_name}' not found in point data for block '{block_display}'")
                    continue
                print(f"  Block '{block_display}': {n_elements} points")
                if weight_field:
                    weight_array = data_arrays.GetArray(weight_field)
                    if weight_array is None:
                        print(f"'{weight_field}' not found in point data for block '{block_display}' (required for integration)")
                        continue
                    print(f"    Using weight field '{weight_field}' from data arrays")
                    for i in range(n_elements):
                        val = field_array.GetValue(i)
                        weight = weight_array.GetValue(i)
                        block_total += val * weight
                else:
                    print(f"    No weight field specified, summing raw values")
                    for i in range(n_elements):
                        block_total += field_array.GetValue(i)
            
            print(f"    Block total: {block_total:.6e}")
            total += block_total
        
        print(f"Total integrated value: {total:.6e}")
        return total
    
    def _get_cell_type_name(self, cell_type):
        """Get human-readable name for VTK cell type"""
        cell_type_names = {
            vtk.VTK_TRIANGLE: "Triangle",
            vtk.VTK_QUAD: "Quad", 
            vtk.VTK_POLYGON: "Polygon",
            vtk.VTK_TETRA: "Tetrahedron",
            vtk.VTK_HEXAHEDRON: "Hexahedron",
            vtk.VTK_WEDGE: "Wedge",
            vtk.VTK_PYRAMID: "Pyramid"
        }
        return cell_type_names.get(cell_type, f"Unknown({cell_type})")
    
    def _compute_cell_area(self, cell):
        """Compute area of a VTK cell"""
        cell_type = cell.GetCellType()
        
        if cell_type in [vtk.VTK_TRIANGLE, vtk.VTK_QUAD, vtk.VTK_POLYGON]:
            # Surface cells - use VTK's built-in area calculation
            if cell_type == vtk.VTK_TRIANGLE:
                p0 = cell.GetPoints().GetPoint(0)
                p1 = cell.GetPoints().GetPoint(1) 
                p2 = cell.GetPoints().GetPoint(2)
                return vtk.vtkTriangle.TriangleArea(p0, p1, p2)
            else:
                # For quads and polygons, use shoelace formula
                pts = cell.GetPoints()
                n = pts.GetNumberOfPoints()
                coords = np.array([pts.GetPoint(j) for j in range(n)])
                if n < 3:
                    return 0.0
                # Project to best-fit plane and compute area
                # For simplicity, use cross product for triangulated area
                if n == 4:  # Quad
                    # Split quad into two triangles
                    p0, p1, p2, p3 = coords
                    area1 = 0.5 * np.linalg.norm(np.cross(p1-p0, p2-p0))
                    area2 = 0.5 * np.linalg.norm(np.cross(p2-p0, p3-p0))
                    return area1 + area2
                else:
                    # General polygon - fan triangulation from first vertex
                    total_area = 0.0
                    for i in range(1, n-1):
                        p0, p1, p2 = coords[0], coords[i], coords[i+1]
                        area = 0.5 * np.linalg.norm(np.cross(p1-p0, p2-p0))
                        total_area += area
                    return total_area
        else:
            # For volume cells, return 0 (shouldn't be used for surface integration)
            return 0.0
    
    def save_integrated_fields_to_csv(self, variable_list, weight_field, data_type='cell', block_name=None, block_id=None, csv_path='integrated_fields.csv'):
        """
        Integrate each variable over each block and save results to a CSV file.
        CSV columns: variable, block1, block2, ..., total
        Args:
            variable_list: list of variable names to integrate
            weight_field: field to use for integration (e.g., 'face_area_magnitude', 'cell_volume')
            data_type: 'cell' or 'point'
            block_name: None (all blocks), str (single block), or list (multiple blocks)
            block_id: Block index (only used if block_name is None)
            csv_path: output CSV file path
        """
        import pandas as pd
        blocks_to_process = self._resolve_blocks(block_name, block_id)
        block_names = [name for name, _ in blocks_to_process]
        results = []
        for var in variable_list:
            values = []
            total = 0.0
            for block_display, block_idx in blocks_to_process:
                val = self.integrate_field(var, data_type=data_type, block_name=block_display, block_id=block_idx, weight_field=weight_field)
                values.append(val)
                total += val
            results.append([var] + values + [total])
        columns = ['variable'] + block_names + ['total']
        df = pd.DataFrame(results, columns=columns)
        df.to_csv(csv_path, index=False)
        print(f"Integrated field values saved to {csv_path}")
        
    def save_variable_stats_to_csv(self, csv_path='variable_stats.csv', block_name=None, block_id=None):
        """
        Compute full summary stats (min, mean, max, median, std, var, skew, kurt) for all cell and point variables and save to CSV.
        Args:
            csv_path: output CSV file path
            block_name: None (all blocks), str (single block), or list (multiple blocks)
            block_id: Block index (only used if block_name is None)
        """
        import pandas as pd
        from scipy.stats import skew, kurtosis
        if block_name == 'ALL_BLOCKS':
            blocks_to_process = [(b, i) for i, b in enumerate(self.block_names)]
        else:
            blocks_to_process = self._resolve_blocks(block_name, block_id)
        results = []
        for block_display, block_idx in blocks_to_process:
            block = self.data[block_idx]
            # Cell data
            cell_data = block.GetCellData()
            for i in range(cell_data.GetNumberOfArrays()):
                var = cell_data.GetArrayName(i)
                arr = cell_data.GetArray(var)
                if arr is not None and arr.GetNumberOfTuples() > 0:
                    vals = np.array([arr.GetValue(j) for j in range(arr.GetNumberOfTuples())])
                    stats = [
                        np.min(vals),
                        np.mean(vals),
                        np.max(vals),
                        np.median(vals),
                        np.std(vals),
                        np.var(vals),
                        skew(vals),
                        kurtosis(vals)
                    ]
                    results.append([var, 'cell', block_display] + stats)
            # Point data
            point_data = block.GetPointData()
            for i in range(point_data.GetNumberOfArrays()):
                var = point_data.GetArrayName(i)
                arr = point_data.GetArray(var)
                if arr is not None and arr.GetNumberOfTuples() > 0:
                    vals = np.array([arr.GetValue(j) for j in range(arr.GetNumberOfTuples())])
                    stats = [
                        np.min(vals),
                        np.mean(vals),
                        np.max(vals),
                        np.median(vals),
                        np.std(vals),
                        np.var(vals),
                        skew(vals),
                        kurtosis(vals)
                    ]
                    results.append([var, 'point', block_display] + stats)
        columns = ['variable', 'data_type', 'block_name', 'min', 'mean', 'max', 'median', 'std', 'var', 'skew', 'kurt']
        df = pd.DataFrame(results, columns=columns)

        # Add summary row for all blocks for each variable/data_type
        summary_rows = []
        for (var, data_type) in df[['variable', 'data_type']].drop_duplicates().values:
            vals = df[(df['variable'] == var) & (df['data_type'] == data_type)]
            all_values = []
            for idx, row in vals.iterrows():
                # Recompute stats from all values in all blocks
                block = row['block_name']
                # Find block index
                block_idx = None
                for i, b in enumerate(self.block_names):
                    if b == block:
                        block_idx = i
                        break
                if block_idx is not None:
                    if data_type == 'cell':
                        arr = self.data[block_idx].GetCellData().GetArray(var)
                    else:
                        arr = self.data[block_idx].GetPointData().GetArray(var)
                    if arr is not None:
                        all_values.extend([arr.GetValue(j) for j in range(arr.GetNumberOfTuples())])
            if all_values:
                all_values = np.array(all_values)
                stats = [
                    np.min(all_values),
                    np.mean(all_values),
                    np.max(all_values),
                    np.median(all_values),
                    np.std(all_values),
                    np.var(all_values),
                    skew(all_values),
                    kurtosis(all_values)
                ]
                summary_rows.append([var, data_type, 'ALL_BLOCKS'] + stats)
        if summary_rows:
            df = pd.concat([df, pd.DataFrame(summary_rows, columns=columns)], ignore_index=True)

        df.to_csv(csv_path, index=False)
        print(f"Full variable summary stats saved to {csv_path}")

class CFDComparisonProcessor:
    def __init__(self, file_paths, labels=None):
        """
        file_paths: list of dataset file paths
        labels: optional list of labels for each dataset
        """
        self.processors = [CFDPostProcessor(fp) for fp in file_paths]
        self.labels = labels if labels is not None else [f'Dataset {i}' for i in range(len(file_paths))]

    def compare_bar(self, field, agg_func='mean', save_path=None, data_type='cell', block_name=None, combined=False):
        """
        Bar chart comparing aggregated field values across datasets.
        Similar to CFDPostProcessor.plot_bar but for multiple datasets.
        """
        plt.figure(figsize=(10, 6))
        values = []
        labels = []
        
        for i, (proc, dataset_label) in enumerate(zip(self.processors, self.labels)):
            # Determine which blocks to use
            if block_name is None:
                blocks_to_use = proc.data
            elif isinstance(block_name, str):
                try:
                    idx = proc.get_block_index(block_name)
                    blocks_to_use = [proc.data[idx]]
                except Exception as e:
                    print(f"Warning: Block '{block_name}' not found in dataset '{dataset_label}': {e}")
                    blocks_to_use = []
            elif isinstance(block_name, list):
                blocks_to_use = []
                for name in block_name:
                    try:
                        idx = proc.get_block_index(name)
                        blocks_to_use.append(proc.data[idx])
                    except Exception as e:
                        print(f"Warning: Block '{name}' not found in dataset '{dataset_label}': {e}")
            else:
                print(f"Warning: Invalid block_name type: {type(block_name)}")
                blocks_to_use = []

            # Aggregate field values across selected blocks
            all_data = []
            for block in blocks_to_use:
                data_dict = self._get_data_dict(block, data_type)
                if field in data_dict:
                    all_data.extend(data_dict[field])
            if all_data:
                data = np.array(all_data)
                if agg_func == 'mean':
                    val = np.mean(data)
                elif agg_func == 'sum':
                    val = np.sum(data)
                elif agg_func == 'max':
                    val = np.max(data)
                elif agg_func == 'min':
                    val = np.min(data)
                else:
                    val = np.mean(data)
                values.append(val)
                labels.append(dataset_label)
            else:
                print(f"Warning: Field '{field}' not found in selected blocks for dataset '{dataset_label}'")
        
        if values:
            plt.bar(labels, values, alpha=0.7)
            plt.ylabel(field)
            plt.title(f'Comparison: {field} ({agg_func})')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            fname = save_path or f'compare_bar_{field}_{agg_func}.png'
            plt.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved comparison bar chart: {fname}")
        else:
            print(f"No valid data found for field '{field}' in any dataset")
            plt.close()

    def compare_line(self, field, x_axis, mode='overlay', combine_func='mean', save_path=None, data_type='cell', block_name=None, num_slices=100):
        """
        Line plot comparison across datasets using averaged/binned data.
        Similar to CFDPostProcessor.plot_line but for multiple datasets.
        """
        plt.figure(figsize=(12, 8))
        
        plot_created = False
        
        for i, (proc, dataset_label) in enumerate(zip(self.processors, self.labels)):
            try:
                # Use slice_and_average to get binned data along the x_axis
                if x_axis in ['x', 'y', 'z']:
                    # Get averaged data sliced along the coordinate axis
                    df = proc.slice_and_average(axis=x_axis, num_slices=num_slices, data_type=data_type, 
                                              block_name=block_name)
                    
                    if not df.empty and field in df.columns:
                        x_data = df[x_axis].values
                        y_data = df[field].values
                        
                        if mode == 'overlay':
                            plt.plot(x_data, y_data, label=dataset_label, linewidth=2, marker='o', markersize=3, alpha=0.8)
                            plot_created = True
                        elif mode == 'combined':
                            # Data is already binned/averaged by slice_and_average
                            plt.plot(x_data, y_data, 
                                    label=f'{dataset_label} (averaged)', linewidth=2, marker='o', markersize=3)
                            plot_created = True
                    else:
                        print(f"Warning: Field '{field}' not found in averaged data for dataset '{dataset_label}'")
                        
                else:
                    # For non-coordinate x_axis, we need to handle differently
                    # This is more complex as we'd need to slice along one axis and plot another field
                    print(f"Warning: Non-coordinate x_axis '{x_axis}' not yet supported for comparison plots")
                    
            except Exception as e:
                print(f"Warning: Cannot plot '{field}' vs '{x_axis}' for dataset '{dataset_label}' - {e}")
        
        if plot_created:
            plt.xlabel(x_axis)
            plt.ylabel(field)
            plt.title(f'Comparison: {field} vs {x_axis} (Averaged Data)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            fname = save_path or f'compare_line_{field}_vs_{x_axis}.png'
            plt.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved comparison line plot: {fname}")
        else:
            print(f"No valid data found to create line plot for '{field}' vs '{x_axis}'")
            plt.close()
        
        if plot_created:
            plt.xlabel(x_axis)
            plt.ylabel(field)
            plt.title(f'Comparison: {field} vs {x_axis}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            fname = save_path or f'compare_line_{field}_vs_{x_axis}.png'
            plt.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved comparison line plot: {fname}")
        else:
            print(f"No valid data found to create line plot for '{field}' vs '{x_axis}'")
            plt.close()

    def _get_data_dict(self, mesh, data_type):
        """Helper method to get the appropriate data dictionary"""
        if data_type == 'cell':
            return self._get_cell_data_dict(mesh)
        else:
            return self._get_point_data_dict(mesh)
    
    def _get_cell_data_dict(self, mesh):
        """Get cell data as dictionary"""
        cell_data = {}
        if hasattr(mesh, 'GetCellData'):
            cd = mesh.GetCellData()
            for i in range(cd.GetNumberOfArrays()):
                array = cd.GetArray(i)
                name = cd.GetArrayName(i)
                if array and name:
                    # Convert VTK array to numpy
                    cell_data[name] = numpy_support.vtk_to_numpy(array)
        return cell_data
    
    def _get_point_data_dict(self, mesh):
        """Get point data as dictionary"""
        point_data = {}
        if hasattr(mesh, 'GetPointData'):
            pd = mesh.GetPointData()
            for i in range(pd.GetNumberOfArrays()):
                array = pd.GetArray(i)
                name = pd.GetArrayName(i)
                if array and name:
                    # Convert VTK array to numpy
                    point_data[name] = numpy_support.vtk_to_numpy(array)
        return point_data
    
    def _get_points_array(self, mesh):
        """Get points coordinates as numpy array"""
        if hasattr(mesh, 'GetPoints'):
            points_vtk = mesh.GetPoints().GetData()
            return numpy_support.vtk_to_numpy(points_vtk)
        return None

    def compare_scatter(self, field_x, field_y, save_path=None, data_type='cell', block_name=None):
        """
        Scatter plot comparison across datasets.
        Similar to CFDPostProcessor.plot_scatter but for multiple datasets.
        """
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 8))
        
        def get_coordinates_for_data_type(mesh, data_type):
            """Get coordinates that match the data type (cell centers for cell data, points for point data)"""
            if data_type == 'cell':
                # Get cell centers for coordinates
                centers = vtk.vtkCellCenters()
                centers.SetInputData(mesh)
                centers.Update()
                center_points = centers.GetOutput().GetPoints()
                n_elements = mesh.GetNumberOfCells()
                coords = np.zeros((n_elements, 3))
                for i in range(n_elements):
                    coords[i] = center_points.GetPoint(i)
                return coords
            else:
                # Get point coordinates
                n_elements = mesh.GetNumberOfPoints()
                points = mesh.GetPoints()
                coords = np.zeros((n_elements, 3))
                for i in range(n_elements):
                    coords[i] = points.GetPoint(i)
                return coords
        
        def get_axis_data(mesh, axis, data_type):
            """Get axis data - either coordinates or field data"""
            if axis in ['x', 'y', 'z']:
                axis_idx = {'x': 0, 'y': 1, 'z': 2}[axis]
                coords = get_coordinates_for_data_type(mesh, data_type)
                return coords[:, axis_idx]
            else:
                data_dict = self._get_data_dict(mesh, data_type)
                return data_dict.get(axis, None)
        
        plot_created = False
        
        # Use a more distinct colormap for better visibility
        # Create a list of distinct colors for better contrast
        distinct_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                          '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']
        
        # If we have more datasets than distinct colors, fall back to a colormap
        if len(self.processors) <= len(distinct_colors):
            colors = distinct_colors[:len(self.processors)]
        else:
            # Use Set3 colormap for more datasets - it has better contrast than tab10
            colors = plt.cm.Set3(np.linspace(0, 1, len(self.processors)))
        
        for i, (proc, dataset_label) in enumerate(zip(self.processors, self.labels)):
            # Get data from all blocks if block_name is None, otherwise specific block
            if block_name:
                block_idx = proc.get_block_index(block_name)
                meshes = [proc.data[block_idx]]
            else:
                # Use all blocks
                meshes = proc.data
            
            # Collect data from all relevant meshes
            all_x_data = []
            all_y_data = []
            
            for mesh in meshes:
                x_data = get_axis_data(mesh, field_x, data_type)
                y_data = get_axis_data(mesh, field_y, data_type)
                
                if x_data is not None and y_data is not None and len(x_data) == len(y_data):
                    all_x_data.append(x_data)
                    all_y_data.append(y_data)
            
            # Combine all data
            if all_x_data and all_y_data:
                combined_x = np.concatenate(all_x_data)
                combined_y = np.concatenate(all_y_data)
                
                plt.scatter(combined_x, combined_y, label=dataset_label, alpha=0.7, 
                           color=colors[i], s=25, edgecolors='white', linewidth=0.8)
                plot_created = True
            else:
                print(f"Warning: Cannot create scatter plot for dataset '{dataset_label}' - data missing or size mismatch")
        
        if plot_created:
            plt.xlabel(field_x)
            plt.ylabel(field_y)
            plt.title(f'Comparison Scatter: {field_y} vs {field_x}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            fname = save_path or f'compare_scatter_{field_y}_vs_{field_x}.png'
            plt.savefig(fname, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved comparison scatter plot: {fname}")
        else:
            print(f"No valid data found to create scatter plot for '{field_y}' vs '{field_x}'")
            plt.close()

    def get_processor(self, idx):
        """
        Access individual CFDPostProcessor by index.
        """
        return self.processors[idx]
    
    def compare_variable_stats_csvs(self, csv_paths, processors=None, labels=None, output_dir='comparison_results', plot_stats=['mean', 'max', 'min'], block_name='ALL_BLOCKS', plot_types=['box', 'violin', 'hist']):
        """
        Compare variable stats CSVs for multiple datasets, compute useful statistics, and generate plots.
        Args:
            csv_paths: list of CSV file paths (one per dataset)
            labels: list of labels for each dataset (optional)
            output_dir: directory to save plots and comparison CSV
            plot_stats: list of stats to plot (e.g., ['mean', 'max', 'min'])
            block_name: which block to compare (default 'ALL_BLOCKS')
        Returns:
            comparison DataFrame
        """
        import pandas as pd
        import matplotlib.pyplot as plt
        import os
        os.makedirs(output_dir, exist_ok=True)
        dfs = [pd.read_csv(path) for path in csv_paths]
        if labels is None:
            labels = [f'Dataset_{i+1}' for i in range(len(dfs))]
        # Filter for specified block_name
        dfs = [df[df['block_name'] == block_name].copy() for df in dfs]
        # Merge all DataFrames on variable and data_type using outer join
        merged = dfs[0][['variable', 'data_type']].copy()
        for i, (df, label) in enumerate(zip(dfs, labels)):
            df_sub = df[['variable', 'data_type'] + plot_stats].copy()
            # Rename stat columns to include label
            df_sub = df_sub.rename(columns={stat: f'{label}_{stat}' for stat in plot_stats})
            if i == 0:
                merged = df_sub
            else:
                merged = pd.merge(merged, df_sub, on=['variable', 'data_type'], how='outer')
        # Compute differences and percent changes for each stat
        for stat in plot_stats:
            base = f'{labels[0]}_{stat}'
            for label in labels[1:]:
                comp = f'{label}_{stat}'
                merged[f'diff_{comp}_vs_{base}'] = merged[comp] - merged[base]
                merged[f'percent_change_{comp}_vs_{base}'] = 100 * (merged[comp] - merged[base]) / merged[base]
        # Save comparison CSV
        comp_csv = os.path.join(output_dir, 'variable_stats_comparison.csv')
        merged.to_csv(comp_csv, index=False)
        print(f"Variable stats comparison saved to {comp_csv}")

        # Generate bar plots for each stat
        for stat in plot_stats:
            plt.figure(figsize=(10, 6))
            for label in labels:
                plt.bar(merged['variable'] + '_' + merged['data_type'], merged[f'{label}_{stat}'], alpha=0.7, label=label)
            plt.xticks(rotation=90)
            plt.ylabel(stat)
            plt.title(f'Comparison of {stat} for {block_name}')
            plt.legend()
            plt.tight_layout()
            plot_path = os.path.join(output_dir, f'compare_{stat}_{block_name}.png')
            plt.savefig(plot_path, dpi=300)
            plt.close()
            print(f"Saved plot: {plot_path}")

        # Generate true box/violin/histogram/KDE/CDF plots for each variable/data_type using raw arrays
        if processors is not None:
            from scipy.stats import gaussian_kde
            for var, data_type in merged[['variable', 'data_type']].drop_duplicates().values:
                raw_data = []
                for proc in processors:
                    # Aggregate all values for this variable/data_type/block_name
                    vals = []
                    blocks_to_use = [i for i, b in enumerate(proc.block_names) if block_name == 'ALL_BLOCKS' or b == block_name]
                    for block_idx in blocks_to_use:
                        if data_type == 'cell':
                            arr = proc.data[block_idx].GetCellData().GetArray(var)
                        else:
                            arr = proc.data[block_idx].GetPointData().GetArray(var)
                        if arr is not None:
                            vals.extend([arr.GetValue(j) for j in range(arr.GetNumberOfTuples())])
                    raw_data.append(np.array(vals))
                # Filter out empty arrays and their labels
                filtered = [(arr, label) for arr, label in zip(raw_data, labels) if arr is not None and len(arr) > 0]
                if filtered:
                    filtered_data, filtered_labels = zip(*filtered)
                else:
                    filtered_data, filtered_labels = [], []
                # Box plot
                if 'box' in plot_types and filtered_data:
                    plt.figure(figsize=(10, 6))
                    plt.boxplot(filtered_data, labels=filtered_labels, vert=True, patch_artist=True)
                    plt.title(f'Box Plot: {var} ({data_type}, {block_name})')
                    plt.ylabel(var)
                    plt.tight_layout()
                    plot_path = os.path.join(output_dir, f'boxplot_{var}_{data_type}_{block_name}.png')
                    plt.savefig(plot_path, dpi=300)
                    plt.close()
                    print(f"Saved box plot: {plot_path}")
                # Violin plot
                if 'violin' in plot_types and filtered_data:
                    plt.figure(figsize=(10, 6))
                    plt.violinplot(filtered_data, showmeans=True)
                    plt.xticks(np.arange(1, len(filtered_labels)+1), filtered_labels, rotation=0)
                    plt.title(f'Violin Plot: {var} ({data_type}, {block_name})')
                    plt.ylabel(var)
                    plt.tight_layout()
                    plot_path = os.path.join(output_dir, f'violinplot_{var}_{data_type}_{block_name}.png')
                    plt.savefig(plot_path, dpi=300)
                    plt.close()
                    print(f"Saved violin plot: {plot_path}")
                # Histogram plot
                if 'hist' in plot_types and filtered_data:
                    plt.figure(figsize=(10, 6))
                    for arr, label in zip(filtered_data, filtered_labels):
                        plt.hist(arr, bins=40, alpha=0.6, label=label)
                    plt.title(f'Histogram: {var} ({data_type}, {block_name})')
                    plt.xlabel(var)
                    plt.ylabel('Count')
                    plt.legend()
                    plt.tight_layout()
                    plot_path = os.path.join(output_dir, f'histogram_{var}_{data_type}_{block_name}.png')
                    plt.savefig(plot_path, dpi=300)
                    plt.close()
                    print(f"Saved histogram plot: {plot_path}")
                # KDE plot
                if 'kde' in plot_types and filtered_data:
                    plt.figure(figsize=(10, 6))
                    for arr, label in zip(filtered_data, filtered_labels):
                        if len(arr) > 1 and len(np.unique(arr)) > 1:
                            try:
                                kde = gaussian_kde(arr)
                                x_grid = np.linspace(np.min(arr), np.max(arr), 200)
                                plt.plot(x_grid, kde(x_grid), label=label)
                            except Exception as e:
                                print(f"Skipping KDE for {label} ({var}): {e}")
                        else:
                            print(f"Skipping KDE for {label} ({var}): not enough unique values.")
                    plt.title(f'KDE Plot: {var} ({data_type}, {block_name})')
                    plt.xlabel(var)
                    plt.ylabel('Density')
                    plt.legend()
                    plt.tight_layout()
                    plot_path = os.path.join(output_dir, f'kdeplot_{var}_{data_type}_{block_name}.png')
                    plt.savefig(plot_path, dpi=300)
                    plt.close()
                    print(f"Saved KDE plot: {plot_path}")
                # CDF plot
                if 'cdf' in plot_types and filtered_data:
                    plt.figure(figsize=(10, 6))
                    for arr, label in zip(filtered_data, filtered_labels):
                        if len(arr) > 0:
                            sorted_arr = np.sort(arr)
                            cdf = np.arange(1, len(sorted_arr)+1) / len(sorted_arr)
                            plt.plot(sorted_arr, cdf, label=label)
                    plt.title(f'CDF Plot: {var} ({data_type}, {block_name})')
                    plt.xlabel(var)
                    plt.ylabel('Cumulative Probability')
                    plt.legend()
                    plt.tight_layout()
                    plot_path = os.path.join(output_dir, f'cdfplot_{var}_{data_type}_{block_name}.png')
                    plt.savefig(plot_path, dpi=300)
                    plt.close()
                    print(f"Saved CDF plot: {plot_path}")
        return merged
    
    def compare_integrated_csvs(self, csv_paths, labels=None, reference_label=None, output_csv=None):
        """
        Compare integrated variable CSVs for multiple datasets and show percent improvement from a reference.
        Args:
            csv_paths: list of CSV file paths (one per dataset)
            labels: list of labels for each dataset (optional)
            reference_label: label of the reference dataset for percent improvement (if None, uses first)
            output_csv: path to save the comparison CSV (optional)
        Returns:
            comparison DataFrame
        """
        import pandas as pd
        # Load all CSVs
        dfs = [pd.read_csv(path) for path in csv_paths]
        if labels is None:
            labels = [f'Dataset_{i+1}' for i in range(len(dfs))]
        # Merge on 'variable'
        merged = dfs[0][['variable']].copy()
        for df, label in zip(dfs, labels):
            merged[label] = df['total']
        # Compute percent improvement
        ref_label = reference_label if reference_label else labels[0]
        for label in labels:
            if label != ref_label:
                merged[f'percent_improvement_vs_{ref_label}_{label}'] = 100 * (merged[label] - merged[ref_label]) / merged[ref_label]
        if output_csv:
            merged.to_csv(output_csv, index=False)
            print(f"Comparison saved to {output_csv}")
        return merged

# Example usage and test
if __name__ == "__main__":
    # This is for testing without the actual file
    print("CFD Post-Processor with VTK backend (no PyVista)")
    print("For testing, please run your main script with this class")