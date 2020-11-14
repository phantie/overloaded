from overloaded import Overloader
import pytest
import sys
from numbers import Number

@pytest.fixture
def overloaded():
    return Overloader()