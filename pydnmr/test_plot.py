# TODO: create meaningful tests that pass

# import pytest
import dnmrplot


def test_dnmrplot_2spin_type():

    WINDNMR_DEFAULT = (165.00, 135.00, 1.50, 0.50, 0.50, 0.5000)
    x, y = dnmrplot.dnmrplot_2spin(*WINDNMR_DEFAULT)
    print('x ', type(x), "y", type(y))
    assert type(x) == "<class 'numpy.ndarray'>"
    assert type(y) == "<class 'numpy.ndarray'>"