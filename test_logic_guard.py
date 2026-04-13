# Test Logic Guard
from engine.logic_guard import get_logic_guard

guard = get_logic_guard()

print('=== LOGIC GUARD TEST ===')
print()

# Test modules
tests = [
    ('forecaster', {}),
    ('order_flow', {}),
    ('learning_loop', {}),
    ('fixed_learning', {}),
]

for mod, data in tests:
    can_run, msg = guard.can_run_module(mod, data)
    print(f'{mod}: Can run = {can_run}')
    print(f'  Message: {msg}')
    print()

# Available data
print('Available Data:')
for k, v in guard.available_data.items():
    print(f'  {k}: {v}')

print()
print('=== DONE ===')