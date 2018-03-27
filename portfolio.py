import numpy as np
#from sklearn import datasets
import scipy.stats as ss
#from scipy.optimize import minimize
#import sklearn
import cvxopt
#import scipy.cluster.hierarchy as sch
import pandas as pd
import random
import sklearn.covariance
import sklearn.model_selection
import sklearn.mixture
import sklearn.linear_model
import warnings
#import pomegranate
import sys
import matplotlib.pyplot as plt
import inspect
import warnings
import sklearn.exceptions
from sklearn.exceptions import ConvergenceWarning

#def get_random_matrix(n_samples, n_features):
#    cov = datasets.make_spd_matrix(n_features)
#    means = (np.random.random(n_features) - 0.5) * 5
#    x = np.random.multivariate_normal(means, cov, n_samples)
#    return cov, means, x

def multivariate_normal_logpdf(x, mu, cov):
    return ss.multivariate_normal.logpdf(x, mu, cov, allow_singular=True)

def shannon_entropy(x, mu, cov):
    p = multivariate_normal_pdf(x, mu, cov)
    return sum(p*np.log(p))

def kl_divergence(mu1, cov1, mu2, cov2, n = int(1e6)):
    """
    p1 is true distribution
    """
    x = np.random.multivariate_normal(mu1, cov1, n)
    p1 = multivariate_normal_pdf(x, mu1, cov1)
    p2 = multivariate_normal_pdf(x, mu2, cov2)

    return ss.entropy(p1, p2)

def is_none(x):
    return isinstance(x, type(None))



class NaiveBayesRegression(object):
    """
    Naive bayes model, where the number of hidden nodes acts as regularization for the data.

    """

    def __init__(self):
        pass

    # TODO fix
    def fit(self, x, distributions, n_nodes = 3):
        """
        Fit the hidden bayes model.
        x: array of size (n_samples, n_features)
        distributions: array of size (n_features, ) that indicates which distribution the 
            features follows. Can be any singlevariate distribution from pomegranate

        """

        init_dist = []
        for i, dist in enumerate(distributions):
            if isinstance(dist, DiscreteDistribution):
                pass


        product_distribution = pomegranate.distributions.IndependentComponentsDistribution()

        self.model = pomegranate.GeneralMixtureModel.from_samples(distributions, n_components = n_nodes, X = x)

class Estimators(object):
    """
    Estimators for covariance and/or means
    """

    def __init__(self, mean_estimator = 'mle', cov_estimator = 'mle'):
        self.mean_estimator = mean_estimator
        self.cov_estimator = cov_estimator
        self._set_mean_and_cov()
        #self.corr = self.get_mle_corr()

    def get_diag_covariance(self, x = None, ddof = 1):
        """
        """
        if is_none(x):
            x = self.x

        return np.diag(x.var(0))

    def get_mle_covariance(self, x = None, ddof = 1):
        """
        Calculates the MLE unbiased covariance matrix of a matrix x
        of shape (n_samples, n_features).
        """
        if is_none(x):
            x = self.x

        # 1e-7 to avoid singularities
        return np.cov(x, ddof = 1, rowvar = False) + 1e-7 * np.identity(x.shape[1])

    def get_oas_covariance(self, x = None):
        """
        Calculates the OAS (Oracle Approximating Shrinkage Estimator) covariance.
        """
        if is_none(x):
            x = self.x

        return sklearn.covariance.oas(self.x)[0]

    def get_lw_covariance(self, x = None):
        """
        Calculates the shrunk Ledoit-Wolf covariance matrix.
        """
        if is_none(x):
            x = self.x

        return sklearn.covariance.ledoit_wolf(self.x)[0]

#    def get_gl_covariance(self, x = None, alpha = 0.1):
#        """
#        Calculates the GraphLasso variance, where the off diagonal elements have l1-regularization
#        """
#
#        if is_none(x):
#            x = self.x
#
#        empirical_cov = self.get_mle_covariance(x = x)
#        return sklearn.covariance.graph_lasso(emp_cov = empirical_cov, alpha=alpha, max_iter=1000, tol=1e-6, verbose=False, enet_tol=1e-6)[0]
#
#    def get_gl_covariance_cv(self, x = None):
#        """
#        Leave-one-out cross validation of the covariance matrix by a Graphical Lasso.
#        """
#
#        if is_none(x):
#            x = self.x
#
#        model = sklearn.covariance.GraphLassoCV(alphas=[1e4,9e5], max_iter=100, tol=1e-2, 
#                verbose=True, enet_tol=1e-2, cv = self.cv_generator, n_jobs=2, n_refinements = 1)
#        model.fit(x)
#        print(model.alpha_)
#        print(model.covariance_[:2,:2])
#        print(self.get_mle_covariance(x = x)[:2,:2])
#        return model.covariance_ + 1e-3 * np.identity(self.n_assets)
#        mu = self.get_mle_mean(x)
#        alphas = 10**np.arange(-6, 6, 1.0)
#
#        ll = np.zeros(alphas.size)
#
#        for j, (train_idx, test_idx) in enumerate(self.cv_generator.split(range(x.shape[0]))):
#            x_train = x[train_idx]
#            x_test = x[test_idx]
#            for i, alpha in enumerate(alphas):
#                with warnings.catch_warnings():
#                    warnings.simplefilter("ignore")
#                    try:
#                        train_cov = self.get_gl_covariance(x = x_train, alpha = alpha)
#                        print(i, 1)
#                    except FloatingPointError:
#                        train_cov = self.get_mle_covariance(x = x_train)
#                        print(i, 0)
#                    ll[i] += np.sum(multivariate_normal_logpdf(x_test, mu, train_cov))
#
#
#        best_idx = np.argmax(ll)
#        print(ll, best_idx)
#        if best_idx == 0:
#            print("Warning: Consider lowering the minimum bound for alpha in graph lasso")
#        elif best_idx == alphas.size-1:
#            print("Warning: Consider raising the minimum bound for alpha in graph lasso")
#        return self.get_gl_covariance(x = x, alpha = alphas[best_idx])

    def get_mle_mean(self, x = None):
        if is_none(x):
            x = self.x

        return x.mean(0)

    def get_mle_corr(self, x = None):
        if is_none(x):
            x = self.x

        return np.corrcoef(x, rowvar=False)

    def _set_mean_and_cov(self):
        self.mean = self._get_mean()
        self.cov = self._get_cov()

    def _get_mean(self):
        if self.mean_estimator == 'mle':
            return self.get_mle_mean()
        elif is_none(self.mean_estimator):
            return None
        else:
            quit("Error: Unknown strategy %s for getting means" % self.mean_estimator)

    def _get_cov(self):
        if self.cov_estimator == 'mle':
            return self.get_mle_covariance()
        elif self.cov_estimator == 'diag':
            return self.get_diag_covariance()
        elif self.cov_estimator == 'oas':
            return self.get_oas_covariance()
        #elif self.cov_estimator == 'gl':
        #    return self.get_gl_covariance_cv()
        elif self.cov_estimator == 'lw':
            return self.get_lw_covariance()
        elif is_none(self.cov_estimator):
            return None
        else:
            quit("Error: Unknown strategy %s for getting covariance" % self.cov)

    def naive_bayes_mean(self):
        pass


class Portfolio(Estimators):
    """
    For creating portfolios.
    """

    def __init__(self, df = None, x = None, cost = None, classes = None, mean_estimator = 'mle',
            cov_estimator = 'mle', portfolio = 'zero_mean_min_variance', l2 = 0.0,
            positive_constraint = False, upper_mean_bound = 1, n_mixtures = 1, scaling = False,
            n_splits = 3, n_repeats = 1, metric = 'mae'):

        self.x = x
        self.cost = cost
        self.classes = classes
        self.positive_constraint = positive_constraint
        self.portfolio = portfolio
        self.upper_mean_bound = upper_mean_bound
        self.l2 = l2
        self.metric = metric
        self.cv_generator = sklearn.model_selection.RepeatedKFold(n_splits = n_splits, n_repeats = n_repeats)
        self.n_splits = n_splits
        self.n_repeats = n_repeats
        self.scaling = scaling

        # preprocess if a pandas dataframe was given
        self._pandas_parser(df)
        # Get mixture weights if n_mixture > 1
        #self._get_mixture_weights(n_mixtures)



        self.n_samples = self.x.shape[0]
        self.n_assets = self.x.shape[1]
        self._scale_data()

        super(Portfolio, self).__init__(mean_estimator = mean_estimator, 
                cov_estimator = cov_estimator)


    def _scale_data(self):
        """
        Scale everything by a constant to fit the first value
        """

        if self.scaling:
            target = self.x[0]
            self.slopes = np.sum(self.x * target, axis=1) / np.sum(self.x**2, axis=1)
            #idx = np.argsort(slopes)[len(slopes)//2]
            #target = self.x[idx]
            #self.slopes = np.sum(self.x * target, axis=1) / np.sum(self.x**2, axis=1)
            #quit(self.slopes)
            #self.slopes = np.sign(slopes)
            #self.slopes = np.ones(slopes.size)
            #print(np.sum(abs(self.slopes[:,None]*self.x - target)))
            self.x = self.slopes[:,None] * self.x
        else:
            self.slopes = np.ones(self.n_samples)

    def _pandas_parser(self, df):
        if is_none(df):
            return
        # just to make sure that stuff is sorted
        # supress warning as this works like intended
        pd.options.mode.chained_assignment = None
        df.sort_values(['functional', 'basis', 'unrestricted', 'reaction'])
        pd.options.mode.chained_assignment = "warn"

        unique_reactions = df.reaction.unique()
        unique_basis = df.basis.unique()
        unique_functionals = df.functional.unique()

        basis_to_id = {key:value for value, key in enumerate(unique_basis)}
        func_to_id = {key:value for value, key in enumerate(unique_functionals)}
        unres_to_id = {True: 1, False: 0}

        self.id_to_basis = {value:key for value, key in enumerate(unique_basis)}
        self.id_to_func = {value:key for value, key in enumerate(unique_functionals)}
        self.id_to_unres = {1:True, 0:False}

        energies = []
        times = []
        errors = []
        for idx, reac in enumerate(unique_reactions):
            sub_df = df.loc[df.reaction == reac]
            energies.append(sub_df.energy.tolist())
            errors.append(sub_df.error.tolist())
            times.append(sub_df.time.tolist())
            if idx == 0:
                func = [func_to_id[x] for x in sub_df.functional.tolist()]
                bas = [basis_to_id[x] for x in sub_df.basis.tolist()]
                unres = [unres_to_id[x] for x in sub_df.unrestricted.tolist()]
                classes = np.asarray([func, bas, unres], dtype=int)

        self.x = np.asarray(errors)
        self.raw = np.asarray(energies)
        self.cost = np.asarray(times)
        self.classes = classes

    def fit(self ):
        if self.portfolio == 'zero_mean_min_variance':
            self.weights = self.zero_mean_min_variance()
            self.intercept = 0
        elif self.portfolio == 'zero_mean_min_variance_cv':
            self.weights = self.zero_mean_min_variance_cv()
            self.intercept = 0
        elif self.portfolio == 'min_variance_upper_mean_bound':
            self.weights = self.min_variance_upper_mean_bound()
            self.intercept = 0
        elif self.portfolio == 'min_variance_upper_mean_bound_cv':
            self.weights = self.min_variance_upper_mean_bound_cv()
            self.intercept = 0
        elif self.portfolio == 'min_squared_mean':
            self.weights= self.min_squared_mean()
            self.intercept = 0
        elif self.portfolio == 'min_squared_mean_cv':
            self.weights= self.min_squared_mean_cv()
            self.intercept = 0
        elif self.portfolio == 'elastic_net':
            self.weights, self.intercept = self.elastic_net()
        elif self.portfolio == 'constrained_elastic_net':
            self.weights = self.constrained_elastic_net()
            self.intercept = 0
        elif self.portfolio == 'constrained_elastic_net_cv':
            self.weights = self.constrained_elastic_net_cv()
            self.intercept = 0
        elif self.portfolio == 'single_method':
            self.weights = self.single_method()
            self.intercept = 0
        else:
            quit("Error: Unknown portfolio method %s" % self.portfolio)

    def zero_mean_min_variance(self, x = None, alpha = 0):
        """
        Minimize x'Cx, where C is the covariance matrix and x is the portfolio weights.
        The constraints sum(x) = 1 and m'x = 0 is used, with m being the asset means.
        Optionally the constraint x >= 0 is used if self.positive_constraint == False.
        l2 regularization can be included.
        """

        if is_none(x):
            x = self.x

        # suppress output
        cvxopt.solvers.options['show_progress'] = False

        # objective
        P = cvxopt.matrix(self.cov + alpha * np.identity(self.n_assets))
        q = cvxopt.matrix(0.0, (self.n_assets,1))

        #### constraints ###

        # optional constraint x >= 0 if positive_constraint == True
        # and l1 constraint
        if self.positive_constraint:
            G = cvxopt.matrix(-np.identity(self.n_assets))
            h = cvxopt.matrix(0.0, (self.n_assets, 1))
        else:
            G = cvxopt.matrix(0.0, (1, self.n_assets))
            h = cvxopt.matrix(0.0)

        # sum(x) = 1
        A1 = np.ones((1, self.n_assets))
        b1 = np.ones((1,1))
        # mean.T dot x = 0
        A2 = self.mean.reshape(1, self.n_assets)
        b2 = np.zeros((1,1))
        # combine them
        A = cvxopt.matrix(np.concatenate([A1, A2]))
        b = cvxopt.matrix(np.concatenate([b1, b2]))
        sol = cvxopt.solvers.qp(P, q, G, h, A, b)
        return np.asarray(sol['x']).ravel()

    def zero_mean_min_variance_cv(self):
        """
        Determine the optimal l2 value for the zero_mean_min_variance approach
        by n_splits x n_repeats repeated k-fold cross validation
        """

        if self.positive_constraint:
            l2 = 10**np.arange(-9, 2.01, 0.5)
        else:
            l2 = 10**np.arange(-9, -5.01, 0.5)

        return self.internal_cv(self.zero_mean_min_variance, l2)

    def min_variance_upper_mean_bound_cv(self):
        """
        Determine the optimal l2 value for the min_variance_upper_mean_bound approach
        by n_splits x n_repeats repeated k-fold cross validation
        """

        l2 = 10**np.arange(-9, -5.01, 0.5)

        return self.internal_cv(self.min_variance_upper_mean_bound, l2)

    def min_squared_mean_cv(self):
        """
        Determine the optimal l2 value for the min_squared_mean approach
        by n_splits x n_repeats repeated k-fold cross validation
        """

        if self.positive_constraint:
            l2 = 10**np.arange(-9, 1.01, 0.5)
        else:
            l2 = 10**np.arange(-9, -3.01, 0.5)

        return self.internal_cv(self.min_squared_mean, l2)

    #def internal_cv(self, method, alphas):
    #    """
    #    Determines the optimal regularization parameter of
    #    the given alphas, for a given method
    #    """

    #    se = np.zeros((self.n_repeats, alphas.size))

    #    for i, (train, test) in enumerate(self.cv_generator.split(range(self.n_samples))):
    #        for j, v in enumerate(alphas):
    #            weights = method(x = self.x[train], alpha = v)
    #            se[i//self.n_splits, j] += sum(np.sum(weights * self.x[test], axis=1)**2)

    #    best_idx = np.argmin(np.median(se, axis=0))
    #    #print(best_idx, alphas.size)
    #    if best_idx == 0:
    #        print("Warning: Consider lowering the minimum bound for alpha for method %s" % str(method))
    #    elif best_idx == alphas.size-1:
    #        print("Warning: Consider raising the minimum bound for alpha for method %s" % str(method))
    #    return method(alpha = alphas[best_idx])

    def internal_cv(self, method, alphas):
        """
        Determines the optimal regularization parameter of
        the given alphas, for a given method
        """

        se = np.zeros(alphas.size)

        for i, (train, test) in enumerate(self.cv_generator.split(range(self.n_samples))):
            for j, v in enumerate(alphas):
                weights = method(x = self.x[train], alpha = v)
                se[j] += sum(np.sum(weights * self.x[test], axis=1)**2)

        best_idx = np.argmin(se)
        #print(best_idx, alphas.size)
        if best_idx == 0 and alphas[0] > 1e-9:
            print("Warning: Consider lowering the minimum bound for alpha for method %s" % str(method))
        elif best_idx == alphas.size-1:
            print("Warning: Consider raising the minimum bound for alpha for method %s" % str(method))
        return method(alpha = alphas[best_idx])

    #def internal_cv(self, method, alphas):
    #    """
    #    Determines the optimal regularization parameter of
    #    the given alphas, for a given method
    #    """

    #    best_alphas = []

    #    for i, (train, test) in enumerate(self.cv_generator.split(range(self.n_samples))):
    #        lowest_se = np.inf
    #        best_alpha_idx = None
    #        for j, v in enumerate(alphas):
    #            weights = method(x = self.x[train], alpha = v)
    #            se = sum(np.sum(weights * self.x[test], axis=1)**2)
    #            if se <= lowest_se:
    #                lowest_se = se
    #                best_alpha_idx = j
    #        print(best_alpha_idx)
    #        best_alphas.append(best_alpha_idx)



    #    best_idx = int(np.median(best_alphas))
    #    #print(best_idx, alphas.size)
    #    if best_idx == 0:
    #        print("Warning: Consider lowering the minimum bound for alpha for method %s" % str(method))
    #    elif best_idx == alphas.size-1:
    #        print("Warning: Consider raising the minimum bound for alpha for method %s" % str(method))
    #    return method(alpha = alphas[best_idx])

    def min_variance_upper_mean_bound(self, x = None, alpha = 0):
        """
        Minimize x'Cx, where C is the covariance matrix and x is the portfolio weights.
        The constraints sum(x) = 1 and |m'x| < self.upper_mean_bound is used, with m being the asset means.
        Optionally the constraint x >= 0 is used if self.positive_constraint == False.
        l2 regularization can be added.
        """

        if is_none(x):
            x = self.x

        # suppress output
        cvxopt.solvers.options['show_progress'] = False

        ### objectives ###
        P = cvxopt.matrix(self.cov + alpha * np.identity(self.n_assets))
        q = cvxopt.matrix(0.0, (self.n_assets,1))

        #### constraints ###

        # |m'x| < self.upper_mean_bound as well as
        # optional constraint x >= 0 if positive == False
        if self.positive_constraint:
            G = np.empty((self.n_assets + 2, self.n_assets))
            G[:-2, :] = -np.identity(self.n_assets)
            G[-2:, :] = self.mean
            G[-1:, :] = -self.mean
            G = cvxopt.matrix(G)
            h = np.zeros((self.n_assets+2, 1))
            h[-2:] = self.upper_mean_bound
            h = cvxopt.matrix(h)
        else:
            G = np.zeros((2, self.n_assets))
            G[0,:] = self.mean
            G[1,:] = -self.mean
            G = cvxopt.matrix(G)
            h = np.zeros((2,1))
            h[:] = self.upper_mean_bound
            h = cvxopt.matrix(h)


        # sum(x) = 1
        A = cvxopt.matrix(1.0, (1, self.n_assets))
        b = cvxopt.matrix(1.0)

        ### solve ###

        sol = cvxopt.solvers.qp(P, q, G, h, A, b)
        return np.asarray(sol['x']).ravel()

    def min_squared_mean(self, x = None, alpha = 0):
        """
        Minimize x'mm'x + x'Cx, where C is the covariance matrix, m being the asset means and x is the portfolio weights.
        The constraints sum(x) = 1 is used.
        Optionally the constraint x >= 0 is used if self.positive_constraint == False.
        """

        if is_none(x):
            x = self.x

        # objective
        P = cvxopt.matrix(self.mean[:, None] * self.mean[None, :] + 
                self.cov + alpha * np.identity(self.n_assets))
        q = cvxopt.matrix(0.0, (self.n_assets,1))

        #### constraints ###

        # optional constraint x >= 0 if positive_constraint == False
        if self.positive_constraint:
            G = cvxopt.matrix(-np.identity(self.n_assets))
            h = cvxopt.matrix(0.0, (self.n_assets, 1))
        else:
            G = cvxopt.matrix(0.0, (1, self.n_assets))
            h = cvxopt.matrix(0.0)

        # sum(x) = 1/slopes
        #A = cvxopt.matrix(1.0, (self.n_samples, self.n_assets))
        #b = cvxopt.matrix(1.0/self.slopes, (self.n_samples, 1))
        A = cvxopt.matrix(1.0, (1, self.n_assets))
        b = cvxopt.matrix(1.0)
        # suppress output
        cvxopt.solvers.options['show_progress'] = False

        # solve
        sol = cvxopt.solvers.qp(P, q, G, h, A, b, verbose=False)

        return np.asarray(sol['x']).ravel()

    def elastic_net(self):
        """
        Minimize the squared error of a linear model with l1 and l2 regularization.
        The regularization parameters are determined by 5 fold cross validation.
        """

        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        model = sklearn.linear_model.ElasticNetCV(
                cv = self.cv_generator, 
                #l1_ratio = [0.0001, 0.001, 0.01, 0.1, .2, 0.5, 0.8, 0.9, 0.99, 1.0],
                l1_ratio = np.arange(0.0,1.01,0.05),
                max_iter = 500, positive = self.positive_constraint,
                alphas = 10**np.arange(-3,4.01,0.25),
                n_jobs=2, tol=1e-5)
        

        model.fit(self.raw, (self.raw - self.x)[:,0])

        if np.isclose(model.alpha_, 1e-3) or \
                np.isclose(model.alpha_, 1e4):
            print("Warning: Increase alpha range. Best alpha was %s" % str(model.alpha_))

        #print(model.alphas_)
        #print("l1:", model.l1_ratio_)
        #print("al:", model.alpha_)
        #print("ni:", model.n_iter_)

        return model.coef_, model.intercept_

    def constrained_elastic_net(self, x = None, alpha = None, init_weights = None):
        """
        Minimize x'(L+EE')x, where L is a constant times the identity matrix (l2 regularization),
        E is the error of the training set and x is the portfolio weights.
        The constraints sum(x) = 1 and x >= 0 is used.
        """

        if is_none(x):
            x = self.x
        if is_none(alpha):
            alpha = self.l2

        ### objectives ###
        P = cvxopt.matrix(x.T.dot(x) + alpha*np.identity(self.n_assets))
        q = cvxopt.matrix(0.0, (self.n_assets,1))

        #### constraints ###

        # x >= 0
        G = cvxopt.matrix(-np.identity(self.n_assets))
        h = cvxopt.matrix(0.0, (self.n_assets, 1))


        # sum(x) = 1
        A = cvxopt.matrix(1.0, (1, self.n_assets))
        b = cvxopt.matrix(1.0)

        # suppress output
        cvxopt.solvers.options['show_progress'] = False

        # change defaults
        #cvxopt.solvers.options['refinement'] = 5
        #cvxopt.solvers.options['maxiters'] = 1000
        #cvxopt.solvers.options['abstol'] = 1e-8
        #cvxopt.solvers.options['reltol'] = 1e-7
        #cvxopt.solvers.options['feastol'] = 1e-8

        ### solve ###
        if is_none(init_weights):
            sol = cvxopt.solvers.qp(P, q, G, h, A, b)
        else:
            # warmstart
            sol = cvxopt.solvers.qp(P, q, G, h, A, b, initvals = {'x':cvxopt.matrix(init_weights[:,None])})
        return np.asarray(sol['x']).ravel()

    def constrained_elastic_net_cv(self):
        """
        Determine the optimal l2 value for constrained elastic net
        by n_splits x n_repeats repeated k-fold cross validation
        """

        l2 = 10**np.arange(-5, 4.01, 0.5)

        return self.internal_cv(self.constrained_elastic_net, l2)

    def single_method(self):
        if self.metric == "mae":
            acc = np.mean(abs(self.x), axis=0)
        elif self.metric == "rmsd":
            acc = np.sqrt(np.mean((self.x)**2, axis=0))
        elif self.metric == "max":
            acc = np.max(abs(self.x), axis=0)
        else:
            quit("Unknown metric %s" % self.metric)

        idx = np.argmin(acc)

        self.weights = np.zeros(acc.shape)
        self.weights[idx] = 1

        idx_class = self.classes[:,idx]
        #print(self.id_to_func[idx_class[0]], self.id_to_basis[idx_class[1]], self.id_to_unres[idx_class[2]])
        return self.weights


def score(y_pred, metric):#, y = None):
    #if is_none(y):
    #    y = np.zeros(y_pred.shape[0])

    if metric == 'mae':
        #np.mean(abs(y_pred-y))
        return np.mean(abs(y_pred))
    elif metric == 'rmsd':
        #np.sqrt(np.mean((y_pred-y)**2))
        return np.sqrt(np.mean((y_pred)**2))
    elif metric == 'max':
        #np.max(abs(y_pred-y))
        return np.max(abs(y_pred))
    else:
        quit("Unknown metric: %s" % self.metric)

def outer_cv(df, kwargs):

    if 'n_splits' in kwargs:
        n_splits = kwargs['n_splits']
    else:
        n_splits = 3
    if 'n_repeats' in kwargs:
        n_repeats = kwargs['n_repeats']
    else:
        n_repeats = 1


    reactions = df.reaction.unique()

    portfolio_energies = []
    likelihoods = []
    errors = np.zeros((reactions.size, n_repeats))
    for i, (train_idx, test_idx) in enumerate(sklearn.model_selection.RepeatedKFold(
            n_splits = n_splits, n_repeats = n_repeats).split(reactions)):
        #print(i)

        train_df = df.loc[df.isin(reactions[train_idx]).reaction]

        m = Portfolio(df = train_df, **kwargs)
        m.fit()
        #cut = 1e-6
        #portfolio_energy = np.sum(np.clip(m.optimal_portfolio,cut, 1) / sum(np.clip(m.optimal_portfolio,cut, 1)) * energies)
        for idx in test_idx:
            reac = reactions[idx]
            energies = df.loc[df.reaction == reac].energy.as_matrix()
            target = (energies - df.loc[df.reaction == reac].error.as_matrix())[0]
            errors[idx, i//n_splits] = sum(m.weights * energies) + m.intercept - target
            #timings = df.loc[df.reaction == reac].time.as_matrix()

        #portfolio_energies.append(sum(m.weights * energies) + m.intercept - target)
        #likelihoods.append(multivariate_normal_pdf(energies, m.mean, m.cov))

    portfolio_energies = np.median(errors, axis=1)
    #portfolio_energies = np.mean(errors, axis=1)

    #ref_df = df.loc[(df.functional == 'M06-2X') & (df.basis == 'qzvp') & (df.unrestricted == True)][["reaction","error"]]
    #ref = ref_df.error.as_matrix()

    #plt.scatter(portfolio_energies, likelihoods)
    #plt.show()

    return portfolio_energies




    #print(abs(portfolio_energies).max(), np.sqrt(np.mean((portfolio_energies)**2)), np.mean(abs(portfolio_energies)))
    #fig, ax = plt.subplots()

    #ax.scatter(abs(portfolio_energies), abs(ref))
    #lims = [
    #        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
    #        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    #        ]
    #
    ## now plot both limits against eachother
    #ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    #ax.set_aspect('equal')
    #ax.set_xlim(lims)
    #ax.set_ylim(lims)

    #plt.show()

def print_statistics(d):
    for key, value in d.items():
        print("{:25s} {:>.2f} {:>.2f} {:>.2f}".format(key, score(value, metric='max'),  score(value, metric='rmsd'),  score(value, metric='mae')))

def evaluate_all_methods(df, n_splits = 3, n_repeats = 1):
    errors = {}

    np.random.seed(42)

    errors['single_method'] = outer_cv(df, {"portfolio": "single_method", "metric":"rmsd",
        'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['elastic_net'] = outer_cv(df, {"positive_constraint": 0, "portfolio": "elastic_net",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['positive_elastic_net'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "elastic_net", 
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    errors['constrained_elastic_net'] = outer_cv(df, {"portfolio": "constrained_elastic_net",
        'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['constrained_elastic_net_cv'] = outer_cv(df, {"portfolio": "constrained_elastic_net_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['zero_mean_min_variance'] = outer_cv(df, {"positive_constraint": 0, "portfolio": "zero_mean_min_variance",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['zero_mean_min_variance_cv'] = outer_cv(df, {"positive_constraint": 0, "portfolio": "zero_mean_min_variance_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_zero_mean_min_variance'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "zero_mean_min_variance",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_zero_mean_min_variance_cv'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "zero_mean_min_variance_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_half'] = outer_cv(df, {"upper_mean_bound":0.5, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_cv_half'] = outer_cv(df, {"upper_mean_bound":0.5, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_1'] = outer_cv(df, {"upper_mean_bound":1, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_cv_1'] = outer_cv(df, {"upper_mean_bound":1, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_2'] = outer_cv(df, {"upper_mean_bound":2, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_variance_upper_mean_bound_cv_2'] = outer_cv(df, {"upper_mean_bound":2, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['positive_min_variance_upper_mean_bound_half'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":0.5, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_min_variance_upper_mean_bound_cv_half'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":0.5, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['positive_min_variance_upper_mean_bound_1'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":1, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_min_variance_upper_mean_bound_cv_1'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":1, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['positive_min_variance_upper_mean_bound_2'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":2, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_min_variance_upper_mean_bound_cv_2'] = outer_cv(df, {"positive_constraint":1,"upper_mean_bound":2, "positive_constraint": 0, "portfolio": "min_variance_upper_mean_bound_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_squared_mean'] = outer_cv(df, {"positive_constraint": 0, "portfolio": "min_squared_mean",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    errors['positive_min_squared_mean'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "min_squared_mean",
        'n_splits': n_splits, 'n_repeats': n_repeats})
    errors['positive_min_squared_mean_diag'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "min_squared_mean", "cov_estimator":"diag",
        'n_splits': n_splits, 'n_repeats': n_repeats})
    ##errors['min_squared_mean_cv'] = outer_cv(df, {"positive_constraint": 0, "portfolio": "min_squared_mean_cv",
    ##    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['positive_min_squared_mean_cv'] = outer_cv(df, {"positive_constraint": 1, "portfolio": "min_squared_mean_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['oracle'] = outer_cv(df, {"cov_estimator": "oas", "positive_constraint": 1, "portfolio": "min_squared_mean",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})
    #errors['lw_cv'] = outer_cv(df, {"cov_estimator": "lw", "positive_constraint": 1, "portfolio": "min_squared_mean_cv",
    #    'n_splits': n_splits, 'n_repeats': n_repeats})

    #fig, ax = plt.subplots()

    #ax.scatter(abs(errors['positive_min_squared_mean']), abs(errors['single_method']))
    #lims = [
    #        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
    #        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    #        ]
    #
    ## now plot both limits against eachother
    #ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    #ax.set_aspect('equal')
    #ax.set_xlim(lims)
    #ax.set_ylim(lims)

    #plt.show()

    print_statistics(errors)



### TODO
# weights
# parallel joblib
# scaling
# timings
# bayes (pomegranate / pymc)
# mixtures
# elastic net
# t-distribution
# classification of error
# support both elastic net and portfolio methods
# cv distribution / means, cov etc.
# predict call

# Tasks
# compare methods using all data points (linear, normal, t, mixture)/(binary scaling, linear scaling)
# select best
# Repeat for maximum different basis sets
# Time vs accuracy
# Classification of error from probability

if __name__ == "__main__":

    if len(sys.argv) == 1:
        "Example usage: python portfolio abde12_reac.pkl"

    df = pd.read_pickle(sys.argv[1])
    #df = df.loc[(df.dataset == "abde12")]
    df = df.loc[(df.basis == 'qzvp') & (df.unrestricted == True)]
    #m = Portfolio(df=df)
    #mix = sklearn.mixture.GaussianMixture(n_components=4, covariance_type='full')
    #mix.fit(m.x)
    #print(mix.bic(m.x), mix.aic(m.x))
    #quit()
    #evaluate_all_methods(df, n_splits = 15, n_repeats = 5)
    evaluate_all_methods(df, n_splits = 5, n_repeats = 3)
    #evaluate_all_methods(df, n_splits = 3, n_repeats = 1)

