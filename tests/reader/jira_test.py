import reader.jira

def test_jira_class_exists():
    assert hasattr(reader.jira, 'Jira')
