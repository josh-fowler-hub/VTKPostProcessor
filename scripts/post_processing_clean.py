from PostProcessing.VTKPostProcessor import CFDPostProcessor
import os

# Create an instance of the post-processor
processor = CFDPostProcessor('geom_vol.vtm')

# Get available variables and blocks
print("\n=== Dataset Information ===")
block_names = processor.get_block_names()
print(f"Available blocks: {block_names}")

# Create output directories
os.makedirs('2D_contour_plots', exist_ok=True)
os.makedirs('line_plots', exist_ok=True)
os.makedirs('bar_charts', exist_ok=True)
os.makedirs('3d_plots', exist_ok=True)
os.makedirs('averaged_data', exist_ok=True)
os.makedirs(name='surface_contours', exist_ok=True)
os.makedirs('powerpoint_images', exist_ok=True)  # For PNG exports

# =============================================================================
# BLOCK 1: SLICE AND AVERAGE DATA GENERATION
# Comment out this entire block if averaged data already exists
# =============================================================================
print("\n=== BLOCK 1: Slice and Average for All Blocks ===")
all_dataframes = {}

for block_name in block_names:
    print(f"\nProcessing slice and average for block: {block_name}")
    try:
        df = processor.slice_and_average(axis='y', num_slices=100, data_type='cell', block_name=block_name)
        if not df.empty:
            csv_path = f'averaged_data/{block_name}_avg.csv'
            processor.save_averages(df, csv_path)
            all_dataframes[block_name] = df
            print(f"  Saved: {csv_path} ({df.shape[0]} rows, {df.shape[1]} columns)")
        else:
            print(f"  No data found for {block_name}")
    except Exception as e:
        print(f"  Failed to process {block_name}: {e}")

# # =============================================================================
# # BLOCK 2: LOAD EXISTING AVERAGED DATA (Alternative to Block 1)
# # Uncomment this block if you want to load pre-existing averaged data
# # =============================================================================
# print("\n=== BLOCK 2: Loading Existing Averaged Data ===")
# import pandas as pd
# all_dataframes = {}

# for block_name in block_names:
#     csv_path = f'averaged_data/{block_name}_avg.csv'
#     if os.path.exists(csv_path):
#         try:
#             df = pd.read_csv(csv_path)
#             all_dataframes[block_name] = df
#             print(f"  Loaded: {csv_path} ({df.shape[0]} rows, {df.shape[1]} columns)")
#         except Exception as e:
#             print(f"  Failed to load {csv_path}: {e}")
#     else:
#         print(f"  File not found: {csv_path}")

# =============================================================================
# BLOCK 3: VISUALIZATION GENERATION - SETUP
# =============================================================================
print("\n=== BLOCK 3: Visualization Setup ===")

# Track all variables across all blocks for overlay plots
all_variables = set()
block_variables = {}

# Collect variable information for all blocks
for block_name in block_names:
    print(f"\n--- Analyzing Block: {block_name} ---")
    
    try:
        # Get variables for this block
        variables = processor.get_variable_names(block_name=block_name, verbose=False)
        cell_vars = variables['cell_data']
        point_vars = variables['point_data']
        
        block_variables[block_name] = {
            'cell_data': cell_vars,
            'point_data': point_vars
        }
        
        # Add to global variable set
        all_variables.update(cell_vars)
        
        print(f"  Cell variables: {cell_vars}")
        print(f"  Point variables: {point_vars}")
        
    except Exception as e:
        print(f"  Failed to analyze {block_name}: {e}")

print(f"\nAll variables found: {sorted(all_variables)}")



# =============================================================================
# BLOCK 4: 2D CONTOUR PLOTS (MATPLOTLIB)
# Comment out this entire block to skip 2D contour generation
# =============================================================================
print(f"\n=== BLOCK 4: Creating 2D Contour Plots (Matplotlib) ===")
for block_name in block_names:
    if block_name in block_variables:
        cell_vars = block_variables[block_name]['cell_data']
        print(f"\nCreating contour plots for {block_name}...")
        
        for var_name in cell_vars:
            try:
                contour_path = f'2D_contour_plots/contour_{var_name}_{block_name}.png'
                processor.plot_contour_matplotlib(
                    field_name=var_name,
                    block_name=block_name,
                    data_type='cell',
                    n_contours=15,
                    save_path=contour_path
                )
                print(f"  ✓ Contour: {contour_path}")
                
            except Exception as e:
                print(f"  ✗ Failed contour {var_name}: {e}")

# =============================================================================
# BLOCK 5: AVERAGED LINE PLOTS (FROM SLICE DATA)
# Comment out this entire block to skip averaged line plot generation
# =============================================================================
print(f"\n=== BLOCK 5: Creating Averaged Line Plots ===")
for block_name in block_names:
    if block_name in all_dataframes:
        print(f"\nCreating averaged line plot for {block_name}...")
        try:
            line_path = f'line_plots/averaged_lines_{block_name}.png'
            processor.plot_averaged_lines(
                dataframe=all_dataframes[block_name],
                coordinate='y',
                save_path=line_path,
                block_name=block_name
            )
            print(f"  ✓ Averaged line plot: {line_path}")
        except Exception as e:
            print(f"  ✗ Failed averaged line plot for {block_name}: {e}")
    else:
        print(f"  No averaged data for {block_name}")

# =============================================================================
# BLOCK 6: 3D SURFACE PLOTS (PLOTLY)
# Comment out this entire block to skip 3D surface generation
# =============================================================================
print(f"\n=== BLOCK 6: Creating 3D Surface Plots ===")
for block_name in block_names:
    if block_name in block_variables:
        cell_vars = block_variables[block_name]['cell_data']
        if cell_vars:
            print(f"\nCreating 3D surface plot for {block_name}...")
            try:
                surface_path = f'3d_plots/surface_{cell_vars[0]}_{block_name}.html'
                processor.plot_contour_plotly_surface(
                    field_name=cell_vars[0],
                    block_name=block_name,
                    data_type='cell',
                    save_path=surface_path
                )
                print(f"  ✓ 3D surface: {surface_path}")
            except Exception as e:
                print(f"  ✗ 3D surface failed for {block_name}: {e}")

# =============================================================================
# BLOCK 7: SURFACE CONTOUR PLOTS (PLOTLY 2D PROJECTIONS)
# Comment out this entire block to skip surface contour generation
# =============================================================================
print(f"\n=== BLOCK 7: Creating Surface Contour Plots ===")
for block_name in block_names:
    if block_name in block_variables:
        cell_vars = block_variables[block_name]['cell_data']
        if cell_vars:
            print(f"\nCreating surface contours for {block_name}...")
            
            # Create surface contours for each projection
            for projection in ['x', 'y', 'z']:
                try:
                    contour_path = f'surface_contours/surface_contour_{cell_vars[0]}_{projection}proj_{block_name}.html'
                    processor.plot_surface_contours_plotly(
                        field_name=cell_vars[0],
                        block_name=block_name,
                        data_type='cell',
                        projection_axis=projection,
                        save_path=contour_path
                    )
                    print(f"  ✓ Surface contour ({projection}-proj): {contour_path}")
                except Exception as e:
                    print(f"  ✗ Surface contour ({projection}-proj) failed: {e}")

# =============================================================================
# BLOCK 8: GEOMETRY SURFACE CONTOUR PLOTS (PLOTLY 3D MESH) - ALL CAMERA VIEWS
# Comment out this entire block to skip geometry surface contour generation
# =============================================================================
print(f"\n=== BLOCK 8: Creating Combined Geometry Surface Contour Plots - All Camera Views ===")
print(f"Variables to process: {sorted(all_variables)}")

# Define all available camera views
camera_views = {
    'isometric': 'Standard isometric view (best for presentations)',
    'front': 'Front view (Y-axis direction)',
    'side': 'Side view (X-axis direction)', 
    'top': 'Top-down view (Z-axis direction)',
    'back': 'Back view',
    'bottom': 'Bottom-up view',
    'perspective': 'Default perspective view',
    'close_isometric': 'Closer isometric view',
    'far_isometric': 'Farther isometric view'
}

print(f"Camera views to generate: {list(camera_views.keys())}")

# Create subdirectories for different camera views
import shutil
for view_name in camera_views.keys():
    os.makedirs(f'powerpoint_images/{view_name}_views', exist_ok=True)
    os.makedirs(f'surface_contours/{view_name}_views', exist_ok=True)

# Create plots for each variable with all camera views
for var_name in sorted(all_variables):
    print(f"\n{'='*60}")
    print(f"Processing variable: '{var_name}'")
    print(f"{'='*60}")
    
    # Check which blocks have this variable
    blocks_with_variable = []
    for block_name in block_names:
        if block_name in block_variables:
            cell_vars = block_variables[block_name]['cell_data']
            if var_name in cell_vars:
                blocks_with_variable.append(block_name)
    
    if blocks_with_variable:
        print(f"Found '{var_name}' in blocks: {blocks_with_variable}")
        
        # Generate plots for each camera view
        successful_views = []
        failed_views = []
        
        for view_name, view_description in camera_views.items():
            print(f"\n  Creating {view_name} view...")
            print(f"    Description: {view_description}")
            
            try:
                # Create file paths for this view
                html_path = f'surface_contours/{view_name}_views/geometry_surface_contour_combined_{var_name}_{view_name}_view.html'
                
                result = processor.plot_geometry_surface_contours_combined(
                    field_name=var_name,
                    block_name=blocks_with_variable,  # Pass list of blocks that have this variable
                    data_type='cell',
                    save_path=html_path,
                    camera_view=view_name
                )
                
                # Handle the new return format (dict with 'html' and 'png' keys)
                if isinstance(result, dict):
                    print(f"    ✓ HTML file: {result['html']}")
                    if result['png']:
                        # Copy PNG to organized PowerPoint directory
                        png_filename = os.path.basename(result['png'])
                        powerpoint_png = f'powerpoint_images/{view_name}_views/{png_filename}'
                        shutil.copy2(result['png'], powerpoint_png)
                        print(f"    ✓ PowerPoint PNG: {powerpoint_png}")
                        successful_views.append(view_name)
                    else:
                        print(f"    ⚠ PNG export failed for {view_name} view")
                        failed_views.append(view_name)
                else:
                    # Handle old return format (just the file path)
                    print(f"    ✓ File created: {result}")
                    successful_views.append(view_name)
                    
            except Exception as e:
                print(f"    ✗ Failed to create {view_name} view: {e}")
                failed_views.append(view_name)
        
        # Summary for this variable
        print(f"\n  Summary for '{var_name}':")
        print(f"    ✓ Successful views: {len(successful_views)}/{len(camera_views)} - {successful_views}")
        if failed_views:
            print(f"    ✗ Failed views: {failed_views}")
        print(f"    📊 Includes {len(blocks_with_variable)} blocks")
        
    else:
        print(f"  Skipping '{var_name}' - not found in any blocks")

# =============================================================================
# BLOCK 9: OVERLAY PLOTS FROM AVERAGED DATA (Single Variable, All Blocks)
# Comment out this entire block to skip overlay plot generation
# =============================================================================
print(f"\n=== BLOCK 9: Creating Overlay Plots - Single Variable Across All Blocks ===")
print(f"Variables found across all blocks: {sorted(all_variables)}")

# For each variable, create an overlay plot showing all blocks
for var_name in sorted(all_variables):
    print(f"\nCreating overlay plot for '{var_name}' across all blocks...")
    
    # Find which blocks have this variable and averaged data
    blocks_with_data = {}
    for block_name, df in all_dataframes.items():
        field_col = f'{var_name}_avg'
        if field_col in df.columns and not df[field_col].isna().all():
            blocks_with_data[block_name] = df
    
    if len(blocks_with_data) >= 1:  # Changed from >1 to >=1 to include single blocks
        try:
            overlay_path = f'line_plots/overlay_{var_name}_all_blocks.png'
            processor.plot_overlay_averaged_lines(
                dataframes_dict=blocks_with_data,
                field_name=var_name,
                coordinate='y',
                save_path=overlay_path
            )
            print(f"  ✓ Overlay plot: {overlay_path}")
            print(f"    Blocks included: {list(blocks_with_data.keys())}")
        except Exception as e:
            print(f"  ✗ Overlay plot failed for {var_name}: {e}")
    else:
        print(f"  Skipping {var_name} - no valid data found")


# =============================================================================
# BLOCK 10: SLICED BAR CHARTS
# Comment out this entire block to skip sliced bar chart generation
# =============================================================================
print(f"\n=== BLOCK 10: Creating Sliced Bar Charts ===")

# Create bar charts output directory
os.makedirs('bar_charts', exist_ok=True)

# Define fields to analyze
bar_chart_fields = ['heat_flux', 'temperature']

for field_name in bar_chart_fields:
    # Check if this field exists in any block
    field_exists = False
    for block_name in block_names:
        if block_name in block_variables:
            if field_name in block_variables[block_name]['cell_data']:
                field_exists = True
                break
    
    if field_exists:
        print(f"\nCreating sliced bar chart for {field_name}...")
        try:
            # Create sliced bar chart with fresh slice data for each block
            for block_name in block_names:
                if block_name in block_variables and field_name in block_variables[block_name]['cell_data']:
                    save_path = f'bar_charts/sliced_bar_chart_{field_name.replace(" ", "_").lower()}_{block_name}.png'
                    slice_results = processor.plot_sliced_bar_chart(
                        field_name=field_name,
                        axis='y',
                        num_slices=10,
                        data_type='cell',
                        block_name=block_name,
                        save_path=save_path,
                        show_percentages=(field_name == 'heat_flux'),
                        show_totals=True
                    )
                    print(f"  ✓ Sliced bar chart for {block_name}: {save_path}")
            
        except Exception as e:
            print(f"  ✗ Failed sliced bar chart for {field_name}: {e}")
    else:
        print(f"  Skipping sliced bar chart for {field_name} - field not found in any block")

# =============================================================================
# BLOCK 11: BLOCK COMPARISON BAR CHARTS
# Comment out this entire block to skip block comparison bar chart generation
# =============================================================================
print(f"\n=== BLOCK 11: Creating Block Comparison Bar Charts ===")

for field_name in bar_chart_fields:
    # Check if this field exists in any block
    field_exists = False
    for block_name in block_names:
        if block_name in block_variables:
            if field_name in block_variables[block_name]['cell_data']:
                field_exists = True
                break
    
    if field_exists:
        print(f"\nCreating block comparison chart for {field_name}...")
        try:
            # Create block comparison bar chart
            block_results = processor.plot_block_comparison_chart(
                field_name=field_name,
                output_dir='bar_charts',
                save_png=True,
                save_html=True,
                block_spec=None,  # All blocks
                show_totals=True,
                use_percentages=(field_name == 'heat_flux')  # Percentages for heat flux
            )
            print(f"  ✓ Block comparison chart: bar_charts/block_comparison_{field_name.replace(' ', '_').lower()}.png")
            print(f"  ✓ Block comparison chart: bar_charts/block_comparison_{field_name.replace(' ', '_').lower()}.html")
            
        except Exception as e:
            print(f"  ✗ Failed block comparison chart for {field_name}: {e}")
    else:
        print(f"  Skipping block comparison chart for {field_name} - field not found in any block")

# =============================================================================
# BLOCK 12: INTEGRATE HEAT FLUX OVER ALL BLOCKS AND SAVE TO CSV
# =============================================================================
print("\n=== BLOCK 2: Integrate heat_flux over all blocks ===")
try:
    processor.save_integrated_fields_to_csv(
        variable_list=['heat_flux'],
        weight_field='face_area_magnitude',
        data_type='cell',
        csv_path='integrated_heat_flux.csv'
    )
    print("  ✓ Integrated heat_flux saved to integrated_heat_flux.csv")
except Exception as e:
    print(f"  Failed to integrate heat_flux: {e}")

# =============================================================================
# BLOCK 13: SAVE VARIABLE STATS TO CSV
# =============================================================================
print("\n=== BLOCK 3: Save variable statistics to CSV ===")
try:
    processor.save_variable_stats_to_csv(
        csv_path='variable_statistics.csv'
    )
    print("  ✓ Variable statistics saved to variable_statistics.csv")
except Exception as e:
    print(f"  Failed to save variable statistics: {e}")

# =============================================================================
# FINAL SUMMARY AND STATISTICS
# =============================================================================
print("\n=== Processing Complete ===")
print("\nFiles generated:")
print("📁 averaged_data/")
print("   - *_avg.csv (slice-averaged data for each block)")
print("📁 contour_plots/")
print("   - contour_*_*.png (2D contour plots for each variable and block)")
print("📁 line_plots/")
print("   - averaged_lines_*.png (line plots from slice-averaged data)")
print("   - overlay_*_all_blocks.png (overlay plots: single variable across all blocks)")
print("📁 3d_plots/")
print("   - surface_*_*.html (3D surface plots)")
print("📁 surface_contours/")
print("   - surface_contour_*_*proj_*.html (2D contour plots projected on coordinate planes)")
print("   - geometry_surface_contour_combined_*_all_blocks.html (3D combined plots: all blocks, one variable each)")
print("   - geometry_surface_contour_combined_*_all_blocks.png (PNG versions for PowerPoint)")
print("📁 powerpoint_images/")
print("   - *.png (PowerPoint-ready images copied from surface_contours/)")

# Summary statistics
total_files = 0
for folder in ['averaged_data', 'contour_plots', 'line_plots', '3d_plots', 'surface_contours', 'powerpoint_images']:
    if os.path.exists(folder):
        count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        print(f"\n{folder}: {count} files")
        total_files += count

print(f"\nTotal files generated: {total_files}")
print(f"Processed {len(block_names)} blocks with {len(all_variables)} unique variables")