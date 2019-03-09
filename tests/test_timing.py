from pytest import raises

from tests.context import karma
from karma.timing import Timing, TimingError


def test_get_uptime_before_timer_started_will_fail():
    with raises(TimingError, match=r'Timer has not been started. Cannot get uptime.'):
        Timing.get_uptime()
