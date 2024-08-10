import bork.api

def test_aliases():
    assert frozenset(bork.api.aliases()) == frozenset((
        'docs', 'docs-clean',
        'lint',
        'test', 'test-fast', 'test-slow',
    ))
