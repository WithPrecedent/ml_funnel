"""
.. module:: siMpLify project
:synopsis: data science projects made simple
:publisher: Corey Rayburn Yung
:copyright: 2019-2020
:license: Apache-2.0
"""

import dataclasses
import importlib
import pathlib
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import warnings

import numpy as np
import pandas as pd

import simplify
from simplify.core import base
from simplify.core import configuration
from simplify.core import dataset
from simplify.core import files
from simplify.core import worker
from simplify.core import utilities


@dataclasses.dataclass
class Project(base.SimpleSystem):
    """Controller class for siMpLify projects.

    Args:
        idea (Optional[Union[Idea, str]]): an instance of Idea or a string
            containing the file path or file name (in the current working
            directory) where a file of a supported file type with settings for
            an Idea instance is located. Defaults to None.
        filer (Optional[Union['Filer', str]]): an instance of Filer or a string
            containing the full path of where the root folder should be located
            for file output. A filer instance contains all file path and
            import/export methods for use throughout siMpLify. Defaults to None.
        dataset (Optional[Union['Dataset', pd.DataFrame, np.ndarray, str]]): an
            instance of Dataset, an instance of Data, a string containing the
            full file path where a data file for a pandas DataFrame is located,
            a string containing a file name in the default data folder (as
            defined in the shared Filer instance), a full folder path where raw
            files for data to be extracted from, a string
            containing a folder name which is an attribute in the shared Filer
            instance, a DataFrame, or numpy ndarray. If a DataFrame, Data
            instance, ndarray, or string is
            passed, the resultant data object is stored in the 'data' attribute
            in a new Dataset instance as a DataFrame. Defaults to None.
        workers (Optional[Union[List[str], Dict[str, 'Package'], Dict[str,
            'Worker'], 'SimpleRepository', 'Manager']]): mapping of 'Package'
            instances or the information needed to create one and store it in
            a 'Manager' instance. Defaults to an empty 'SimpleRepository' instance.
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared 'Idea' instance, 'name' should match the appropriate
            section name in 'Idea'. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. Defaults to
            'project'.
        identification (Optional[str]): a unique identification name for this
            'Project' instance. The name is used for creating file folders
            related to the 'Project'. If not provided, a string is created from
            the date and time.
        auto_draft (Optional[bool]): whether to call the 'draft' method when
            instanced. Defaults to True.
        auto_publish (Optional[bool]): whether to call the 'publish' method when
            instanced. Defaults to True.
        auto_apply (Optional[bool]): whether to call the 'apply' method when
            instanced. For auto_apply to have an effect, 'dataset' must also
            be passed. Defaults to False.

    """
    idea: Optional['Idea'] = None
    filer: Optional['Filer'] = None
    dataset: Optional[Union[
        'Dataset',
        pd.DataFrame,
        np.ndarray,
        str,
        Dict[str, Union[
            pd.DataFrame,
            np.ndarray,
            str]]]] = None
    workers: Optional[Union[
        List[str],
        Dict[str, 'Worker'],
        'SimpleRepository',
        'Manager']] = dataclasses.field(default_factory = base.SimpleRepository)
    name: Optional[str] = dataclasses.field(default_factory = lambda: 'project')
    identification: Optional[str] = dataclasses.field(
        default_factory = utilities.datetime_string)
    auto_draft: Optional[bool] = True
    auto_publish: Optional[bool] = True
    auto_apply: Optional[bool] = False

    def __post_init__(self) -> None:
        """Initializes class attributes and calls selected methods."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Validates 'Idea' instance.
        self.idea = configuration.Idea(contents = self.idea)
        # Adds general attributes from 'idea'.
        self.idea.inject(instance = self)
        # Validates 'Filer' instance.
        self.filer = files.Filer(root_folder = self.filer, idea = self.idea)
        # Validates 'Dataset' instance.
        self.dataset = dataset.Dataset(data = self.dataset, idea = self.idea)
        # Validates and initializes 'workers'.
        self.workers = self._validate_workers(workers = self.workers)
        self.workers = self._initialize_workers(workers = self.workers)
        # Creats an 'Overview' instance, providing an outline of the overall
        # project from 'Worker' instances stored in 'manager'.
        self.overview = Overview.create(manager = self.manager)
        # Creates a 'Library' instance for storing 'Book' instances.
        self.library = base.Simple(
            manager = self.manager,
            catalog = self.overview)
        # Initializes 'stage' and validates core siMpLify objects.
        super().__post_init__()
        # Calls 'draft' method if 'auto_draft' is True.
        if self.auto_draft:
            self.draft()
        # Calls 'publish' method if 'auto_publish' is True.
        if self.auto_publish:
            self.publish()
        # Calls 'apply' method if 'auto_apply' is True.
        if self.auto_apply:
            self.apply()
        return self

    """ Dunder Methods """

    def __iter__(self) -> Iterable:
        """Returns iterable for class instance, depending upon 'stage'.

        Returns:
            Iterable: different depending upon stage.

        """
        return iter(self.workers)

    """ Other Dunder Methods """

    def __call__(self) -> Callable:
        """Drafts, publishes, and applies Project.

        Calling Project as a function is compatible with and used by the
        command line interface.

        """
        self.auto_apply = True
        self.__post__init()
        return self

    def __repr__(self) -> str:
        """Returns string representation of a class instance."""
        return self.__str__()

    def __str__(self) -> str:
        """Returns string representation of a class instance."""
        return f'Project {self.identification}: {str(self.overview)}'

    """ Core siMpLify Methods """

    def add(self,
            item: Union[
                'Package',
                'Library',
                'Book',
                'Chapter',
                'Manager',
                'Worker',
                'Dataset',
                 str],
            name: Optional[str] = None,
            overwrite: Optional[bool] = False) -> None:
        """Adds 'worker' to 'manager' or 'book' to 'library'.

        Args:
            item (Union['Package', 'Library', 'Book', 'Chapter', 'Manager',
                'Worker', 'Dataset', str]): a siMpLify object to add
            name (Optional[str]): key to use for the passed item in either
                'library' or 'manager'. Defaults to None. If not passed, the
                'name' attribute of item will be used as the key for item.
           overwrite (Optional[bool]): whether to overwrite an existing
                attribute with the imported object (True) or to update the
                existing attribute with the imported object, if possible
                (False). Defaults to True.

        """
        if name is None:
            try:
                name = item.name
            except (AttributeError, TypeError):
                name = item
        if isinstance(item, str):
            self.manager.add(worker = self.options[item].load())
        elif isinstance(item, Worker):
            self.manager.add(worker = item)
        elif isinstance(item, Package):
            self.options[name] = item
            self.workers[name] = item
            self.manager.add(worker = item.load())
        elif isinstance(item, Book):
            self.library.add(book = item)
        else:
            raise TypeError(
                'add requires a Worker, Book, Package, or string type')
        return self

    def draft(self) -> None:
        """Initializes 'workers' and drafts a 'Library' instance."""
        # Iterates through 'workers' and creates Book instances in 'library'.
        for name, worker in self.manager.items():
            self.library = worker.publisher.draft(library = self.library)
        return self

    def publish(self) -> None:
        """Finalizes 'Book' instances in 'Library'."""
        # Iterates through 'workers' and finalizes each Book instance. The
        # finalized instances are stored in 'library'.
        for name, worker in self.manager.items():
            self.library = worker.publisher.publish(library = self.library)
        return self

    def apply(self, data: Optional['Dataset'] = None, **kwargs) -> None:
        """Applies created objects to passed 'data'.

        Args:
            data (Optional['Dataset']): data object for methods to be
                applied. If not passed, data stored in the 'dataset' is
                used.
            kwargs: any other parameters to pass to the 'apply' method of a
                'Scholar' instance.

        """
        # Assigns 'data' to 'dataset' attribute and validates it.
        if data:
            self.dataset = Dataset(data = data, idea = self.idea)
        # Iterates through each worker, creating and applying needed Books,
        # Chapters, and Techniques for each worker in the Library.
        for name, book in self.library.items():
            self.dataset, self.library = self.workers[name].apply(
                data = self.dataset,
                library = self.library,
                **kwargs)
        return self

    """ File Import/Export Methods """

    def load(self,
            file_path: Union[str, pathlib.Path],
            overwrite: Optional[bool] = True) -> None:
        """Loads a siMpLify object and stores it in the appropriate attribute.

        Args:
            file_path (Union[str, pathlib.Path]): path to saved 'Library'
                instance.
            overwrite (Optional[bool]): whether to overwrite an existing
                attribute with the imported object (True) or to update the
                existing attribute with the imported object, if possible
                (False). Defaults to True.

        """
        loaded = self.filer(file_path = file_path)
        if isinstance(loaded, Project):
            self = loaded
        elif isinstance(loaded, Library):
            if overwrite:
                self.library = loaded
            else:
                self.library.update(loaded)
        elif isinstance(loaded, Book):
            self.library.add(book = loaded)
        elif isinstance(loaded, Manager):
            if overwrite:
                self.manager = loaded
            else:
                self.manager.update(loaded)
        elif isinstance(loaded, Worker):
            self.manager.add(worker = loaded)
        elif isinstance(loaded, Dataset):
            if overwrite:
                self.dataset = loaded
            else:
                self.dataset.add(data = loaded)
        else:
            raise TypeError(
                'loaded object must be Projecct, Library, Book, Dataset, \
                     Manager, or Worker type')
        return self

    def save(self,
            attribute: Union[str, object],
            file_path: Optional[Union[str, pathlib.Path]]) -> None:
        """Saves a siMpLify object.

        Args:
            attribute (Union[str, object]): either the name of the attribute or
                siMpLify object to save.
            file_path (Optional[Union[str, pathlib.Path]]): path to save
                'attribute'.

        Raises:
            AttributeError: if 'attribute' is a string and cannot be found in
                the 'Project' subclass or its 'manager' and 'library'
                attributes.

        """
        if isinstance(attribute, str):
            try:
                attribute = getattr(self, attribute)
            except AttributeError:
                try:
                    attribute = getattr(self.manager, attribute)
                except AttributeError:
                    try:
                        attribute = getattr(self.library, attribute)
                    except AttributeError:
                        AttributeError(f'attribute not found in {self.name}')
        else:
            self.filer.save(attribute)
        return self

    """ Private Methods """

    def _initialize_workers(self,
                workers: Optional[List[str]]) -> Dict[str, 'Package']:
        """Validates 'workers' or converts them to the appropriate type.

        Args:
            workers (Optional[List[str]]): a list

        Returns:
            Dict[str, 'Package']:

        """
        self.options = self.idea['workers']
        if not workers:
            try:
                outer_key = self.__class__.__name__.lower()
                inner_key = f'{self.__class__.__name__.lower()}_workers'
                workers = utilities.listify(self.idea[outer_key][inner_key])
            except KeyError:
                pass
        if isinstance(workers, dict):
            return workers
        else:
            new_workers = {p: self.options[p] for p in workers}
            if new_workers:
                return new_workers
            else:
                return self.workers


@dataclasses.dataclass
class Package(base.SimpleComponent):

    name: Optional[str] = None
    module: Optional[str] = dataclasses.field(
        default_factory = lambda: 'simplify.core')
    instructions: Optional[str] = 'Instructions'


DEFAULT_PACKAGES = {
    'wrangler': worker.Worker(
        name = 'wrangler',
        module = 'simplify.wrangler.wrangler',
        instructions = 'WranglerInstructions'),
    'explorer': worker.Worker(
        name = 'explorer',
        module = 'simplify.explorer.explorer',
        instructions = 'ExplorerInstructions'),
    'analyst': worker.Worker(
        name = 'analyst',
        module = 'simplify.analyst.analyst',
        instructions = 'AnalystInstructions'),
    'critic': worker.Worker(
        name = 'critic',
        module = 'simplify.critic.critic',
        instructions = 'CriticInstructions'),
    'artist': worker.Worker(
        name = 'artist',
        module = 'simplify.artist.artist',
        instructions = 'ArtistInstructions')}