import viewer.tools

def test_add_trendline():
    assert callable(viewer.tools.add_trendline)

def test_add_percentile():
    assert callable(viewer.tools.add_percentile)

def test_add_range_buttons():
    assert callable(viewer.tools.add_range_buttons)
