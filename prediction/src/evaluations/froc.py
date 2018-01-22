import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.spatial
import sklearn.metrics as skl_metrics
from matplotlib.ticker import FixedFormatter
from tqdm import tqdm

# plot settings
FROC_minX = 0.125  # Minimum value of x-axis of FROC curve
FROC_maxX = 8  # Maximum value of x-axis of FROC curve
cpm_xpoints = [0.125, 0.25, 0.5, 1, 2, 4, 8]


def generateBootstrapSet(scanToCandidatesDict, FROCImList):
    """
    Generates bootstrapped version of set.
    """
    # get a random list of images using sampling with replacement
    FROCImList_rand = np.random.choice(FROCImList, size=len(FROCImList), replace=True)

    # get a new list of candidates
    candidatesExists = False
    for im in FROCImList_rand:
        if im not in scanToCandidatesDict:
            continue

        if not candidatesExists:
            candidates = np.copy(scanToCandidatesDict[im])
            candidatesExists = True
        else:
            candidates = np.concatenate((candidates, scanToCandidatesDict[im]), axis=1)

    return candidates


def compute_mean_ci(interp_sens, confidence=0.95):
    sens_mean = np.zeros((interp_sens.shape[1]), dtype='float32')
    sens_lb = np.zeros((interp_sens.shape[1]), dtype='float32')
    sens_up = np.zeros((interp_sens.shape[1]), dtype='float32')

    Pz = (1.0 - confidence) / 2.0

    for i in range(interp_sens.shape[1]):
        # get sorted vector
        vec = interp_sens[:, i]
        vec.sort()

        sens_mean[i] = np.average(vec)
        sens_lb[i] = vec[math.floor(Pz * len(vec))]
        sens_up[i] = vec[math.floor((1.0 - Pz) * len(vec))]

    return sens_mean, sens_lb, sens_up


def computeFROC_bootstrap(FROCGTList, FROCProbList,
                          FPDivisorList, FROCImList,
                          excludeList, numberOfBootstrapSamples=1000, confidence=0.95):
    set1 = np.concatenate(([FROCGTList], [FROCProbList], [excludeList]), axis=0)

    fps_lists = []
    sens_lists = []
    thresholds_lists = []

    FPDivisorList_np = np.asarray(FPDivisorList)
    FROCImList_np = np.asarray(FROCImList)

    # Make a dict with all candidates of all scans
    scanToCandidatesDict = {}
    for i in range(len(FPDivisorList_np)):
        seriesuid = FPDivisorList_np[i]
        candidate = set1[:, i: i + 1]

        if seriesuid not in scanToCandidatesDict:
            scanToCandidatesDict[seriesuid] = np.copy(candidate)
        else:
            scanToCandidatesDict[seriesuid] = np.concatenate((scanToCandidatesDict[seriesuid], candidate), axis=1)

    for i in tqdm(range(numberOfBootstrapSamples)):
        # Generate a bootstrapped set
        btpsamp = generateBootstrapSet(scanToCandidatesDict, FROCImList_np)
        fps, sens, thresholds = computeFROC(btpsamp[0, :], btpsamp[1, :], len(FROCImList_np), btpsamp[2, :])

        fps_lists.append(fps)
        sens_lists.append(sens)
        thresholds_lists.append(thresholds)

    # compute statistic
    all_fps = np.linspace(FROC_minX, FROC_maxX, num=10000)

    # Then interpolate all FROC curves at this points
    interp_sens = np.zeros((numberOfBootstrapSamples, len(all_fps)), dtype='float32')
    for i in range(numberOfBootstrapSamples):
        interp_sens[i, :] = np.interp(all_fps, fps_lists[i], sens_lists[i])

    # compute mean and CI
    sens_mean, sens_lb, sens_up = compute_mean_ci(interp_sens, confidence=confidence)

    return all_fps, sens_mean, sens_lb, sens_up


def computeFROC(FROCGTList, FROCProbList,
                totalNumberOfImages, excludeList):
    # Remove excluded candidates
    FROCGTList_local = []
    FROCProbList_local = []

    for i in range(len(excludeList)):
        if not excludeList[i]:
            FROCGTList_local.append(FROCGTList[i])
            FROCProbList_local.append(FROCProbList[i])

    numberOfDetectedLesions = sum(FROCGTList_local)
    totalNumberOfLesions = sum(FROCGTList)
    totalNumberOfCandidates = len(FROCProbList_local)

    fpr, tpr, thresholds = skl_metrics.roc_curve(FROCGTList_local, FROCProbList_local)
    # Handle border case when there are no false positives and ROC analysis give nan values.
    if sum(FROCGTList) == len(FROCGTList):
        print("WARNING, this system has no false positives..")
        fps = np.zeros(len(fpr))
    else:
        fps = fpr * (totalNumberOfCandidates - numberOfDetectedLesions) / totalNumberOfImages
    sens = (tpr * numberOfDetectedLesions) / totalNumberOfLesions
    return fps, sens, thresholds


def collect(annotations_filename,
            annotations_excluded_filename,
            seriesuids_filename,
            results_filename):
    annotations = pd.read_csv(annotations_filename)
    annotations_excluded = pd.read_csv(annotations_excluded_filename)
    seriesUIDs = pd.read_csv(seriesuids_filename, header=None, names=['seriesuid'])

    # nodules = annotations.loc[annotations.seriesuid.isin(seriesUIDs.seriesuid)]
    nodules = pd.merge(annotations, seriesUIDs, how='inner', on=['seriesuid'])
    nodules['included'] = True

    # nodules_excluded = annotations_excluded.loc[annotations_excluded.seriesuid.isin(seriesUIDs.seriesuid)]
    nodules_excluded = pd.merge(annotations_excluded, seriesUIDs, how='inner', on=['seriesuid'])
    nodules_excluded['included'] = False
    allNodules = pd.concat([nodules, nodules_excluded])
    allNodules.loc[allNodules.diameter_mm <= 0, 'diameter_mm'] = 10

    results = pd.read_csv(results_filename)
    # results = results.loc[results.seriesuid.isin(seriesUIDs.seriesuid)]
    results = pd.merge(results, seriesUIDs, how='inner', on=['seriesuid'])

    return (allNodules, results, seriesUIDs)


def make_plot(fps, sens, fps_bs_itp, sens_bs_mean, sens_bs_lb, sens_bs_up,
              FROCProbList, numberOfBootstrapSamples, outputDir, CADSystemName):
    """
    Plot FROC graphs in log scale.
    """
    fps_itp = np.linspace(FROC_minX, FROC_maxX, num=10001)
    sens_itp = np.interp(fps_itp, fps, sens)

    # create FROC graphs
    if len(FROCProbList):
        plt.figure()
        ax = plt.gca()
        clr = 'b'
        plt.plot(fps_itp, sens_itp, color=clr, label="%s" % CADSystemName, lw=2)
        if numberOfBootstrapSamples:
            plt.plot(fps_bs_itp, sens_bs_mean, color=clr, ls='--')
            plt.plot(fps_bs_itp, sens_bs_lb, color=clr, ls=':')  # , label = "lb")
            plt.plot(fps_bs_itp, sens_bs_up, color=clr, ls=':')  # , label = "ub")
            ax.fill_between(fps_bs_itp, sens_bs_lb, sens_bs_up, facecolor=clr, alpha=0.05)
        xmin = FROC_minX
        xmax = FROC_maxX
        plt.xlim(xmin, xmax)
        plt.ylim(0, 1)
        plt.xlabel('Average number of false positives per scan')
        plt.ylabel('Sensitivity')
        plt.legend(loc='lower right')
        plt.title('FROC performance - %s' % (CADSystemName))

        plt.xscale('log', basex=2)
        ax.xaxis.set_major_formatter(FixedFormatter(cpm_xpoints))

        # set your ticks manually
        ax.xaxis.set_ticks(cpm_xpoints)
        ax.yaxis.set_ticks(np.arange(0, 1.1, 0.1))
        plt.grid(b=True, which='both')
        plt.tight_layout()

        plt.savefig(os.path.join(outputDir, "froc_%s.png" % CADSystemName), bbox_inches=0, dpi=300)


def competition_performance_metric(annotations_path, annotations_excluded_path,
                                   seriesuids_path, results_path, output_dir, postfix='CAD',
                                   nb_bootstrap=1000, max_nb_CAD_marks=100,
                                   confidence=.95, plot=True):
    """
    Computes competition performance metric,
    implementation based on https://luna16.grand-challenge.org/evaluation/

    Params:
        annotations_path (str): path to annotations csv file, should contain following columns:
            [seriesuid, coordX, coordY, coordZ, diameter_mm]
        annotations_excluded_path (str): path to annotations excluded csv file, should contain following columns:
            [seriesuid, coordX, coordY, coordZ, diameter_mm]
        seriesuids_path (str): path to seriesuids csv file, should contain following columns:
            [seriesuid]
        results_path (str): path to results csv file, should contain following columns:
            [seriesuid, coordX, coordY, coordZ, probability]
        output_dir (str): directory for the output files.
        postfix (str): a postfix to output files.
        nb_bootstrap (int): number of bootstrap samples to be computed,
            if False then no bootstrap will be applied.
        max_nb_CAD_marks: maximum amount of registrations per scan (sorted by probabilities values)
        confidence: value for symmetric confidence interval.
        plot: whether to plot FROC graphs in log scale.

    Returns:
        1-d array of CPM values.
    """
    nodules, results, series = collect(
        annotations_path,
        annotations_excluded_path,
        seriesuids_path,
        results_path
    )

    cand_TPs = cand_FPs = cand_FNs = 0
    FROC_GTs = []
    FROC_probs = []
    FP_divisors = []
    excludes = []

    all_candidates = results.groupby(['seriesuid']).groups
    for seriesuid, candidates in all_candidates.items():
        candidates = results.loc[candidates]
        candidates = candidates.sort_values(
            ['probability'],
            ascending=False
        ).iloc[:max_nb_CAD_marks]

        nodule_annots = nodules[nodules.seriesuid == seriesuid]
        acoords = nodule_annots[['coordX', 'coordY', 'coordZ']].values
        bcoords = candidates[['coordX', 'coordY', 'coordZ']].values
        dists = scipy.spatial.distance.cdist(acoords, bcoords)
        covered = dists <= np.expand_dims(nodule_annots.diameter_mm / 2, -1)

        included = nodule_annots.included

        pvals = [candidates.probability[c].max() for c in covered[nodule_annots.included]]
        pvals = [p for p in pvals if not np.isnan(p)]

        FROC_probs.extend(pvals)
        FROC_GTs.extend([1] * len(pvals))
        FP_divisors.extend([seriesuid] * len(pvals))
        excludes.extend([False] * len(pvals))
        cand_TPs += len(pvals)

        uncovered = True ^ covered.sum(axis=-1, dtype=np.bool_)
        uncovered_incl = (included & uncovered).sum()

        cand_FNs += uncovered_incl
        # append a positive sample with the lowest probability, such that this is added in the FROC analysis
        FROC_GTs.extend([1.] * uncovered_incl)
        FROC_probs.extend([-1.] * uncovered_incl)
        FP_divisors.extend([seriesuid] * uncovered_incl)
        excludes.extend([True] * uncovered_incl)

        probs = candidates.probability[True ^ covered.sum(axis=0, dtype=np.bool_)]
        cand_FPs += len(probs)
        FROC_GTs.extend([0.] * len(probs))
        FROC_probs.extend(probs.values.tolist())
        FP_divisors.extend([seriesuid] * len(probs))
        excludes.extend([False] * len(probs))

    predicat = len(FROC_GTs) == len(FROC_probs) == len(FP_divisors) == len(excludes)
    assert predicat, "Length of FROC vectors not the same, this should never happen! Aborting..\n"

    # compute FROC
    fps, sens, thresholds = computeFROC(FROC_GTs, FROC_probs, len(series), excludes)

    if nb_bootstrap:
        fps_bs_itp, sens_bs_mean, sens_bs_lb, sens_bs_up = computeFROC_bootstrap(
            FROC_GTs,
            FROC_probs,
            FP_divisors,
            series.seriesuid,
            excludes,
            numberOfBootstrapSamples=nb_bootstrap,
            confidence=confidence
        )
    else:
        fps_bs_itp = sens_bs_mean = sens_bs_lb = sens_bs_up = None

    if plot:
        make_plot(fps, sens, fps_bs_itp, sens_bs_mean, sens_bs_lb, sens_bs_up,
                  FROC_probs, nb_bootstrap, output_dir, postfix)

    idxs = [min(np.where(fps >= p)[0]) for p in cpm_xpoints]

    return sens[idxs]
