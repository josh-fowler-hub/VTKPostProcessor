#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def test_matplotlib_contour():
    """Test matplotlib contour plotting without PyVista"""
    print("Testing Matplotlib 2D contour plotting...")
    
    # Generate synthetic 3D data
    np.random.seed(42)
    n_points = 1000
    
    # Create some synthetic CFD-like data
    x = np.random.uniform(-1, 1, n_points)
    y = np.random.uniform(-1, 1, n_points)
    z = np.random.uniform(-0.1, 0.1, n_points)
    
    # Create a synthetic field (like pressure)
    pressure = (
        np.sin(2 * np.pi * x) * np.cos(2 * np.pi * y) + 
        0.5 * np.sin(4 * np.pi * x) + 
        0.1 * np.random.normal(0, 1, n_points)
    )
    
    print(f"Generated {n_points} data points")
    print(f"X range: {x.min():.3f} to {x.max():.3f}")
    print(f"Y range: {y.min():.3f} to {y.max():.3f}")
    print(f"Pressure range: {pressure.min():.3f} to {pressure.max():.3f}")
    
    # Create regular grid for interpolation
    try:
        from scipy.interpolate import griddata
        
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        Xi, Yi = np.meshgrid(xi, yi)
        
        # Interpolate data to regular grid
        Zi = griddata((x, y), pressure, (Xi, Yi), method='linear')
        
        # Create contour plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Filled contours
        contourf = ax1.contourf(Xi, Yi, Zi, levels=15, cmap='viridis', alpha=0.8)
        contour = ax1.contour(Xi, Yi, Zi, levels=15, colors='black', alpha=0.4, linewidths=0.5)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_title('Pressure Contours (Filled)')
        ax1.set_aspect('equal')
        cbar1 = plt.colorbar(contourf, ax=ax1)
        cbar1.set_label('Pressure')
        
        # Scatter plot with original data
        scatter = ax2.scatter(x, y, c=pressure, cmap='viridis', s=2, alpha=0.6)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('Original Data Points')
        ax2.set_aspect('equal')
        cbar2 = plt.colorbar(scatter, ax=ax2)
        cbar2.set_label('Pressure')
        
        plt.tight_layout()
        
        # Save the plot
        output_file = 'test_matplotlib_contour.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Matplotlib contour plot saved: {output_file}")
        return True
        
    except ImportError:
        print("✗ SciPy not available for interpolation")
        return False
    except Exception as e:
        print(f"✗ Matplotlib contour failed: {e}")
        return False

def test_plotly_3d():
    """Test plotly 3D visualization"""
    print("\nTesting Plotly 3D visualization...")
    
    try:
        import plotly.graph_objects as go
        import plotly.offline as pyo
        
        # Generate synthetic 3D data
        np.random.seed(42)
        n_points = 2000
        
        # Create some synthetic CFD-like data with 3D structure
        x = np.random.uniform(-2, 2, n_points)
        y = np.random.uniform(-2, 2, n_points)
        z = np.random.uniform(-1, 1, n_points)
        
        # Create a synthetic field (like temperature)
        temperature = (
            np.exp(-(x**2 + y**2)/2) * np.cos(z) + 
            0.5 * np.sin(np.sqrt(x**2 + y**2 + z**2)) +
            0.1 * np.random.normal(0, 1, n_points)
        )
        
        print(f"Generated {n_points} 3D data points")
        print(f"Temperature range: {temperature.min():.3f} to {temperature.max():.3f}")
        
        # Sample data for performance (if too many points)
        if len(x) > 5000:
            indices = np.random.choice(len(x), 5000, replace=False)
            x = x[indices]
            y = y[indices] 
            z = z[indices]
            temperature = temperature[indices]
        
        # Create 3D scatter plot
        fig = go.Figure(data=go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=3,
                color=temperature,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Temperature')
            ),
            text=[f'T: {val:.3f}' for val in temperature],
            hovertemplate='<b>%{text}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='3D CFD Data Visualization',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            width=1000,
            height=800
        )
        
        # Save as HTML
        output_file = 'test_plotly_3d.html'
        pyo.plot(fig, filename=output_file, auto_open=False)
        
        print(f"✓ Plotly 3D plot saved: {output_file}")
        return True
        
    except ImportError:
        print("✗ Plotly not available")
        return False
    except Exception as e:
        print(f"✗ Plotly 3D visualization failed: {e}")
        return False

def test_ascii_contour():
    """Test ASCII art contour representation"""
    print("\nTesting ASCII contour visualization...")
    
    try:
        # Generate synthetic 2D data
        x = np.linspace(-2, 2, 50)
        y = np.linspace(-2, 2, 40)
        X, Y = np.meshgrid(x, y)
        
        # Create a synthetic field
        Z = np.sin(X) * np.cos(Y) + 0.5 * np.exp(-(X**2 + Y**2)/2)
        
        # Create ASCII representation
        levels = np.linspace(Z.min(), Z.max(), 10)
        chars = ' .:;+=xX$&'
        
        output_file = 'test_ascii_contour.txt'
        
        with open(output_file, 'w') as f:
            f.write("ASCII Contour Plot Test\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data range: {Z.min():.3f} to {Z.max():.3f}\n")
            f.write("Legend: " + " ".join([f"{chars[i]}={levels[i]:.2f}" for i in range(0, len(chars), 2)]) + "\n")
            f.write("-" * 50 + "\n")
            
            for j in range(len(y)):
                line = ""
                for i in range(len(x)):
                    value = Z[len(y)-1-j, i]  # Flip Y for proper orientation
                    level_idx = np.digitize(value, levels) - 1
                    level_idx = max(0, min(len(chars)-1, level_idx))
                    line += chars[level_idx]
                f.write(line + "\n")
        
        # Show first few lines in terminal
        with open(output_file, 'r') as f:
            lines = f.readlines()[:15]
            print("ASCII contour preview:")
            for line in lines:
                print("  " + line.strip())
        
        print(f"✓ ASCII contour saved: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ ASCII contour failed: {e}")
        return False

def main():
    print("Testing Alternative Visualization Backends")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test each backend
    if test_matplotlib_contour():
        success_count += 1
    
    if test_plotly_3d():
        success_count += 1
        
    if test_ascii_contour():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {success_count}/{total_tests} backends working")
    
    if success_count > 0:
        print("✓ Alternative visualization backends are available!")
        print("  You can use these for your CFD contour plots.")
    else:
        print("✗ No visualization backends working")
    
    # List generated files
    import glob
    files = glob.glob("test_*")
    if files:
        print(f"\nGenerated {len(files)} test files:")
        for f in files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()