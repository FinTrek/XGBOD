import numpy as np
import pandas as pd
from utility import precision_n
from sklearn.metrics import roc_auc_score
from sklearn.metrics import average_precision_score
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from PyNomaly import loop


def knn(X, n_neighbors):
    '''
    Utility function to return k-average, k-median, knn
    :param X: train data
    :param n_neighbors: number of neighbors
    :return:
    '''
    neigh = NearestNeighbors()
    neigh.fit(X)

    res = neigh.kneighbors(n_neighbors=n_neighbors, return_distance=True)
    # k-average, k-median, knn
    return np.mean(res[0], axis=1), np.median(res[0], axis=1), res[0][:, -1]


def generate_TOS_knn(X, y, k_list, feature_list):
    knn_clf = ["knn_mean", "knn_median", "knn_kth"]

    result_knn = np.zeros([X.shape[0], len(k_list) * len(knn_clf)])
    roc_knn = []
    prec_knn = []

    for i in range(len(k_list)):
        k = k_list[i]
        k_mean, k_median, k_k = knn(X, n_neighbors=k)
        knn_result = [k_mean, k_median, k_k]

        for j in range(len(knn_result)):
            score_pred = knn_result[j]
            clf = knn_clf[j]

            roc = np.round(roc_auc_score(y, score_pred), decimals=4)
            apc = np.round(average_precision_score(y, score_pred), decimals=4)
            prec_n = np.round(
                precision_n(y=y.ravel(), y_pred=score_pred, n=y.sum()),
                decimals=4)
            print('{clf} roc / apr / pren @ {k} is {roc} {apc} {pren}'.
                  format(clf=clf, k=k, roc=roc, apc=apc, pren=prec_n))
            feature_list.append(clf + str(k))
            roc_knn.append(roc)
            prec_knn.append(prec_n)
            result_knn[:, i * len(knn_result) + j] = score_pred

    return feature_list, roc_knn, prec_knn, result_knn


def generate_TOS_loop(X, y, k_list, feature_list):
    # only compatible with pandas
    df_X = pd.DataFrame(X)

    result_loop = np.zeros([X.shape[0], len(k_list)])
    roc_loop = []
    prec_loop = []

    for i in range(len(k_list)):
        k = k_list[i]
        clf = loop.LocalOutlierProbability(df_X, n_neighbors=k).fit()
        score_pred = clf.local_outlier_probabilities.astype(float)

        roc = np.round(roc_auc_score(y, score_pred), decimals=4)
        apc = np.round(average_precision_score(y, score_pred), decimals=4)
        prec_n = np.round(
            precision_n(y=y.ravel(), y_pred=score_pred, n=y.sum()), decimals=4)
        print('loop roc / apr / pren @ {k} is {roc} {apc} {pren}'.format(k=k,
                                                                         roc=roc,
                                                                         apc=apc,
                                                                         pren=prec_n))

        feature_list.append('loop_' + str(k))
        roc_loop.append(roc)
        prec_loop.append(prec_n)
        result_loop[:, i] = score_pred

    return feature_list, roc_loop, prec_loop, result_loop


def generate_TOS_lof(X, y, k_list, feature_list):
    result_lof = np.zeros([X.shape[0], len(k_list)])
    roc_lof = []
    prec_lof = []

    for i in range(len(k_list)):
        k = k_list[i]
        clf = LocalOutlierFactor(n_neighbors=k)
        y_pred = clf.fit_predict(X)
        score_pred = clf.negative_outlier_factor_

        roc = np.round(roc_auc_score(y, score_pred * -1), decimals=4)
        apc = np.round(average_precision_score(y, score_pred * -1), decimals=4)
        prec_n = np.round(
            precision_n(y=y.ravel(), y_pred=score_pred * -1, n=y.sum()),
            decimals=4)
        print('lof roc / apr / pren @ {k} is {roc} {apc} {pren}'.format(k=k,
                                                                        roc=roc,
                                                                        apc=apc,
                                                                        pren=prec_n))
        feature_list.append('lof_' + str(k))
        roc_lof.append(roc)
        prec_lof.append(prec_n)
        result_lof[:, i] = score_pred * -1

    return feature_list, roc_lof, prec_lof, result_lof


def generate_TOS_svm(X, y, nu_list, feature_list):
    result_ocsvm = np.zeros([X.shape[0], len(nu_list)])
    roc_ocsvm = []
    prec_ocsvm = []

    for i in range(len(nu_list)):
        nu = nu_list[i]
        clf = OneClassSVM(nu=nu)
        clf.fit(X)
        score_pred = clf.decision_function(X)

        roc = np.round(roc_auc_score(y, score_pred * -1), decimals=4)

        apc = np.round(average_precision_score(y, score_pred * -1), decimals=4)
        prec_n = np.round(
            precision_n(y=y.ravel(), y_pred=(score_pred * -1).ravel(),
                        n=y.sum()), decimals=4)
        print('svm roc / apr / pren @ {nu} is {roc} {apc} {pren}'.format(nu=nu,
                                                                         roc=roc,
                                                                         apc=apc,
                                                                         pren=prec_n))
        feature_list.append('ocsvm_' + str(nu))
        roc_ocsvm.append(roc)
        prec_ocsvm.append(prec_n)
        result_ocsvm[:, i] = score_pred.reshape(score_pred.shape[0]) * -1

    return feature_list, roc_ocsvm, prec_ocsvm, result_ocsvm


def generate_TOS_iforest(X, y, n_list, feature_list):
    result_if = np.zeros([X.shape[0], len(n_list)])
    roc_if = []
    prec_if = []

    for i in range(len(n_list)):
        n = n_list[i]
        clf = IsolationForest(n_estimators=n)
        clf.fit(X)
        score_pred = clf.decision_function(X)

        roc = np.round(roc_auc_score(y, score_pred * -1), decimals=4)
        apc = np.round(average_precision_score(y, score_pred * -1), decimals=4)
        prec_n = np.round(
            precision_n(y=y.ravel(), y_pred=(score_pred * -1).ravel(),
                        n=y.sum()), decimals=4)
        print('if roc / apr / pren @ {n} is {roc} {apc} {pren}'.format(n=n,
                                                                       roc=roc,
                                                                       apc=apc,
                                                                       pren=prec_n))
        feature_list.append('if_' + str(n))
        roc_if.append(roc)
        prec_if.append(prec_n)
        result_if[:, i] = score_pred.reshape(score_pred.shape[0]) * -1

    return feature_list, roc_if, prec_if, result_if