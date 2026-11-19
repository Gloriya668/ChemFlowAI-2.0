"""Select a version without changing existing saved projects or route identifiers."""
def case_key(spec):
    return 'pyridine525' if spec.get('dataset') == 'pyridine' and spec.get('source', {}).get('variant') == 'pyridine525' else spec['dataset']

def result_key(project, route=None):
    route = route or project.get('route')
    return 'pyridine525' if route == 'pyridine' and case_key(project['spec']) == 'pyridine525' else route
