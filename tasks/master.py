
import read_pars_file as rpf

from os.path import join, isfile
import sys
import operator
import numpy as np
from scipy.spatial import cKDTree
from astropy.io import ascii
from astropy.table import Table
from astropy.table import Column

import matplotlib.pyplot as plt
import time as t


def in_params():
    """
    Read and prepare input parameter values.

    TODO
    Returns
    -------
    pars : dictionary
        All parameters.
    """
    pars = rpf.main()

    pars['in_out_path'] = pars['mypath'].replace(
        'tasks', 'output/' + pars['master_folder'])

    # Format parameters appropriately.
    if pars['load_format'][0][0] == 'allstar':
        f = join(pars['in_out_path'], pars['load_format'][0][1])
        if isfile(f):
            pars['load_format'] = 'allstar'
            pars['als_files'] = f

            # Check that all .als files exist.
            for file in ascii.read(f).columns[0]:
                f = join(pars['in_out_path'], file)
                if not isfile(f):
                    print("{}\n file does not exist. Exit.".format(f))
                    sys.exit()
        else:
            print("{}\n file does not exist. Exit.".format(f))
            sys.exit()
    else:
        pars['load_format'], pars['als_files'] = 'default', ''

    return pars


def loadFrames(in_out_path, load_format, als_files):
    """
    Load photometric lists of stars.

    Parameters
    ----------
    in_out_path : string
        Path to the folder where input photometric files exist, and where the
        output files generated by this script will be stored.
    load_format : string
       Selected format for the photometry files.
    extCoeffs : list
        Extinction coefficients for each observed filter.

    Returns
    -------
    frames : dictionary
        Contains x,y coordinates, magnitudes and their errors, for each
        observed frame (all filters, all exposure times).

    """

    frames = {'U': {}, 'B': {}, 'V': {}, 'I': {}, 'R': {}}
    xy_shifts = {'U': {}, 'B': {}, 'V': {}, 'I': {}, 'R': {}}

    if load_format == 'allstar':
        files_data = ascii.read(als_files)

        for fname, filt, expT, K, x0, y0 in files_data:
            # if filt == 'U':  # TODO: remove this
            als = ascii.read(in_out_path + '/' + fname, format='daophot')
            # DELETE
            # # Used to align .als test files.
            # if filt == 'V' and str(expT) == '300':
            #     dx, dy = [13., -7.]
            # elif filt == 'V' and str(expT) == '30':
            #     dx, dy = [7., -8.]
            # elif filt == 'V' and str(expT) == '3':
            #     dx, dy = [10., -9.]
            # elif filt == 'B' and str(expT) == '300':
            #     dx, dy = [6., -7.]
            # elif filt == 'B' and str(expT) == '30':
            #     dx, dy = [0., -5.]
            # elif filt == 'U' and str(expT) == '300':
            #     dx, dy = [4., 2.]
            # elif filt == 'U' and str(expT) == '30':
            #     dx, dy = [6.5, 0.]
            # else:
            #     dx, dy = [0., 0.]
            # frames[filt].update(
            #     {str(expT): [als['XCENTER'] + dx, als['YCENTER'] + dy, zAmag,
            #      als['MERR']]})
            # DELETE
            frames[filt].update(
                {str(expT): [als['XCENTER'], als['YCENTER'], als['MAG'],
                 als['MERR']]})
            xy_shifts[filt].update({str(expT): (float(x0), float(y0))})

            print("Loaded: {}, ({}, {}) N={}".format(
                fname, filt, expT, len(frames[filt][str(expT)][0])))
    elif load_format == 'default':
        # TODO: write code.
        pass

    return frames, xy_shifts


def framesOrder(frames):
    """
    TODO: allow selecting the reference frame manually.

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


def transfABCD(x, y, ABCD):
    """
    Apply transformation equations to obtain new (xt, yt) coordinates.
    """
    A, B, C, D = ABCD
    xt = A + x * C + y * D
    yt = B + y * C + x * D

    return xt, yt


def solveABCD(x1, y1, x2, y2):
    """
    Obtain new A, B, C, D parameters, solving the linear equations:

    1*A + 0*B + x2*C + y2*D = x1
    0*A + 1*B + y2*C + x2*D = y1
    """
    N = len(x1)
    l1 = np.array([np.ones(N), np.zeros(N), x2, y2])
    l2 = np.array([np.zeros(N), np.ones(N), y2, x2])
    M1 = np.vstack([l1.T, l2.T])
    M2 = np.concatenate([x1, y1])
    A, B, C, D = np.linalg.lstsq(M1, M2)[0]
    print("New A,B,C,D parameters: "
          "({:.3f}, {:.3f}, {:.3f}, {:.3f})".format(A, B, C, D))

    return A, B, C, D


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
        * fr2[min_dist_idx[i]]: closest star in fr2 to the ith star in fr1.
        Also the index of the minimum distance in dist[i], i.e.: distance to
        the closest processed star to the ith reference star:
        * dist[i][min_dist_idx[i]]: distance between these two stars.
    min_dists : list
        Minimum distance for each star in the reference frame to a star in the
        processed frame.

    Notes
    -----
    len(fr1) = len(dist) = len(min_dist_idx)

    """
    fr1 = np.array(zip(*[x_fr1, y_fr1]))
    fr2 = np.array(zip(*[x_fr2, y_fr2]))
    min_dists, min_dist_idx = cKDTree(fr2).query(fr1, 1)

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
    maxrad : int
        see frameCombine()

    Returns
    -------
    N_dupl_c1 : int
        Number of reference stars that were matched to the same processed star
        as another reference star. These stars will be re-processed.
    match_c1_ids : list
        IDs in reference frame for unique matches between frames.
    match_c2_ids : list
        IDs in the processed frame for unique matches between frames.
    no_match_c1 : list
        IDs of reference stars with no match found within maxrad.

    """

    N_dupl_c1, match_c1_ids, match_c2_ids, match_d = 0, [], [], []
    # Indexes of matched star in both frames and distance between them.
    for c1_i, c2_i, d in zip(*[c1_ids, c2_ids, d2d]):
        # Filter by maximum allowed match distance.
        if d <= float(maxrad):
            # Check if this processed star was already stored as a match with
            # another reference star.
            if c2_i in match_c2_ids:
                # Update number of duplicated reference stars.
                N_dupl_c1 += 1
                # Index of this stored c2 star.
                j = match_c2_ids.index(c2_i)
                # If the previous match had a larger distance than this match,
                # replace with this match.
                if match_d[j] > d:
                    # Now replace this reference star.
                    match_c1_ids[j] = c1_i
                    match_d[j] = d
            else:
                # Store IDs of both matched stars, and their distance.
                match_c1_ids.append(c1_i)
                match_c2_ids.append(c2_i)
                match_d.append(d)
        # else:
            # This reference star has no processed star closer than the max
            # distance allowed.

    return N_dupl_c1, match_c1_ids, match_c2_ids, match_d


def frameCoordsUpdt(x_ref, y_ref, x_fr, y_fr, match_fr1_ids, match_fr2_ids):
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
    x_fr_updt[match_fr2_ids] = 1000000.
    y_fr_updt[match_fr2_ids] = 1000000.

    x_ref_updt, y_ref_updt = np.copy(x_ref), np.copy(y_ref)
    x_ref_updt[match_fr1_ids] = -1000000.
    y_ref_updt[match_fr1_ids] = -1000000.

    return x_ref_updt, y_ref_updt, x_fr_updt, y_fr_updt


def frameMatch(x_ref, y_ref, x_fr, y_fr, maxrad):
    """
    Match stars in the reference frame (x_ref, y_ref) with those from the
    processed frame (x_fr, y_fr), rejecting matches with distances beyond
    'maxrad'.

    Parameters
    ----------
    x_ref, y_ref : list
        x,y coordinates for stars in the reference frame.
    x_fr, y_fr : list
        x,y coordinates for stars in the processed frame.
    maxrad : int
        see frameCombine()

    Returns
    -------
    match_fr1_ids_all : list
        Indexes of stars in the reference frame that match stars in the
        processed frame.
    match_fr2_ids_all : list
        Indexes of stars in the processed frame that match stars in the
        reference frame.

    Notes
    -----
        x_ref[match_fr1_ids_all] == x_fr[match_fr2_ids_all]
        y_ref[match_fr1_ids_all] == y_fr[match_fr2_ids_all]
    """

    # Initial full list of IDs for the reference and processed frame.
    fr1_ids = np.arange(len(x_ref)).tolist()
    N_fr2 = len(x_fr)

    match_fr1_ids_all, match_fr2_ids_all, match_d_all = [], [], []
    # Continue until no more duplicate matches exist.
    counter, N_dupl_fr1 = 1, 1
    while N_dupl_fr1 > 0:

        # Find closest stars between reference and processed frame.
        s = t.clock()
        fr2_ids_2fr1, fr1fr2_d2d = closestStar(x_ref, y_ref, x_fr, y_fr)
        print(' 1', t.clock() - s)

        # Match reference and processed frame.
        s = t.clock()
        N_dupl_fr1, match_fr1_ids, match_fr2_ids, match_d = starMatch(
            fr1_ids, fr2_ids_2fr1, fr1fr2_d2d, maxrad)
        print(' 2', t.clock() - s)
        # Store unique matches and distances.
        match_fr1_ids_all += match_fr1_ids
        match_fr2_ids_all += match_fr2_ids
        match_d_all += match_d

        # x1, y1 = x_ref[match_fr1_ids], y_ref[match_fr1_ids]
        # x2, y2 = x_fr[match_fr2_ids], y_fr[match_fr2_ids]
        # plt.subplot(131)
        # plt.scatter(x_ref, y_ref, c='g', s=2, zorder=1)
        # plt.scatter(x_fr, y_fr, c='r', s=5, zorder=4)
        # plt.xlim(0., 4100.)
        # plt.ylim(0., 4100.)
        # plt.subplot(132)
        # plt.scatter(x1, y1, c='g', s=2, zorder=1)
        # plt.scatter(x2, y2, c='r', s=5, zorder=4)
        # plt.subplot(133)
        # plt.scatter(x1, x1 - x2, c='b', s=5)
        # plt.scatter(y1, y1 - y2, c='r', s=5)
        # plt.show()

        print("{}.".format(counter))
        counter += 1

        s = t.clock()
        print(" Cross-matched stars: {}".format(len(match_fr1_ids)))
        if match_fr1_ids:
            print(" (Mean cross-match distance: {:.2f} px)".format(
                np.mean(match_d_all)))
        print(" Reference stars w/ no match within maxrad: {}".format(
            len(x_ref) - len(match_fr1_ids_all) - N_dupl_fr1))

        # If there are any stars from the reference frame that had
        # duplicated matches and were stored for re-matching.
        if N_dupl_fr1 > 0:
            print(" Reference stars for re-match: {}".format(N_dupl_fr1))
            print(" Frame stars for re-match: {}".format(
                N_fr2 - len(match_fr2_ids_all)))
            # Update coordinates of matched stars in both frames.
            x_ref, y_ref, x_fr, y_fr = frameCoordsUpdt(
                x_ref, y_ref, x_fr, y_fr, match_fr1_ids, match_fr2_ids)
        else:
            print(" Frame stars w/ no match within maxrad: {}".format(
                N_fr2 - len(match_fr2_ids_all)))

        print(' 1', t.clock() - s)

    return match_fr1_ids_all, match_fr2_ids_all


def UpdtRefFrame(
    refFrameInfo, refFrame, frame, match_fr1_ids_all, match_fr2_ids_all, ABCD):
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
        see frameMatch()
    refFrame : list
        see frameMatch()
    frame : list
        see frameMatch()
    match_fr1_ids_all : list
        Indexes of stars in refFrame that were matched to a star in frame.
    match_fr2_ids_all : list
        Indexes of stars in frame that were matched to a star in refFrame.
    ABCD: tuple of floats
        Transformation parameters for the frame's coordinates(A, B, C, D)

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
    # Update x,y coordinates before storing.
    x_fr, y_fr = transfABCD(x_fr, y_fr, ABCD)

    # For each reference frame star.
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

    # Number of frames processed this far including the reference frame, but
    # excluding this one.
    N_fr = len(refFrame[0][0]) - 1

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

    # Update the information stored on the frames processed.
    refFrameInfo.append([fr_filt, fr_expTime, fr_st_no_match])

    return refFrameInfo, refFrame


def frameCombine(refFrameInfo, refFrame, frame, xy_shifts, maxrad):
    """
    Combine 'refFrame' and 'frame' to generate an updated 'refFrame'
    with all matches and non-matches identified and stored.

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
    xy_shifts: dict
        Contains the x0,y0 shifts for each frame.
    maxrad : int
        Maximum allowed distance (radius) for a match to be valid.

    Returns
    -------
    refFrameInfo : list
        Updated list.
    refFrame : list
        Updated list.
    """

    # Extract (x,y) coordinates, averaging the values assigned to the
    # same star. Use np.nanmean() because stars from 'refFrame' that could not
    # be matched to a star in 'frame', will have a 'NaN' value attached to
    # its x,y coordinates lists.
    x_ref, y_ref = [], []  # TODO improve this block
    for st in refFrame:
        x_ref.append(np.nanmean(st[0]))
        y_ref.append(np.nanmean(st[1]))
    x_ref, y_ref = np.array(x_ref), np.array(y_ref)

    # Extract filter name and exposure time of the processed frame.
    fr_filt, fr_expTime = frame[:2]
    # x,y coordinates and their shifts
    x_fr, y_fr = frame[2][:2]
    x0, y0 = xy_shifts[fr_filt][fr_expTime]
    print('\nProcessing frame: {}, {} (N={})'.format(
        fr_filt, fr_expTime, len(x_fr)))

    A, B, C, D = x0, y0, 1., 0.
    print("Initial A,B,C,D parameters: ({}, {}, {}, {})".format(A, B, C, D))

    min_rad, mstep = 3., -1
    # if fr_filt == 'I':  # TODO remove this
    #     maxrad, min_rad = 20., 15.

    rads_list = np.arange(maxrad, min_rad - 1., mstep)
    print("Minimum match radius: {}".format(min_rad))

    for m_rad in rads_list:
        print("Match using maxrad={}".format(m_rad))

        # Apply transformation equations
        s = t.clock()
        xt, yt = transfABCD(x_fr, y_fr, (A, B, C, D))
        print('1', t.clock() - s)

        # Match frames
        match_fr1_ids_all, match_fr2_ids_all = frameMatch(
            x_ref, y_ref, xt, yt, float(m_rad))

        # Solve for new A,B,C,D using only the cross-matched stars, only if
        # the loop while run one more time.
        if m_rad != rads_list[-1]:
            s = t.clock()
            x1 = np.array(x_ref)[match_fr1_ids_all]
            y1 = np.array(y_ref)[match_fr1_ids_all]
            x2, y2 = x_fr[match_fr2_ids_all], y_fr[match_fr2_ids_all]
            A, B, C, D = solveABCD(x1, y1, x2, y2)
            x_med, y_med = np.median(x1 - x2), np.median(y1 - y2)
            print(x_med, y_med)
            print('3', t.clock() - s)

    # Update reference frame.
    print("Updating reference frame.")
    refFrameInfo, refFrame = UpdtRefFrame(
        refFrameInfo, refFrame, frame, match_fr1_ids_all, match_fr2_ids_all,
        (A, B, C, D))

    return refFrameInfo, refFrame


def groupFilters(refFrameInfo, refFrame):
    """
    Group observed frames according to filters and exposure times.

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
            ids = Column(np.arange(len(tab)), name='ID')
            tab.add_column(ids, index=0)
            # Append to grouped dictionary.
            group_phot.update({f: tab})

    return group_phot


def writeToFile(in_out_path, group_phot):
    """
    TODO
    """
    for f, tab in group_phot.iteritems():
        print("\nWriting 'filter_{}.mag' file.".format(f))
        # Remove rows with all 'nan' values before writing to file.
        # tab = rmNaNrows(tab, 1)
        # Write to file.
        if len(tab) > 0:
            ascii.write(
                tab, in_out_path + '/filter_' + f + '.mag',
                format='fixed_width', delimiter=' ',
                formats={_: '%10.4f' for _ in tab.keys()[1:]},
                fill_values=[(ascii.masked, 'nan')], overwrite=True)


def make_plots(in_out_path):
    """
    TODO
    """


def main():
    """
    TODO
    """
    pars = in_params()

    frames, xy_shifts = loadFrames(
        pars['in_out_path'], pars['load_format'], pars['als_files'])

    # Select the 'reference' frame as the one with the largest number of stars,
    # and store the remaining data in the correct order.
    refFrameInfo, refFrame, framesOrdered = framesOrder(frames)

    # Compare the reference frame to all the other frames.
    for frame in framesOrdered:
        print("\n--------------------------------------")
        print("Reference frame (N={}), composed of:".format(
            np.sum(zip(*refFrameInfo)[2])))
        for _ in refFrameInfo:
            print("{}, {} (N={})".format(*_))

        if frame[0] == 'I':  # TODO remove
            refFrameInfo, refFrame = frameCombine(
                refFrameInfo, refFrame, frame, xy_shifts,
                int(float(pars['maxrad'])))

    print("\nFinal combined reference frame (N={})".format(
        np.sum(zip(*refFrameInfo)[2])))
    for _ in refFrameInfo:
        print("{}, {} (N added: {})".format(*_))

    # Group by filters and order by exposure time and data type (x, y, mag,
    # e_mag).
    group_phot = groupFilters(refFrameInfo, refFrame)

    # Create all output files and make final plot.
    writeToFile(pars['in_out_path'], group_phot)
    if pars['do_plots_H'] == 'y':
        make_plots(pars['in_out_path'])


if __name__ == '__main__':
    main()
