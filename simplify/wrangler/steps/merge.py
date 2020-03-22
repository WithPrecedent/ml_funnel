"""
.. module:: merge
:synopsis: merges data with common key
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

from dataclasses.dataclasses import dataclasses.dataclass

from simplify.core.definitionsetter import WranglerTechnique


@dataclasses.dataclass
class Merge(WranglerTechnique):
    """Merges data sources together.

    Args:
        step(str): name of step.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_draft (bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    step: object = None
    parameters: object = None
    name: str = 'encoder'
    auto_draft: bool = True

    def __post_init__(self) -> None:
        return self

    def draft(self) -> None:
        self._options = SimpleRepository(contents = {}
        return self

    def publish(self, dataset, sources):
        return dataset