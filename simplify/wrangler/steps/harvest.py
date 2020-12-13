"""
.. module:: harvest
:synopsis: parses data sources to create pandas DataFrame
:author: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

from dataclasses.dataclasses import dataclasses.dataclass
import os

from simplify.core.definitionsetter import WranglerTechnique


"""DEFAULT_OPTIONS are declared at the top of a module with a SimpleDirector
subclass because siMpLify uses a lazy importing core. This locates the
potential module importations in roughly the same place as normal module-level
import commands. A SimpleDirector subclass will, by default, add the
DEFAULT_OPTIONS to the subclass as the 'options' attribute. If a user wants
to use another set of 'options' for a subclass, they just need to pass
'options' when the class is instanced.
"""
DEFAULT_OPTIONS = {
    'organize': ['simplify.core.retool', 'ReTool'],
    'parse': ['simplify.core.retool', 'ReTool']}


@dataclasses.dataclass
class Harvest(SimpleIterable):
    """Extracts data from text or other sources.

    Args:
        steps(dict): dictionary containing keys of WranglerTechnique names (strings)
            and values of WranglerTechnique class instances.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_draft(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    steps: object = None
    name: str = 'harvester'
    auto_draft: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    def _publish_organize(self, key):
        file_path = os.path.join(self.clerk.techniques,
                                 'organizer_' + key + '.csv')
        self.parameters = {'step': self.step,
                           'file_path': file_path}
        algorithm = self.workers[self.step](**self.parameters)
        self._set_columns(algorithm)
        return algorithm

    def _publish_parse(self, key):
        file_path = os.path.join(self.clerk.techniques,
                                 'parser_' + key + '.csv')
        self.parameters = {'step': self.step,
                           'file_path': file_path}
        algorithm = self.workers[self.step](**self.parameters)
        return algorithm

    def draft(self) -> None:
        return self

    def _set_columns(self, algorithm):
        prefix = algorithm.matcher.section_prefix
        if not hasattr(self, 'columns'):
            self.columns = []
        new_columns = list(algorithm.expressions.values())
        new_columns = [prefix + '_' + column for column in self.columns]
        self.columns.extend(new_columns)
        return self

    def _implement_organize(self, dataset, algorithm):
        dataset.df, dataset.source = algorithm.implement(
                df = dataset.df, source = dataset.source)
        return dataset

    def _implement_parse(self, dataset, algorithm):
        dataset.df = algorithm.implement(df = dataset.df,
                                         source = dataset.source)
        return dataset

    def publish(self):
        for key in self.parameters:
            if hasattr(self, '_publish_' + self.step):
                algorithm = getattr(
                        self, '_publish_' + self.step)(key = key)
            else:
                algorithm = getattr(self, '_publish_generic_list')(key = key)
            self.algorithms.append(algorithm)
        return self