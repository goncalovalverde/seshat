import reader.gitlab

def test_gitlab_class_exists():
    assert hasattr(reader.gitlab, 'Gitlab')
