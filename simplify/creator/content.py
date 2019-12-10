"""
.. module:: content
:synopsis: content builder
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from collections.abc import MutableMapping
from dataclasses import dataclass
from dataclasses import field
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform

from simplify.creator.codex import SimpleCodex
from simplify.library.utilities import listify


@dataclass
class Content(SimpleCodex):
    """Base class for building components in a Page.

    Takes an Outline subclass instance and creates a component object.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. If 'name' is not
            provided, __class__.__name__.lower() is used instead.
        _parent (Optional['Page']): optional way to set 'parent' property.

    """
    idea: 'Idea'
    name: Optional[str] = None
    _parent: Optional['Page'] = None

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        self.proxies = {'parent': 'page'}
        super().__post_init()
        return self

    """ Dunder Methods """

    def iter(self):
        raise NotImplementedError(' '.join([
            self.__class__.__name__, 'cannot have child classes to iterate']))

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Subclasses should provide their own methods, if needed."""
        return self

    def publish(self, data: Optional[object] = None) -> None:
        """Subclasses should provide their own methods, if needed."""
        return self

    def apply(self, outline: 'Outline' **kwargs) -> object:
        """Builds and returns an object.

        Args:
            outline (Optional['Outline']): instance containing information
                needed to build the desired objects.
            kwargs: extra arguments to use in building the desired object.

        Returns:
            object: subclasses should return built object.

        """
        return

    """ Properties """

    @property
    def children(self):
        raise NotImplementedError(' '.join([
            self.__class__.__name__, 'cannot have child classes']))

@dataclass
class Algorithm(Content):
    """Base class for building an algorithm for a Page subclass instance.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. If 'name' is not
            provided, __class__.__name__.lower() is used instead.
        _parent (Optional['Page']): optional way to set 'parent' property.

    """
    idea: 'Idea'
    name: Optional[str] = None
    _parent: Optional['Page'] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Core siMpLify Methods """

    def apply(self, outline: 'Outline', **kwargs) -> object:
        """Builds and returns an algorithm.

        Args:
            outline (Optional['Outline']): instance containing information
                needed to build an algorithm.
            kwargs: ignored by this class.

        Returns:
            object: a loaded algorithm.

        """
        return self._lazily_load_algorithm(outline = outline)


@dataclass
class ParameterBuilder(Content):
    """Base class for building parameters for an algorithm.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. If 'name' is not
            provided, __class__.__name__.lower() is used instead.
        _parent (Optional['Page']): optional way to set 'parent' property.

    """
    idea: 'Idea'
    name: Optional[str] = None
    _parent: Optional['Page'] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Private Methods """

    def _build_idea(self, outline: 'Outline') -> None:
        """Acquires parameters from Idea instance.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        self.bunch = {}
        try:
            self.bunch.update(self.idea_parameters)
        except AttributeError:
            pass
        return self

    def _build_selected(self, outline: 'Outline') -> None:
        """Limits parameters to those appropriate to the outline.

        If 'outline.selected' is True, the keys from 'outline.defaults' are
        used to select the final returned parameters.

        If 'outline.selected' is a list of parameter keys, then only those
        parameters are selected for the final returned parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        if outline.selected:
            if isinstance(outline.selected, list):
                parameters_to_use = outline.selected
            else:
                parameters_to_use = list(outline.default.keys())
            new_parameters = {}
            for key, value in self.bunch.items():
                if key in parameters_to_use:
                    new_parameters.update({key: value})
            self.bunch = new_parameters
        return self

    def _build_required(self, outline: 'Outline') -> None:
        """Adds required parameters (mandatory additions) to 'parameters'.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        try:
            self.bunch.update(outline.required)
        except TypeError:
            pass
        return self

    def _build_search(self, outline: 'Outline') -> None:
        """Separates variables with multiple options to search parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        self.space = {}
        if outline.hyperparameter_search:
            new_parameters = {}
            for parameter, values in self.bunch.items():
                if isinstance(values, list):
                    if any(isinstance(i, float) for i in values):
                        self.space.update(
                            {parameter: uniform(values[0], values[1])})
                    elif any(isinstance(i, int) for i in values):
                        self.space.update(
                            {parameter: randint(values[0], values[1])})
                else:
                    new_parameters.update({parameter: values})
            self.bunch = new_parameters
        return self

    def _build_runtime(self, outline: 'Outline') -> None:
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout siMpLify is the
        addition of a random seed for a consistent, replicable state.

        The runtime variables should be stored as attributes in the SimpleCodex
        instance so that the values listed in outline.runtimes match those
        attributes to be added to parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        try:
            for key, value in outline.runtime.items():
                try:
                    self.bunch.update({key: getattr(self.author, value)})
                except AttributeError:
                    error = ' '.join('no matching runtime parameter',
                                     key, 'found in', self.author.name)
                    raise AttributeError(error)
        except (AttributeError, TypeError):
            pass
        return self

    def _build_conditional(self, outline: 'Outline') -> None:
        """Modifies 'parameters' based upon various conditions.

        An SimpleCodex class should have its own '_build_conditional' method for this
        method to modify 'parameters'. That method should have a 'parameters'
        and 'name' (str) argument and return the modified 'parameters'.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        if 'conditional' in outline:
            try:
                self.bunch = self._parent._build_conditional(
                    name = outline.name,
                    parameters = self.bunch)
            except AttributeError:
                pass
        return self


    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Declares parameter_types."""
        self.parameter_types = [
            'idea',
            'selected',
            'required',
            # 'search',
            'runtime',
            'conditional']
        return self

    def apply(self,
            outline: 'Outline',
            data: Optional[object] = None) -> None:
        """Finalizes parameter 'bunch'.

        Args:
            outline ('Outline'): class containing information about parameter
                construction.
            data (Optional[object]): data container (Ingredients, Review, etc.)
                that has attributes matching any items stored in
                'outline.data_dependent'.

        """
        for parameter_type in self.parameter_types:
            if parameter_type == 'data_dependent':
                getattr(self, '_'.join(['_build', parameter_type]))(
                    outline = outline,
                    data = data)
            else:
                getattr(self, '_'.join(['_build', parameter_type]))(
                    outline = outline)
        return self


@dataclass
class Parameters(MutableMapping):
    """Base class for parameters to be stored.

    Args:
        parameters (Optional[Dict[str, Any]]): dictionary of parameters to be
            passed to a siMpLify or external object.
        page (Optional['Page']): Page instance associated with these parameters.
        data_dependent (Optional[Dict[str, str]]): a dictionary of data
            dependent parameters. Keys are the name of the parameter and values
            are the attribute name of the passed 'data' object given to the
            'apply' method.

    """
    parameters: Optional[Dict[str, Any]] = field(default_factory = dict)
    page: Optional['Page'] = None
    data_dependent: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.page is not None:
            self.name = '_'.join([self.page.name, 'parameters'])
        else:
            self.name = self.__class__.__name__.lower()
        return self

    """ Required ABC Methods """

    def __delitem__(self, item: str) -> None:
        """Deletes item in options.

        Args:
            item (str): name of key in options.

        """
        try:
            del self.parameters[item]
        except KeyError:
            pass
        return self

    def __getitem__(self, item: str) -> Any:
        """Returns item in options.

        If there are no matches, the method searches for a matching wildcard.

        Args:
            item (str): name of key in options.

        Raises:
            KeyError: if 'item' is not found in options and does not match
                a recognized wildcard.

        """
        try:
            return self.parameters[item]
        except KeyError:
            raise KeyError(' '.join([item, 'is not in', self.name]))

    def __setitem__(self, item: str, value: Any) -> None:
        """Sets 'item' in options to 'value'.

        Args:
            item (str): name of key in options.
            value (Any): value to be paired with 'item' in options.

        """
        self.parameters[item] = value
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of options."""
        return iter(self.parameters)

    def __len__(self) -> int:
        """Returns length of options."""
        return len(self.parameters)

    """ Core siMpLify Methods """

    def apply(self, data: Optional[object]) -> Dict[str, Any]:
        """Completes parameter dictionary by adding data dependent parameters.

        Args:
            data (object): data object with attributes for data dependent
                parameters to be added.

        Returns:
            parameters with any data dependent parameters added.

        """
        if self.data_dependents is not None:
            for key, value in self.data_dependents.items():
                try:
                    self.parameters.update({key, getattr(data, value)})
                except KeyError:
                    print('no matching parameter found for', key, 'in',
                        data.name)
        return self.parameters