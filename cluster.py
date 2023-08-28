# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 19:20:07 2020

@author: pablonicolasr,
         jorgehuck@gmail.com
"""

from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans

def cluster_ip(X, min_samples, metric="cosine"):
    """
    Agrupa los documentos en clusters utilizando el algoritmo DBSCAN.
    """
    cluster = DBSCAN(
        eps=0.02222,
        min_samples=min_samples,
        metric=metric,
        algorithm="brute"
    )

    cluster.fit_predict(X)
    return cluster

def kmeans_cluster(X, n_clusters):
    """
    Agrupa los documentos en clusters utilizando el algoritmo KMeans.
    """
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(X)
    return labels

def agglomerative_cluster(X, n_clusters):
    """
    Agrupa los documentos en clusters utilizando el algoritmo AgglomerativeClustering.
    """
    agglomerative = AgglomerativeClustering(n_clusters=n_clusters)
    labels = agglomerative.fit_predict(X)
    return labels
