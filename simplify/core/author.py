"""
.. module:: author
:synopsis: composite tree abstract base classes
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from dataclasses import field
from importlib import import_module
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from simplify.core.book import Book
from simplify.core.book import Chapter
from simplify.core.book import Page
from simplify.core.options import CodexOptions
from simplify.core.utilities import listify


@dataclass
class Creator(ABC):

    idea: 'Idea' = None
    inventory: 'Inventory' = None
    package: Optional[str] = None
    options: Optional[Union['CodexOptions', Dict[str, 'SimpleCodex']]] = field(
        default_factory = dict)
    steps: Optional[Union[List[str], str]] = field(default_factory = list)
    auto_publish: Optional[bool] = True

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        # Validates passed 'options' argument.
        self.options = self._validate_options()
        # Automatically calls 'draft' method.
        self.draft()
        # Calls 'publish' method if 'auto_publish' is True.
        if self.auto_publish:
            self.publish()
        return self

    """ Private Methods """

    def _validate_options(self) -> 'CodexOptions':
        """

        """
        if self.options:
            if isinstance(options, Dict):
                return CodexOptions(options = options)
            else:
                return options
        elif self.package:
            try:
                options = import_module(getattr(
                    self.packages[self.package], 'DEFAULT_OPTIONS'))
                return CodexOptions(options = options)
            except ImportError:
                raise ImportError(' '.join(
                    [self.packages[self.package], 'was not found']))
            except KeyError:
                raise KeyError(' '.join([self.package, 'does not exist']))
            except AttributeError:
                raise AttributeError(' '.join(
                    [self.package, 'does not have DEFAULT_OPTIONS']))
        else:
            raise AttributeError(' '.join(
                [self.__class__.__name__,
                 'requires either options or package argument']))


    def _build_filer(self, codex_type: str) -> 'SimpleFiler':
        """Returns SimpleFiler object appropriate to 'codex_type'.

        Args:
            codex_type (str): either 'book', 'chapter', or 'page'.

        Returns:
            'SimpleFiler' with settings for specific 'codex_type'.

        """
        return self.inventory.filers[codex_type]

    def draft(self) -> None:
        self.packages = {
            'farmer': 'simplify.farmer.farmer',
            'chef': 'simplify.chef.chef',
            'actuary': 'simplify.actuary.actuary',
            'critic': 'simplify.critic.critic',
            'artist': 'simplify.artist.artist'}
        return self

    def apply(self,
            name: str,
            book: Optional['Book'] = Book,
            technique: Optional[str] = None) -> 'SimpleCodex':
        """Creates a SimpleCodex object based upon arguments passed.

        Args:
            codex_type (str): either 'book', 'chapter', or 'page'.
            codex_object (Optional['SimpleCodex']): if the generic Book,
                Chapter, or Page is not to be used, an alternative class
                should be passed.

        Returns:
            SimpleCodex instance.

        """
        parameters = {}
        for need in self.needs[codex_type]:
            parameters[need] = getattr(self, '_'.join(['_draft', need]))()
        if codex_object is None:
            return self.default[codex_type](parameters)
        else:
            return codex_object(parameters)

@dataclass
class Author(Creator):
    """Builds completed Book instances.

    Args:
        idea (Idea): an instance of Idea containing siMpLify project settings.
        inventory (Inventory): an instance of Inventory containing file and
            folder management attributes and methods.
        options (Optional[Union['CodexOptions', Dict[str, 'SimpleCodex']]]):

        auto_publish (Optional[bool]): whether to call the 'publish' method when
            the class is instanced.

    """
    idea: 'Idea'
    inventory: 'Inventory'
    package: Optional[str] = None
    options: Optional[Union['CodexOptions', Dict[str, 'SimpleCodex']]] = field(
        default_factory = dict)
    steps: Optional[Union[List[str], str]] = field(default_factory = list)
    auto_publish: Optional[bool] = True

    def __post_init__(self):
        """Calls initialization methods and sets class instance defaults."""
        self.options = self._validate_options(options = self.options)
        super().__post_init__()
        return self

    """ Private Methods """

    def _build_steps(self, name: str) -> List[str]:
        """Gets 'steps' from Idea, if possible."""
        try:
            return listify(self.idea['_'.join([name, 'steps'])])
        except AttributeError:

    def _build_techniques(self,
            name: str,
            steps: List[str]) -> List[List[str]]:
        """Tries to get techniques from shared Idea instance.

        Returns:
            List[List[str]] of parallel sequences of steps.

        """
        possibilities = []
        for step in steps:
            try:
                possibilities.append(listify(
                    self.idea[name]['_'.join([step, 'techniques'])]))
            except KeyError:
                possibilities.append(['none'])
        return list(map(list, product(*possibilities)))

    def _build_chapters(self,
            name: str,
            technique: str) -> List['Chapter']:
        """
        """
        steps = self._build_steps(name = name)
        possibilities = self._build_techniques(name = name, steps = steps)

        for i, plan in enumerate(self.plans):
            self.chapters.add(
                chapter = self.chapter_type(
                    name = str(i),
                    steps = dict(zip(self.steps, plan)),
                    options = self.options,
                    metadata = self._publish_chapter_metadata(number = i)))
        return chapters

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Sets initial attributes."""
        self.options = {
            'chef': ChefPackage
        }

        return self

    def publish(self) -> None:
        """Creates instances of delegate creators."""
        new_creators = {}
        for name, creator in self.creators.items():
            new_creators[name] = creator(
                idea = self.idea,
                inventory = self.inventory)
        self.creators = new_creators
        return self

    def apply(self,
            name: str,
            book: Optional['Book'] = None,
            options: Optional['CodexOptions'] = None) -> 'Book':
        """Creates a SimpleCodex object based upon arguments passed.

        Args:

        Returns:
            SimpleCodex instance.

        """
        if book is None:
            book = Book
        return self.creators[codex_type].apply(
            name = name,
            codex_object = codex_object,
            technique = technique)

@dataclass
class ChapterCreator(Creator):
    """Base class for building SimpleCodex classes and instances.

    Args:
        idea (Idea): an instance of Idea containing siMpLify project settings.
        inventory (Inventory): an instance of Inventory containing file and
            folder management attributes and methods.

    """
    idea: 'Idea'
    inventory: 'Inventory'
    auto_publish: Optional[bool] = True

    def __post_init__(self):
        """Calls initialization methods and sets class instance defaults."""
        super().__post_init__()
        return self

    def draft(self) -> None:
        """Sets initial attributes."""
        self.needs = ['pages', 'filer']
        self.default = Chapter
        return self


@dataclass
class PageCreator(Creator):
    """Base class for building SimpleCodex classes and instances.

    Args:
        idea (Idea): an instance of Idea containing siMpLify project settings.
        inventory (Inventory): an instance of Inventory containing file and
            folder management attributes and methods.

    """
    idea: 'Idea'
    inventory: 'Inventory'
    auto_publish: Optional[bool] = True

    def __post_init__(self):
        """Calls initialization methods and sets class instance defaults."""
        super().__post_init__()
        return self

    def draft(self) -> None:
        """Sets initial attributes."""
        self.needs = ['algorithm', 'parameters', 'filer']
        self.default = Page
        return self


@dataclass
class SimpleCodex(ABC):
    """Base class for data processing, analysis, and visualization.

    SimpleComposite implements a modified composite tree pattern for organizing
    the various subpackages in siMpLify.

    Args:
        options (Optional[Union['CodexOptions', Dict[str, Any]]]): allows
            setting of 'options' property with an argument. Defaults to None.

    """
    options: (Optional[Union['CodexOptions', Dict[str, Any]]]) = None

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        # Sets default 'name' attribute if none exists.
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__.lower()
        # Automatically calls 'draft' method.
        self.draft()
        # Calls 'publish' method if 'auto_publish' is True.
        if hasattr(self, 'auto_publish') and self.auto_publish:
            self.publish()
        return self

    """ Dunder Methods """

    def __iter__(self) -> Iterable:
        """Returns '_children' dictionary as iterable."""
        return iter(self._children)

    """ Private Methods """

    def _draft_options(self) -> None:
        """Subclasses should provide their own methods to create 'options'.

        If the subclasses also allow for passing of '_options', the code below
        should be included as well.Any

        """
        if self._options is None:
            self._options = CodexOptions(options = {}, _author = self)
        elif isinstance(self._options, Dict):
            self._options = CodexOptions(
                options = self._options,
                _author = self)
        return self

    def _draft_techniques(self) -> None:
        """If 'techniques' does not exist, gets 'techniques' from 'idea'.

        If there are no matching 'steps' or 'techniques' in 'idea', a list with
        'none' is created for 'techniques'.

        """
        self.compare = False
        if self.techniques is None:
            try:
                self.techniques = getattr(
                    self.idea, '_'.join([self.name, 'steps']))
            except AttributeError:
                try:
                    self.compare = True
                    self.techniques = getattr(
                        self.idea, '_'.join([self.name, 'techniques']))
                except AttributeError:
                    self.techniques = ['none']
        else:
            self.techniques = listify(self.techniques)
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Required method that sets default values."""
        # Injects attributes from Idea instance, if values exist.
        self = self.idea.apply(instance = self)
        # initializes core attributes.
        self._draft_options()
        self._draft_techniques()
        return self

    def publish(self) -> None:
        """Required method which applies methods to passed data.

        Subclasses should provide their own 'publish' method.

        Args:
            data (Optional[object]): an optional object needed for the method.

        """
        if data is None:
            data = self.ingredients
        self.options.publish(
            techniques = self.techniques,
            data = data)
        return self

    def apply(self, data: Optional[object], **kwargs) -> None:
        """Applies created objects to passed 'data'.

        Subclasses should provide their own 'apply' method, if needed.

        Args:
            data (object): data object for methods to be applied.

        """
        for technique in self.techniques:
            data = self.options[technique].options.apply(
                key = technique,
                data = data,
                **kwargs)
        return data

    """ Composite Methods and Properties """

    def add_children(self, keys: Union[List[str], str]) -> None:
        """Adds outline(s) to '_children' from 'options' based on key(s).
        Args:
            keys (Union[List[str], str]): key(s) to 'options'.
        """
        for key in listify(keys):
            self._children[key] = self.options[key]
        return self

    def proxify(self) -> None:
        """Creates proxy names for attributes and methods."""
        try:
            proxy_attributes = {}
            for name, proxy in self.proxies.items():
                for key, value in self.__dict__.items():
                    if name in key:
                        proxy_attributes[key.replace(name, proxy)] = value
            self.__dict__.update(proxy_attributes)
        except AttributeError:
            pass
        return self

    @property
    def parent(self) -> 'SimpleCodex':
        """Returns '_parent' attribute."""
        return self._parent

    @parent.setter
    def parent(self, parent: 'SimpleCodex') -> None:
        """Sets '_parent' attribute to 'parent' argument.
        Args:
            parent (SimpleCodex): SimpleCodex class up one level in
                the composite tree.
        """
        self._parent = parent
        return self

    @parent.deleter
    def parent(self) -> None:
        """Sets 'parent' to None."""
        self._parent = None
        return self

    @property
    def children(self) -> Dict[str, Union['Outline', 'SimpleCodex']]:
        """Returns '_children' attribute.
        Returns:
            Dict of str access keys and Outline or SimpleCodex values.
        """
        return self._children

    @children.setter
    def children(self, children: Dict[str, 'Outline']) -> None:
        """Assigns 'children' to '_children' attribute.
        If 'override' is False, 'children' are added to '_children'.
        Args:
            children (Dict[str, 'Outline']): dictionary with str for reference
                keys and values of 'SimpleCodex'.
        """
        self._children = children
        return self

    @children.deleter
    def children(self, children: Union[List[str], str]) -> None:
        """ Removes 'children' for '_children' attribute.
        Args:
            children (Union[List[str], str]): key(s) to children classes to
                remove from '_children'.
        """
        for child in listify(children):
            try:
                del self._children[child]
            except KeyError:
                pass
        return self

    """ Strategy Methods and Properties """

    def add_options(self,
            options: Union['CodexOptions', Dict[str, Any]]) -> None:
        """Assigns 'options' to '_options' attribute.

        Args:
            options (options: Union['CodexOptions', Dict[str, Any]]): either
                another 'CodexOptions' instance or an options dict.

        """
        self.options += options
        return self

    @property
    def options(self) -> 'CodexOptions':
        """Returns '_options' attribute."""
        return self._options

    @options.setter
    def options(self, options: Union['CodexOptions', Dict[str, Any]]) -> None:
        """Assigns 'options' to '_options' attribute.

        Args:
            options (Union['CodexOptions', Dict[str, Any]]): CodexOptions
                instance or a dictionary to be stored within a CodexOptions
                instance (this should follow the form outlined in the
                CodexOptions documentation).

        """
        if isinstance(options, dict):
            self._options = CodexOptions(options = options)
        else:
            self._options.add(options = options)
        return self

    @options.deleter
    def options(self, options: Union[List[str], str]) -> None:
        """ Removes 'options' for '_options' attribute.

        Args:
            options (Union[List[str], str]): key(s) to options classes to
                remove from '_options'.

        """
        for option in listify(options):
            try:
                del self._options[option]
            except KeyError:
                pass
        return self