"""
.. module:: predictors
:synopsis: predictions from models
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

from dataclasses import dataclass
from dataclasses import field
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Optional,
    Tuple, Union)

import numpy as np
import pandas as pd

from simplify.core.base import SimpleSettings
from simplify.critic.critic import Evaluator


@dataclass
class Predictor(Evaluator):
    """Base class for report preparation.

    Args:
        idea (Optional['Idea']): an instance with project settings.

    """
    idea: Optional['Idea'] = None

    """ Core siMpLify Methods """

    def apply(self, data: 'Chapter') -> 'Chapter':
        """Subclasses should provide their own methods."""
        return data
