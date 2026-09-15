"""
Plugins designed for testing purposes.
"""

from __future__ import annotations

import typing

from ngen.cal import hookimpl


import numpy as np
import pandas as pd

if typing.TYPE_CHECKING:
    from datetime import datetime
    from hypy.nexus import Nexus
    from ngen.cal.model import ModelExec


def _zero_timeseries(
    start_time: datetime,
    end_time: datetime,
    simulation_interval: pd.Timedelta,
) -> pd.Series:
    index = pd.date_range(start_time, end_time, freq=simulation_interval)
    values = np.zeros(len(index))
    return pd.Series(data=values, index=index)


class NgenCalZeroObs:
    # NOTE: `ngen_cal_model_observations` only takes the first non-None result.
    # Therefore, try this implementation first to override any other
    # implementations that were loaded previously.
    @hookimpl(tryfirst=True)
    def ngen_cal_model_observations(
        self,
        nexus: Nexus,
        start_time: datetime,
        end_time: datetime,
        simulation_interval: pd.Timedelta,
    ) -> pd.Series:
        ds = _zero_timeseries(start_time, end_time, simulation_interval)
        ds = ds.rename("obs")
        return ds


class NgenCalZeroSim:
    def __init__(self):
        self.ds = None

    @hookimpl
    def ngen_cal_model_configure(self, config: ModelExec) -> None:
        # avoid circular import
        from ngen.cal.ngen import NgenBase

        assert isinstance(config, NgenBase)
        assert config.ngen_realization is not None
        start_time = config.ngen_realization.time.start_time
        end_time = config.ngen_realization.time.end_time
        simulation_interval = pd.to_timedelta(
            config.ngen_realization.time.output_interval, unit="s"
        )

        if (eval_options := config.eval_params) is not None:
            if eval_options.evaluation_start is not None:
                start_time = eval_options.evaluation_start
            if eval_options.evaluation_stop is not None:
                end_time = eval_options.evaluation_stop

        ds = _zero_timeseries(start_time, end_time, simulation_interval)
        ds = ds.rename("sim")
        self.ds = ds

    @hookimpl(tryfirst=True)
    def ngen_cal_model_output(self, nexus: Nexus) -> pd.Series | None:
        assert self.ds is not None, (
            "invariant, ngen_cal_model_configure must not have run"
        )
        return self.ds
