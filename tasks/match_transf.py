
import read_pars_file as rpf
import os
from os.path import join, isfile
import sys

import operator
import numpy as np
import random
from scipy.spatial.distance import cdist
from astropy.io import ascii
from astropy.table import Table
from astropy.table import Column

import timeit
import matplotlib.pyplot as plt


def genData():
    """
    Generate random (x,y) coordinates
    """
    random.seed(9001)
    np.random.seed(117)
    frames = {'U': {'60': [], '100': [], '250': []},
              'B': {'30': [], '70': [], '200': []},
              'V': {'30': [], '70': [], '100': []},
              'I': {'30': [], '50': [], '100': []}}
    # Initial positions
    x = np.random.uniform(0., 4000., 50000)
    y = np.random.uniform(0., 4000., 50000)
    # Factor that determines the number of stars per filter.
    fact = {'U': [5, .5], 'B': [7, .7], 'V': [8, .8], 'I': [10, 1.]}
    for filt, expDict in frames.iteritems():
        for exps in expDict.keys():
            N = 10 * int(float(exps) * np.random.randint(4, fact[filt][0]) *
                         fact[filt][1])
            # Sigma and mu for normal distribution
            sigma, mu = 1., 1.
            # Generate normally distributed noise.
            noise = sigma * np.random.randn(len(x)) + mu
            x_n, y_n = x + noise, y + noise
            x_n, y_n = x_n[:N], y_n[:N]
            xy_n = list(zip(*[x_n, y_n]))
            random.shuffle(xy_n)
            x_n, y_n = np.asarray(zip(*xy_n))
            mag = np.random.uniform(10., 24., N)
            e_mag = np.random.uniform(.01, .2, N)
            # plt.scatter(x, y)
            # plt.scatter(x_n, y_n)
            # plt.show()

            # This is the information stored for each star.
            expDict[exps] = [x_n, y_n, mag, e_mag]

    return frames


def in_params():
    """
    Read and prepare input parameter values.
    """
    pars = rpf.main()

    in_out_path = pars['mypath'].replace(
        'tasks', 'output/' + pars['match_folder'])

    fits_list = []
    for file in os.listdir(in_out_path):
        f = join(in_out_path, file)
        if isfile(f):
            if f.endswith('_phot.mag'):
                fits_list.append(f)

    # if not fits_list:
    #     print("No '*_phot.mag' files found in {} folder.".format(
    #         pars['match_folder']))
    #     print("Exit.")
    #     sys.exit()

    return pars, in_out_path


def framesOrder(frames):
    """
    Assign reference frame as the one with the largest number of detected
    stars. Order the remaining frames with the largest one on top.

    Parameters
    ----------
    frames : dictionary
        Observed photometry. Contains sub-dictionaries with the exposure
        times as keys, and the photometry data as values.

    Returns
    -------
    refFrameInfo : list
        Information about the reference frame. Each sub-list contains the
        filter name, exposure time, and number of stars added to the list
        by appending this frame.
    refFrame : list
        Photometry of the reference frame, selected as the frame with the
        largest number of stars.
    framesOrdered : list
        Each sub-list is an observed frame containing its filter name,
        exposure time, and photometry. Ordered putting the frame with the
        largest number of stars on top.

    """
    flen = []
    for filt, f in frames.iteritems():
        for expTime, fexpT in f.iteritems():
            N = len(fexpT[0])
            flen.append([filt, expTime, N])
    # Sort putting the frames with the largest number of stars first.
    sortIdx = sorted(flen, key=operator.itemgetter(2), reverse=True)

    # Isolate reference frame.
    filt, expTime = sortIdx[0][0], sortIdx[0][1]
    # Store each star separately.
    stars = list(zip(*frames[filt][expTime]))
    # Convert each float to list, to prepare for later appending of data.
    # refFrame = [star1, star2, ...starN]
    # starX = [x, y, mag, e_mag]
    # x = [x1, x2, ...] ; y = [y1, y2, ...] ; mag = [mag1, mag2, ...]
    refFrame = [list(list([_]) for _ in st) for st in stars]
    # Store here names of filters, exposure times, and number of stars added
    # when processing each frame.
    refFrameInfo = [[filt, expTime, len(refFrame)]]

    framesOrdered = []
    for filt, expTime, dummy in sortIdx[1:]:
        framesOrdered.append([filt, expTime, frames[filt][expTime]])

    return refFrameInfo, refFrame, framesOrdered


def closestStar(x_fr1, y_fr1, x_fr2, y_fr2):
    """
    For every star in fr1, find the closest star in fr2.

    Parameters
    ----------
    x_fr1 : list
       x coordinates for stars in the reference frame.
    y_fr1 : list
       y coordinates for stars in the reference frame.
    x_fr2 : list
       x coordinates for stars in the processed frame.
    y_fr2 : list
       y coordinates for stars in the processed frame.

    Returns
    -------
    min_dist_idx : numpy array
        Index to the processed star closest to the reference star, for each
        reference star:
        * fr2[min_dist_idx[i]]: closest star in fr2 to this star in fr1.
        Also the index of the minimum distance in dist[i], i.e.: distance to
        the closest processed star to the ith reference star:
        * dist[i][min_dist_idx[i]]: distance between these two stars.

    Notes
    -----
    len(fr1) = len(dist) = len(min_dist_idx)


    """
    fr1 = np.array(zip(*[x_fr1, y_fr1]))
    fr2 = np.array(zip(*[x_fr2, y_fr2]))
    # Distance to all stars in fr2, for each star in fr1.
    dist = cdist(fr1, fr2, 'euclidean')
    # Indexes to minimum distances.
    min_dist_idx = np.argmin(dist, axis=1)
    # Store only the minimum distances for each star in fr1, to a star in fr2.
    min_dists = [dist[i][md_idx] for i, md_idx in enumerate(min_dist_idx)]

    return min_dist_idx, min_dists


def starMatch(c1_ids, c2_ids, d2d, maxrad):
    """
    Reject duplicated matches and matched stars with distances beyond
    the maximum separation defined.

    Parameters
    ----------
    c1_ids : list
        IDs of stars in the reference frame.
    c2_ids : list
        IDs of stars in the processed frame, closest to each star in the
        reference frame.
    d2d : list
        Distances between each star in the reference frame, and the closest
        star in the processed frame.
    maxrad : float
        see frameMatch().

    Returns
    -------
    match_c1_ids : list
        IDs in reference frame for unique matches between frames.
    match_c2_ids : list
        IDs in the processed frame for unique matches between frames.
    no_match_c1 : list
        IDs of reference stars with no match found within maxrad.
    dupl_c1_ids : list
        IDs of reference stars that were matched to the same processed star as
        another reference star, and had a larger distance. These stars will
        be re-processed.

    """

    match_c1_ids, dupl_c1_ids, match_c2_ids, match_d = [], [], [], []
    # Indexes of matched star in both frames and distance between them.
    for c1_i, c2_i, d in zip(*[c1_ids, c2_ids, d2d]):
        # Filter by maximum allowed match distance.
        if d <= maxrad:
            # Check if this processed star was already stored as a match with
            # another reference star.
            if c2_i in match_c2_ids:
                # Index of this stored c2 star.
                j = match_c2_ids.index(c2_i)
                # If the previous match had a larger distance than this match,
                # replace with this match.
                if match_d[j] > d:
                    # Store replaced reference star here.
                    dupl_c1_ids.append(match_c1_ids[j])
                    # Now replace this star.
                    match_c1_ids[j] = c1_i
                    match_d[j] = d
                else:
                    dupl_c1_ids.append(c1_i)
            else:
                # Store IDs of both matched stars, and their distance.
                match_c1_ids.append(c1_i)
                match_c2_ids.append(c2_i)
                match_d.append(d)
        # else:
            # This reference star has no processed star closer than the max
            # distance allowed.

    return dupl_c1_ids, match_c1_ids, match_c2_ids, match_d


def frameCoordsUpdt(x_fr, y_fr, match_fr2_ids):
    """
    Identify stars in the processed frame that where not matched to any star
    in the reference frame.
    To avoid messing with the indexes, change the coordinates of already
    matched 'frame' stars so that they will not be matched again.

    Parameters
    ----------
    x_fr : list
        Original x coordinates of the stars in the processed frame.
    y_fr : list
        Original y coordinates of the stars in the processed frame.
    match_fr2_ids : list
        IDs of stars in the processed frame that were matched to a star in
        the reference frame.

    Returns
    -------
    x_fr_updt, y_fr_updt : list, list
        Coordinates of frame stars with those identified as matches changed
        so that they will not be matched again.

    """
    # Modify coordinates of matched stars. Use copy of arrays to avoid
    # overwriting the original coordinate values in 'frame'.
    x_fr_updt, y_fr_updt = np.copy(x_fr), np.copy(y_fr)
    x_fr_updt[match_fr2_ids] = -1000.
    y_fr_updt[match_fr2_ids] = -1000.

    return x_fr_updt, y_fr_updt


def UpdtRefFrame(
        refFrameInfo, refFrame, frame, match_fr1_ids_all, match_fr2_ids_all):
    """
    Update the reference frame adding the stars in the processed frame that
    were assigned as matches to each reference star. If a reference star was
    not assigned any match from the processed frame, add a Nan value.

    Also add to the end of the list (thereby increasing the length of the
    reference frame) those processed stars that could not be matched to any
    reference star.

    Parameters
    ----------
    refFrameInfo : list
        see frameMatch().
    refFrame : list
        see frameMatch().
    frame : list
        see frameMatch().
    match_fr1_ids_all : list
        Indexes of stars in refFrame that were matched to a star in frame.
    match_fr2_ids_all : list
        Indexes of stars in frame that were matched to a star in refFrame.

    Returns
    -------
    refFrameInfo : list
        Updated list.
    refFrame : list
        Updated list.

    """
    # Extract processed frame data.
    fr_filt, fr_expTime = frame[:2]
    x_fr, y_fr, mag_fr, emag_fr = frame[2]

    start_time = timeit.default_timer()
    # for each reference frame star.
    for ref_id, ref_st in enumerate(refFrame):
        # Check if this reference star was uniquely associated with a
        # processed star.
        if ref_id in match_fr1_ids_all:
            # Index of the associated processed 'frame' star.
            j = match_fr1_ids_all.index(ref_id)
            fr_id = match_fr2_ids_all[j]
            #
            ref_st[0].append(x_fr[fr_id])
            ref_st[1].append(y_fr[fr_id])
            ref_st[2].append(mag_fr[fr_id])
            ref_st[3].append(emag_fr[fr_id])
        else:
            # If this reference star could not be matched to any processed star
            # within the maximum match radius defined, add a NaN value
            # to mean that no match in the processed frame was found
            # for this reference star.
            ref_st[0].append(np.nan)
            ref_st[1].append(np.nan)
            ref_st[2].append(np.nan)
            ref_st[3].append(np.nan)
    print("C1", timeit.default_timer() - start_time)

    # Number of frames processed this far including the reference frame, but
    # excluding this one.
    N_fr = len(refFrame[0][0]) - 1

    start_time = timeit.default_timer()
    # For each processed frame star.
    fr_st_no_match = 0
    for fr_id, fr_st in enumerate(zip(*[x_fr, y_fr, mag_fr, emag_fr])):
        if fr_id not in match_fr2_ids_all:
            # This frame star was not matched to any reference star.
            x = [np.nan for _ in range(N_fr)] + [fr_st[0]]
            y = [np.nan for _ in range(N_fr)] + [fr_st[1]]
            mag = [np.nan for _ in range(N_fr)] + [fr_st[2]]
            emag = [np.nan for _ in range(N_fr)] + [fr_st[3]]
            refFrame.append([x, y, mag, emag])
            fr_st_no_match += 1
    print("C2", timeit.default_timer() - start_time)

    # Update the information stored on the frames processed.
    refFrameInfo.append([fr_filt, fr_expTime, fr_st_no_match])

    return refFrameInfo, refFrame


def frameMatch(refFrameInfo, refFrame, frame, maxrad):
    """
    Combine 'refFrame' and 'frame' into a new updated 'refFrame'.

    Parameters
    ----------
    refFrameInfo : list
        Contains one sub-list per processed frame with its filter name,
        exposure time, and number of stars not matched to the original refFrame
        that where added to the end of the list. Will be updated before this
        function ends.
    refFrame : list
        Collects all the cross-matched photometry into this single reference
        frame.
    frame : list
        Processed frame to be compared to refFrame.
    maxrad : float
        Maximum allowed distance (radius) for a match to be valid.

    Returns
    -------
    refFrameInfo : list
        Updated list.
    refFrame : list
        Updated list.

    """

    # Extract (x,y) coordinates, averaging the values assigned to the
    # same star.
    x_ref, y_ref = [], []
    for st in refFrame:
        x_ref.append(np.mean(st[0]))
        y_ref.append(np.mean(st[1]))

    # Extract filter name and exposure time of the processed frame.
    fr_filt, fr_expTime = frame[:2]
    x_fr, y_fr = frame[2][:2]
    print('\nProcessing frame: {}, {} (N={})'.format(
        fr_filt, fr_expTime, len(x_fr)))

    # Initial full list of IDs for the reference and processed frame.
    fr1_ids = np.arange(len(refFrame)).tolist()
    fr2_ids = np.arange(len(x_fr)).tolist()

    match_fr1_ids_all, match_fr2_ids_all, match_d_all = [], [], []
    # Continue until no more duplicate matches exist.
    counter = 1
    while fr1_ids:

        # Find closest stars between reference and processed frame.
        fr2_ids_dup, fr1fr2_d2d = closestStar(x_ref, y_ref, x_fr, y_fr)

        # Match reference and processed frame.
        fr1_ids, match_fr1_ids, match_fr2_ids, match_d =\
            starMatch(fr1_ids, fr2_ids_dup, fr1fr2_d2d, maxrad)
        # Store unique matches and distances.
        match_fr1_ids_all += match_fr1_ids
        match_fr2_ids_all += match_fr2_ids
        match_d_all += match_d

        print("{}.".format(counter))
        counter += 1

        print("Matched reference stars: {}".format(len(match_fr1_ids)))
        if match_fr1_ids:
            print("(Mean match dist: {:.2f} px)".format(
                np.mean(match_d_all)))
        print("Reference stars w/ no match within maxrad: {}".format(
            len(refFrame) - len(match_fr1_ids_all) - len(fr1_ids)))

        # If there are any stars from the reference frame that had
        # duplicated matches and were stored for re-matching.
        if fr1_ids:
            print("Reference stars for re-match: {}".format(
                len(fr1_ids)))
            print("Frame stars for re-match: {}".format(
                len(fr2_ids) - len(match_fr2_ids_all)))
            # Update coordinates of matched stars in processed frame.
            x_fr, y_fr = frameCoordsUpdt(x_fr, y_fr, match_fr2_ids)
        else:
            print("Processed stars w/ no match within maxrad: {}".format(
                len(fr2_ids) - len(match_fr2_ids_all)))

    # Update reference frame.
    refFrameInfo, refFrame = UpdtRefFrame(
        refFrameInfo, refFrame, frame, match_fr1_ids_all, match_fr2_ids_all)

    return refFrameInfo, refFrame


def groupFilters(refFrameInfo, refFrame):
    """
    Group obseved frames according to filters and exposure times.
    Also write to file, one per filter, all the cross-matched stars.

    Parameters
    ----------
    refFrameInfo : list
        See frameMatch()
    refFrame : list
        See frameMatch()

    Returns
    -------
    group_phot : dict
        Dictionary of astropy Tables(), one per observed filter with columns
        ordered as 'x_XXX  y_XXX  mag_XXX  emag_XXX', where 'XXX' represents
        the exposure time.

    """

    filters = {'U': {}, 'B': {}, 'V': {}, 'R': {}, 'I': {}}

    # Store data in 'filters' dict, grouped by exposure time.
    x, y, mag, e_mag = [list(zip(*_)) for _ in list(zip(*refFrame))]
    for i, (f, exp, N) in enumerate(refFrameInfo):
        filters[f].update({exp: {'x': x[i], 'y': y[i], 'mag': mag[i],
                                 'e_mag': e_mag[i]}})

    group_phot = {}
    # Order columns, add exposure time to col names, and write to file.
    for f, fdata in filters.iteritems():
        tab = Table()
        for expT, col_data in fdata.iteritems():
            t = Table(col_data, names=col_data.keys())
            t_order = t['x', 'y', 'mag', 'e_mag']
            t = Table(t_order,
                      names=[_ + expT for _ in ['x_', 'y_', 'mag_', 'emag_']])
            tab.add_columns(t.columns.values())

        if len(tab) > 0:
            # Add IDs.
            ids = Column(np.arange(len(tab)), name='#ID')
            tab.add_column(ids, index=0)
            # Append to grouped dictionary.
            group_phot.update({f: tab})

    return group_phot


def mag2flux(mag, zmag=15.):
    """
    Convert magnitudes to flux.

    Parameters
    ----------
    mag : array
        Magnitude values.
    zmag : float
        Arbitray (fixed) constant.

    Returns
    -------
    array
        Fluxes.

    """
    return 10 ** ((zmag - mag) / 2.5)


def emag2eflux(emags, flux):
    """
    Convert magnitude sigmas into flux sigmas.

    Parameters
    ----------
    emags : array
        Magnitude sigma values.
    flux : array
        Flux values.

    Returns
    -------
    array
        Flux sigmas.

    Notes
    -----
    The float used is:
        1.1788231 = (2.5 * log(e)) ** 2

    """
    return emags * (flux ** 2 / 1.1788231)


def flux2mag(flux, zmag=15.):
    """
    Convert fluxes into flux magnitudes.

    Parameters
    ----------
    flux : array
        Flux values.
    zmag : float
        Arbitray (fixed) constant.

    Returns
    -------
    array
        Magnitudes.

    """
    return -2.5 * np.log10(flux) + zmag


def eflux2emag(eflux, flux_mean):
    """
    Convert magnitude sigmas into flux sigmas.

    Parameters
    ----------
    eflux : array
        Flux sigmas.
    flux_mean : array
        Flux mean values.

    Returns
    -------
    array
        Magnitude sigmas.

    Notes
    -----
    The float used is:
        1.0857362 = 2.5 * log10(e)

    """
    return eflux * 1.0857362 / flux_mean


def avrgMags(group_phot, method):
    """
    Combine magnitudes for all cross-matched stars in all frames. Available
    methods are:

    Parameters
    ----------
    group_phot : dictionary
        See groupFilters().
    method : string
        Selected method to obtain the final magnitudes and sigmas for each
        observed filter.

    Returns
    -------
    avrg_phot : dictionary
        Combined magnitudes for each filter, using the selected method.

    """
    avrg_phot = {}
    for f, fvals in group_phot.iteritems():
        xcen, ycen, mags, emags = [], [], [], []
        for col in fvals.itercols():
            if col.name.startswith('x_'):
                xcen.append(col)
            elif col.name.startswith('y_'):
                ycen.append(col)
            elif col.name.startswith('mag_'):
                mags.append(col)
            elif col.name.startswith('emag_'):
                emags.append(col)

        # Median for (x, y) coordinates.
        xmedian = np.nanmedian(zip(*xcen), axis=1)
        ymedian = np.nanmedian(zip(*ycen), axis=1)
        # Convert magnitudes and their sigmas to flux.
        flux = mag2flux(np.array(mags))
        eflux = emag2eflux(emags, flux)

        if method == 'mean':
            # Convert to flux, average, and back to magnitudes.
            flux_mean = np.nanmean(zip(*flux), axis=1)
            mag_mean = flux2mag(flux_mean)

            # Idem for errors (sigmas)
            # Obtain variances.
            flux_vari = np.array(zip(*np.array(eflux) ** 2))
            # Count non-nan values
            non_nans = (~np.isnan(flux_vari)).sum(1)
            # Replace 0 count with np.nan
            non_nans = np.where(non_nans == 0, np.nan, non_nans)
            # Sigma for the flux mean, obtained as:
            # e_f = sqrt(sum(var ** 2)) / N =
            #     = sqrt(mean(var) / N)
            eflux_mean = np.sqrt(
                (1. / non_nans) * np.nanmean(flux_vari, axis=1))
            # Back to magnitudes.
            emag_mean = eflux2emag(eflux_mean, flux_mean)

        # Add data for this filter.
        avrg_phot.update({f: [xmedian, ymedian, mag_mean, emag_mean]})

    return avrg_phot


def rmNaNrows(tab):
    """
    Remove from 'tab' all those rows that contain only NaN values.

    Parameters
    ----------
    tab : class astropy.table
        All cross-matched stars for a given filter.

    Returns
    -------
    tab : class astropy.table
        Same table minus rows with all NaN values.

    """
    # Convert to pandas dataframe.
    tab_df = tab.to_pandas()
    # Find rows with *all* nan values (~ means 'not'). Leave out the 'ID'
    # column (hence the 'tab.keys()[1:]') else all rows contain at least one
    # non-NaN value.
    nan_idx = ~tab_df[tab.keys()[1:]].isnull().all(1)
    # Filter out all nan rows and transform back to Table.
    tab = Table.from_pandas(tab_df[nan_idx])

    return tab


def standardCalib(avrg_phot):
    """
    """

    return


def writeToFile(in_out_path, group_phot):
    """
    """

    print("\nWriting to 'filter_X.mag' files.")
    for f, tab in group_phot.iteritems():
        # Remove rows with all 'nan' values before writing to file.
        tab = rmNaNrows(tab)
        # Write to file.
        if len(tab) > 0:
            ascii.write(
                tab, in_out_path + '/filter_' + f + '.mag',
                format='fixed_width', delimiter=' ',
                formats={_: '%10.4f' for _ in tab.keys()[1:]},
                fill_values=[(ascii.masked, 'nan')], overwrite=True)


def make_plots(in_out_path):
    """
    """


def main():
    """
    """
    pars, in_out_path = in_params()

    # frames = genData()
    # # Select the 'reference' frame as the one with the largest number of stars,
    # # and store the remaining data in the correct order.
    # refFrameInfo, refFrame, framesOrdered = framesOrder(frames)

    # # Compare the reference frame to all the other frames.
    # for frame in framesOrdered:
    #     print("\n--------------------------------------")
    #     print("Reference frame (N={}), composed of:".format(
    #         np.sum(zip(*refFrameInfo)[2])))
    #     for _ in refFrameInfo:
    #         print("{}, {} (N={})".format(*_))

    #     refFrameInfo, refFrame = frameMatch(
    #         refFrameInfo, refFrame, frame, float(pars['maxrad']))

    # print("\nFinal combined reference frame (N={})".format(
    #     np.sum(zip(*refFrameInfo)[2])))
    # for _ in refFrameInfo:
    #     print("{}, {} (N={})".format(*_))

    # # Group by filters and order by exposure time and data type (x, y, mag,
    # # e_mag).
    # group_phot = groupFilters(refFrameInfo, refFrame)

    import pickle
    # with open('temp.pickle', 'wb') as f:
    #     pickle.dump(group_phot, f)
    with open('temp.pickle', 'rb') as f:
        group_phot = pickle.load(f)

    # Combine magnitudes for each filter, for each exposure time.
    avrg_phot = avrgMags(group_phot, pars['method'])

    # Transform combined magnitudes into the standard system.
    stand_phot = standardCalib(avrg_phot)

    # Create all output files and make final plot.
    writeToFile(in_out_path, group_phot, stand_phot)
    if pars['do_plots_F'] == 'y':
        make_plots(in_out_path)


if __name__ == '__main__':
    main()
