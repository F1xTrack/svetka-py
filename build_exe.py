import PyInstaller.__main__
import os

def build():
    # Assets to include
    assets = [
        ('assets', 'assets'),
        ('config.yaml', '.'),
    ]
    
    params = [
        'main.py',
        '--name=SvetkaAI',
        '--windowed',
        '--onefile',
        '--clean',
    ]
    
    for src, dst in assets:
        params.append(f'--add-data={src}{os.pathsep}{dst}')
        
    print(f"Running PyInstaller with: {params}")
    # PyInstaller.__main__.run(params) # This would run the build

if __name__ == "__main__":
    build()
