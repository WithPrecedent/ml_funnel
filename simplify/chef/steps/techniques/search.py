
from dataclasses import dataclass

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from skopt import BayesSearchCV

from simplify.core.base import SimpleTechnique


@dataclass
class Search(SimpleTechnique):
    """Searches for optimal model hyperparameters using specified technique.

    Args:
        technique (str): name of technique.
        parameters (dict): dictionary of parameters to pass to selected
            algorithm.
        name (str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_finalize (bool): whether 'finalize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique : object = None
    parameters : object = None
    auto_finalize : bool = True
    name : str = 'searcher'

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """

    def _get_parameters_conditional(self, technique, parameters):
        if 'refit' in self.parameters:
            self.parameters['scoring'] = self.listify(
                    self.parameters['scoring'])[0]
        return self

    def _print_best_estimator(self):
        if self.verbose:
            print('Searching for best hyperparameters using',
                  self.technique, 'search algorithm')
            print('The', self.parameters['scoring'],
                  'score of the best estimator for this model is',
                  f'{self.algorithm.best_score_ : 4.4f}')
        return self

    """ Core siMpLify Methods """

    def draft(self):
        self.options = {
                'bayes': ['skopt', 'BayesSearchCV'],
                'grid': ['sklearn.model_selection', 'GridSearchCV'],
                'random': ['sklearn.model_selection', 'RandomizedSearchCV']}

    def produce(self, ingredients):
        self.algorithm.fit(ingredients.x_train, ingredients.y_train)
        self.best_estimator = self.algorithm.best_estimator_
        return self.best_estimator