import calculator.flow


def test_cycle_data():
    assert callable(calculator.flow.cycle_data)


def test_throughput():
    assert callable(calculator.flow.throughput)


def test_velocity():
    assert callable(calculator.flow.velocity)


def test_story_points():
    assert callable(calculator.flow.story_points)


def test_lead_time():
    assert callable(calculator.flow.lead_time)


def test_cycle_time():
    assert callable(calculator.flow.cycle_time)


def test_avg_lead_time():
    assert callable(calculator.flow.avg_lead_time)


def test_net_flow():
    assert callable(calculator.flow.net_flow)


def test_wip():
    assert callable(calculator.flow.wip)


def test_cfd():
    assert callable(calculator.flow.cfd)


def test_defect_percentage():
    assert callable(calculator.flow.defect_percentage)
