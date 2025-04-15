from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import babel

# Get the Babel package directory
babel_dir = os.path.dirname(babel.__file__)

# Collect all submodules
hiddenimports = collect_submodules('babel')

# Explicitly add babel.numbers and its dependencies
hiddenimports.extend([
    'babel.numbers',
    'babel.numbers.format',
    'babel.numbers.parse',
    'babel.numbers.plural',
    'babel.numbers.symbols',
    'babel.numbers.validators',
])

# Collect all data files
datas = collect_data_files('babel')

# Explicitly add the numbers data files
numbers_data_dir = os.path.join(babel_dir, 'numbers')
if os.path.exists(numbers_data_dir):
    for file in os.listdir(numbers_data_dir):
        if file.endswith('.py'):
            datas.append((f'babel/numbers/{file}', 'babel/numbers')) 