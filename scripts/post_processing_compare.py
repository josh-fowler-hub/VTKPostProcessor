from PostProcessing.VTKPostProcessor import CFDPostProcessor, CFDComparisonProcessor
import os

# =============================================================================
# CONFIGURATION - Modify these paths and labels as needed
# =============================================================================
# Define datasets to compare
datasets = {
    'file_paths': [
        'dataset1/geom_vol.vtm',
        'dataset2/geom_vol.vtm',
        'dataset3/geom_vol.vtm'
    ],
    'labels': [
        'Configuration A',
        'Configuration B', 
        'Configuration C'
    ]
}

# Create output directories
print("Creating output directories...")
output_dirs = [
    'comparison_results',
    'comparison_results/bar_charts',
    'comparison_results/line_plots',
    'comparison_results/scatter_plots',
    'comparison_results/averaged_data',
    'comparison_results/powerpoint_images'
]

for dir_path in output_dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"  ✓ {dir_path}")

# =============================================================================
# INITIALIZE COMPARISON PROCESSOR
# =============================================================================
print(f"\n=== Initializing Comparison Processor ===")
print(f"Datasets to compare: {len(datasets['file_paths'])}")
for i, (path, label) in enumerate(zip(datasets['file_paths'], datasets['labels'])):
    print(f"  {i+1}. {label}: {path}")

try:
    comparison = CFDComparisonProcessor(datasets['file_paths'], datasets['labels'])
    print("✓ Comparison processor initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize comparison processor: {e}")
    exit(1)

# =============================================================================
# BLOCK 1: DATASET ANALYSIS AND VARIABLE DISCOVERY
# =============================================================================
print(f"\n=== BLOCK 1: Analyzing Datasets ===")

# Analyze each dataset individually
all_variables = set()
dataset_info = {}

for i, (processor, label) in enumerate(zip(comparison.processors, comparison.labels)):
    print(f"\n--- Analyzing Dataset: {label} ---")
    
    try:
        # Get block information
        block_names = processor.get_block_names(verbose=False)
        
        # Get variables for first block (assuming similar structure across blocks)
        if block_names:
            variables = processor.get_variable_names(block_name=block_names[0], verbose=False)
            cell_vars = variables['cell_data']
            point_vars = variables['point_data']
            
            dataset_info[label] = {
                'blocks': block_names,
                'cell_variables': cell_vars,
                'point_variables': point_vars
            }
            
            # Add to global variable set
            all_variables.update(cell_vars)
            
            print(f"  Blocks: {block_names}")
            print(f"  Cell variables: {cell_vars}")
            print(f"  Point variables: {point_vars}")
            
        else:
            print(f"  No blocks found in {label}")
            
    except Exception as e:
        print(f"  Failed to analyze {label}: {e}")

print(f"\nCommon variables found across datasets: {sorted(all_variables)}")

# =============================================================================
# BLOCK 2: COMPARISON BAR CHARTS
# Comment out this entire block to skip comparison bar chart generation
# =============================================================================
print(f"\n=== BLOCK 2: Creating Comparison Bar Charts ===")

# Define aggregation functions to test
agg_functions = ['mean', 'max', 'min', 'sum']
bar_chart_variables = ['pressure', 'temperature', 'heat_flux', 'density']  # Common CFD variables

for var_name in bar_chart_variables:
    if var_name in all_variables:
        print(f"\nCreating bar charts for '{var_name}'...")
        
        for agg_func in agg_functions:
            try:
                save_path = f'comparison_results/bar_charts/compare_bar_{var_name}_{agg_func}.png'
                comparison.compare_bar(
                    field=var_name,
                    agg_func=agg_func,
                    save_path=save_path,
                    data_type='cell'
                )
                print(f"  ✓ Bar chart ({agg_func}): {save_path}")
                
            except Exception as e:
                print(f"  ✗ Failed bar chart ({agg_func}) for {var_name}: {e}")
    else:
        print(f"  Skipping '{var_name}' - not found in datasets")

# =============================================================================
# BLOCK 3: COMPARISON LINE PLOTS
# Comment out this entire block to skip comparison line plot generation
# =============================================================================
print(f"\n=== BLOCK 3: Creating Comparison Line Plots ===")

# Define coordinate axes and variables for line plots
line_plot_axes = ['x', 'y', 'z']  # Spatial coordinates
line_plot_variables = ['pressure', 'temperature', 'velocity', 'heat_flux']
num_slices = 50  # Number of slices for averaging

for var_name in line_plot_variables:
    if var_name in all_variables:
        print(f"\nCreating line plots for '{var_name}'...")
        
        for x_axis in line_plot_axes:
            try:
                # Overlay mode - all datasets on same plot
                save_path = f'comparison_results/line_plots/compare_line_{var_name}_vs_{x_axis}_overlay.png'
                comparison.compare_line(
                    field=var_name,
                    x_axis=x_axis,
                    mode='overlay',
                    save_path=save_path,
                    data_type='cell',
                    num_slices=num_slices
                )
                print(f"  ✓ Line plot (overlay): {var_name} vs {x_axis}")
                
                # Combined mode - binned and aggregated
                save_path = f'comparison_results/line_plots/compare_line_{var_name}_vs_{x_axis}_combined.png'
                comparison.compare_line(
                    field=var_name,
                    x_axis=x_axis,
                    mode='combined',
                    combine_func='mean',
                    save_path=save_path,
                    data_type='cell',
                    num_slices=num_slices
                )
                print(f"  ✓ Line plot (combined): {var_name} vs {x_axis}")
                
            except Exception as e:
                print(f"  ✗ Failed line plot for {var_name} vs {x_axis}: {e}")
    else:
        print(f"  Skipping '{var_name}' - not found in datasets")

# =============================================================================
# BLOCK 4: COMPARISON SCATTER PLOTS
# Comment out this entire block to skip comparison scatter plot generation
# =============================================================================
print(f"\n=== BLOCK 4: Creating Comparison Scatter Plots ===")

# Define variable pairs for scatter plots
scatter_pairs = [
    ('pressure', 'temperature'),
    ('temperature', 'heat_flux'),
    ('y', 'pressure'),  # Coordinate vs field
    ('y', 'temperature'),  # Coordinate vs field
    ('velocity', 'pressure'),
]

for field_x, field_y in scatter_pairs:
    # Check if both variables exist
    x_exists = field_x in all_variables or field_x in ['x', 'y', 'z']
    y_exists = field_y in all_variables or field_y in ['x', 'y', 'z']
    
    if x_exists and y_exists:
        print(f"\nCreating scatter plot: '{field_y}' vs '{field_x}'...")
        
        try:
            save_path = f'comparison_results/scatter_plots/compare_scatter_{field_y}_vs_{field_x}.png'
            comparison.compare_scatter(
                field_x=field_x,
                field_y=field_y,
                save_path=save_path,
                data_type='cell'
            )
            print(f"  ✓ Scatter plot: {save_path}")
            
        except Exception as e:
            print(f"  ✗ Failed scatter plot for {field_y} vs {field_x}: {e}")
    else:
        missing = []
        if not x_exists:
            missing.append(field_x)
        if not y_exists:
            missing.append(field_y)
        print(f"  Skipping '{field_y}' vs '{field_x}' - missing variables: {missing}")

# =============================================================================
# BLOCK 5: BLOCK-SPECIFIC COMPARISONS
# Comment out this entire block to skip block-specific comparison generation
# =============================================================================
print(f"\n=== BLOCK 5: Creating Block-Specific Comparisons ===")

# Get block names from first dataset (assuming similar structure)
if comparison.processors:
    reference_blocks = comparison.processors[0].get_block_names(verbose=False)
    print(f"Reference blocks from first dataset: {reference_blocks}")
    
    # Create comparisons for each block
    for block_name in reference_blocks:
        print(f"\nCreating block-specific comparisons for '{block_name}'...")
        
        # Check if this block exists in all datasets
        block_exists_in_all = True
        for processor in comparison.processors:
            try:
                processor.get_block_index(block_name)
            except ValueError:
                block_exists_in_all = False
                break
        
        if block_exists_in_all:
            # Create bar chart for this specific block
            for var_name in ['pressure', 'temperature']:
                if var_name in all_variables:
                    try:
                        save_path = f'comparison_results/bar_charts/compare_bar_{var_name}_{block_name}_mean.png'
                        comparison.compare_bar(
                            field=var_name,
                            agg_func='mean',
                            save_path=save_path,
                            data_type='cell',
                            block_name=block_name
                        )
                        print(f"  ✓ Block bar chart: {var_name} ({block_name})")
                        
                    except Exception as e:
                        print(f"  ✗ Failed block bar chart for {var_name} ({block_name}): {e}")
        else:
            print(f"  Skipping '{block_name}' - not present in all datasets")

# =============================================================================
# BLOCK 6: AVERAGED DATA COMPARISON
# Comment out this entire block to skip averaged data comparison generation
# =============================================================================
print(f"\n=== BLOCK 6: Creating Averaged Data Comparisons ===")

# Generate slice-averaged data for each dataset
all_averaged_data = {}

for i, (processor, label) in enumerate(zip(comparison.processors, comparison.labels)):
    print(f"\nGenerating averaged data for '{label}'...")
    
    try:
        # Get first block for averaging (or modify to use specific block)
        block_names = processor.get_block_names(verbose=False)
        if block_names:
            df = processor.slice_and_average(
                axis='y',
                num_slices=50,
                data_type='cell',
                block_name=block_names[0]  # Use first block
            )
            
            if not df.empty:
                # Save individual dataset averaged data
                csv_path = f'comparison_results/averaged_data/{label.replace(" ", "_")}_avg.csv'
                processor.save_averages(df, csv_path)
                all_averaged_data[label] = df
                print(f"  ✓ Averaged data: {csv_path}")
            else:
                print(f"  No averaged data generated for {label}")
        else:
            print(f"  No blocks found in {label}")
            
    except Exception as e:
        print(f"  ✗ Failed to generate averaged data for {label}: {e}")

# Create overlay plots from averaged data
if len(all_averaged_data) > 1:
    print(f"\nCreating overlay plots from averaged data...")
    
    # Get common variables across all averaged datasets
    common_avg_vars = None
    for label, df in all_averaged_data.items():
        avg_vars = {col.replace('_avg', '') for col in df.columns if col.endswith('_avg')}
        if common_avg_vars is None:
            common_avg_vars = avg_vars
        else:
            common_avg_vars = common_avg_vars.intersection(avg_vars)
    
    print(f"Common averaged variables: {sorted(common_avg_vars)}")
    
    # Create overlay plots for each common variable
    for var_name in sorted(common_avg_vars):
        try:
            # Use the first processor's overlay method (they should all have the same interface)
            save_path = f'comparison_results/line_plots/overlay_averaged_{var_name}_all_datasets.png'
            comparison.processors[0].plot_overlay_averaged_lines(
                dataframes_dict=all_averaged_data,
                field_name=var_name,
                coordinate='y',
                save_path=save_path
            )
            print(f"  ✓ Averaged overlay: {var_name}")
            
        except Exception as e:
            print(f"  ✗ Failed averaged overlay for {var_name}: {e}")

# =============================================================================
# BLOCK 7: POWERPOINT-READY IMAGES
# Comment out this entire block to skip PowerPoint image generation
# =============================================================================
print(f"\n=== BLOCK 7: Creating PowerPoint-Ready Images ===")

# Copy key plots to PowerPoint directory with descriptive names
import shutil

powerpoint_files = [
    # Bar charts - most important comparisons
    ('comparison_results/bar_charts/compare_bar_pressure_mean.png', 'powerpoint_images/01_pressure_comparison_bar.png'),
    ('comparison_results/bar_charts/compare_bar_temperature_mean.png', 'powerpoint_images/02_temperature_comparison_bar.png'),
    
    # Line plots - key trends
    ('comparison_results/line_plots/compare_line_pressure_vs_y_overlay.png', 'powerpoint_images/03_pressure_vs_height_lines.png'),
    ('comparison_results/line_plots/compare_line_temperature_vs_y_overlay.png', 'powerpoint_images/04_temperature_vs_height_lines.png'),
    
    # Scatter plots - correlations
    ('comparison_results/scatter_plots/compare_scatter_temperature_vs_pressure.png', 'powerpoint_images/05_temperature_pressure_correlation.png'),
    
    # Averaged overlays
    ('comparison_results/line_plots/overlay_averaged_pressure_all_datasets.png', 'powerpoint_images/06_averaged_pressure_overlay.png'),
    ('comparison_results/line_plots/overlay_averaged_temperature_all_datasets.png', 'powerpoint_images/07_averaged_temperature_overlay.png'),
]

print("Copying key plots to PowerPoint directory...")
copied_count = 0
for source, destination in powerpoint_files:
    if os.path.exists(source):
        try:
            shutil.copy2(source, destination)
            print(f"  ✓ {os.path.basename(destination)}")
            copied_count += 1
        except Exception as e:
            print(f"  ✗ Failed to copy {os.path.basename(source)}: {e}")
    else:
        print(f"  - Source not found: {os.path.basename(source)}")

print(f"\nCopied {copied_count} images to PowerPoint directory")

# =============================================================================
# FINAL SUMMARY AND STATISTICS
# =============================================================================
print("\n" + "="*80)
print("COMPARISON PROCESSING COMPLETE")
print("="*80)

print(f"\nDatasets processed: {len(datasets['labels'])}")
for i, label in enumerate(datasets['labels']):
    print(f"  {i+1}. {label}")

print(f"\nVariables analyzed: {len(all_variables)}")
print(f"Variables: {sorted(all_variables)}")

print("\nFiles generated:")
print("📁 comparison_results/")
print("   📁 bar_charts/ - Comparison bar charts for different aggregation functions")
print("   📁 line_plots/ - Line plots comparing trends across datasets")
print("   📁 scatter_plots/ - Scatter plots showing correlations between variables")
print("   📁 averaged_data/ - Slice-averaged CSV data for each dataset")
print("   📁 powerpoint_images/ - Key plots ready for presentations")

# Count total files generated
total_files = 0
for folder in ['comparison_results/bar_charts', 'comparison_results/line_plots', 
               'comparison_results/scatter_plots', 'comparison_results/averaged_data',
               'comparison_results/powerpoint_images']:
    if os.path.exists(folder):
        count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        print(f"\n{folder}: {count} files")
        total_files += count

print(f"\nTotal files generated: {total_files}")
print("\n🎯 Key outputs for presentations:")
print("   - PowerPoint-ready images in comparison_results/powerpoint_images/")
print("   - Interactive comparison plots in comparison_results/")
print("   - Quantitative data in comparison_results/averaged_data/")

print("\n✅ Comparison analysis complete!")
