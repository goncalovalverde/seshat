import calculator

def test_calculator_init():
    c = calculator.Calculator(config={})
    assert hasattr(c, 'config')
