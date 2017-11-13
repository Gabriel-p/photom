
import read_pars_file as rpf

import os
from os.path import join, isfile
import sys
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# from matplotlib.offsetbox import AnchoredText

import astropy.units as u
from astropy.io import ascii, fits
from astropy.table import Table, vstack

from photutils import CircularAperture
from photutils import CircularAnnulus
from photutils import aperture_photometry


def in_params():
    """
    Read and prepare input parameter values.
    """
    pars = rpf.main()

    in_out_path = pars['mypath'].replace('tasks', 'output/standards')

    fits_list = []
    for file in os.listdir(in_out_path):
        f = join(in_out_path, file)
        if isfile(f):
            if f.endswith('_crop.fits'):
                fits_list.append(f)

    if not fits_list:
        print("No '*_crop.fits' files found in 'output/standards' folder."
              " Exit.")
        sys.exit()

    return pars, in_out_path


def read_standard_coo(in_out_path, landolt_fld):
    """
    Read _obs.coo file created by 'id_standards', with calibrated photometric
    data on Landolt standard stars, and their coordinates in the system of
    the observed frame.
    """
    f = join(in_out_path, landolt_fld + '_obs.coo')
    landolt_fl = ascii.read(f)

    return landolt_fl


def standardMagCol(landolt_fl, filt):
    """
    Separate into individual filters. Return single filter, and color term
    used in the fitting process for that filter.
    """
    if filt == 'U':
        standard_mag = landolt_fl['UB'] + landolt_fl['BV'] + landolt_fl['V']
        standard_col = landolt_fl['UB']
    elif filt == 'B':
        standard_mag = landolt_fl['BV'] + landolt_fl['V']
        standard_col = landolt_fl['BV']
    elif filt == 'V':
        standard_mag = landolt_fl['V']
        standard_col = landolt_fl['BV']
    elif filt == 'R':
        standard_mag = landolt_fl['V'] - landolt_fl['VR']
        standard_col = landolt_fl['VR']
    elif filt == 'I':
        standard_mag = landolt_fl['V'] - landolt_fl['VI']
        standard_col = landolt_fl['VI']

    return list(standard_mag), list(standard_col)


def calibrate_magnitudes(tab, itime=1., zmag=25.):
    tab['cal_mags'] = (zmag - 2.5 * np.log10(tab['flux_fit'] / itime)) * u.mag
    return tab


def instrumMags(landolt_fl, hdu_data, exp_time, aper_rad, annulus_in,
                annulus_out):
    """
    Perform aperture photometry for all 'landolt_fl' standard stars observed in
    the 'hdu_data' file.
    """
    # Coordinates from observed frame.
    positions = zip(*[landolt_fl['x_obs'], landolt_fl['y_obs']])
    apertures = CircularAperture(positions, r=aper_rad)
    annulus_apertures = CircularAnnulus(
        positions, r_in=annulus_in, r_out=annulus_out)

    apers = [apertures, annulus_apertures]
    # TODO obtain errors for aperture photometry.

    # from astropy.stats import SigmaClip
    from photutils import Background2D  # , MedianBackground
    # sigma_clip = SigmaClip(sigma=3., iters=10)
    # bkg_estimator = MedianBackground()

    # Selecting the box size requires some care by the user. The box size
    # should generally be larger than the typical size of sources in the
    # image, but small enough to encapsulate any background variations. For
    # best results, the box size should also be chosen so that the data are
    # covered by an integer number of boxes in both dimensions.
    bl = 10
    box_xy = (bl, bl)
    bkg = Background2D(hdu_data, box_xy)
    print("background estimated")

    from photutils.utils import calc_total_error
    effective_gain = 1.1
    error = calc_total_error(hdu_data, bkg.background, effective_gain)
    phot_table = aperture_photometry(hdu_data, apers, error=error)

    # phot_table = aperture_photometry(hdu_data, apers)
    bkg_mean = phot_table['aperture_sum_1'] / annulus_apertures.area()
    bkg_sum = bkg_mean * apertures.area()
    phot_table['flux_fit'] = phot_table['aperture_sum_0'] - bkg_sum
    phot_table = calibrate_magnitudes(phot_table, itime=exp_time)

    phot_table['merr'] = 1.0857 *\
        phot_table['aperture_sum_err_0'] / phot_table['flux_fit']

    # # plt.subplot(131)
    # # median, std = np.median(hdu_data), np.std(hdu_data)
    # # plt.imshow(hdu_data, origin='lower', cmap='Greys_r', vmin=0.,
    # #            vmax=median + std)
    # plt.figure(figsize=(15, 15))
    # plt.subplot(121)
    # plt.title("Background, box_size=({}, {})".format(bl, bl))
    # plt.imshow(bkg.background, origin='lower', cmap='Greys_r')
    # plt.subplot(122)
    # plt.title("Data - background")
    # hdu_bckg = hdu_data - bkg.background
    # median, std = np.median(hdu_bckg), np.std(hdu_bckg)
    # plt.imshow(hdu_bckg, origin='lower',
    #            cmap='Greys_r', vmin=0., vmax=median + std)
    # # plt.show()
    # plt.savefig(str(bl) + '.png', dpi=150, bbox_inches='tight')


    return phot_table


def zeroAirmass(phot_table, extin_coeffs, filt, airmass):
    """
    Correct for airmass, i.e. instrumental magnitude at zero airmass.
    """
    # Identify correct index for this filter's extinction coefficient.
    f_idx = extin_coeffs.index(filt) + 1
    # Extinction coefficient.
    ext = float(extin_coeffs[f_idx])
    # Obtain zero airmass instrumental magnitude for this filter.
    phot_table['instZA'] = phot_table['cal_mags'] - (ext * airmass) * u.mag

    return phot_table


def writeAperPhot(in_out_path, filters):
    """
    """
    tables = []
    for v in filters.values():
        tables.append(Table(zip(*v)))
    aper_phot = Table(
        vstack(tables),
        names=('Filt', 'Stnd_field', 'ID', 'file', 'exp_t', 'A', 'ZA_mag',
               'Col', 'Mag'))

    ascii.write(
        aper_phot, in_out_path + '/stnd_aperphot.dat',
        format='fixed_width', delimiter=' ', formats={'ZA_mag': '%10.4f'},
        fill_values=[(ascii.masked, 'nan')], overwrite=True)


def main():
    """
    Performs aperture photometry on selected standard fields.

    Requires the '_obs.coo' file generated by the 'id_standards' script.

    Returns zero airmass corrected instrumental magnitudes for each filter.
    """
    pars, in_out_path = in_params()

    filters = {'U': [], 'B': [], 'V': [], 'R': [], 'I': []}

    for stnd_fl in pars['stnd_obs_fields']:
        stnd_f_name, fits_list = stnd_fl[0], stnd_fl[1:]
        print("\nPerform aperture photometry and resolve transformation\n"
              "equations for standard field {}.".format(stnd_f_name))
        # Data for this Landolt field from stnd_f_name'_obs.coo' file.
        landolt_fl = read_standard_coo(in_out_path, stnd_f_name)

        # For each observed (aligned and cropped) .fits standard file.
        for imname in fits_list:

            print("Perform aperture photometry on {} file.".format(imname))

            # Load .fits file.
            hdulist = fits.open(join(in_out_path, imname))
            # Extract header and data.
            hdr, hdu_data = hdulist[0].header, hdulist[0].data
            filt, exp_time, airmass = hdr[pars['filter_key']],\
                hdr[pars['exposure_key']], hdr[pars['airmass_key']]
            print("  Filter {}, Exp time {}, Airmass {}".format(
                filt, exp_time, airmass))

            # Obtain instrumental magnitudes for the standard stars in the
            # defined Landolt field, in this observed frame.
            photu = instrumMags(
                landolt_fl, hdu_data, exp_time, float(pars['aperture']),
                float(pars['annulus_in']), float(pars['annulus_out']))

            print("  Correct instrumental magnitudes for zero airmass.")
            photu = zeroAirmass(photu, pars['extin_coeffs'][0], filt, airmass)

            # Extract data for this filter, from '_obs.coo' file.
            stand_mag, stand_col = standardMagCol(landolt_fl, filt)
            # Group frames by filter.
            # Filt  Stnd_field ID  file  exp_t  A  ZA_mag  Col  Mag
            for i, ID in enumerate(landolt_fl['ID']):
                filters[filt].append(
                    [filt, stnd_f_name, ID, imname, str(exp_time), airmass,
                     photu['instZA'][i].value, stand_col[i], stand_mag[i]])

    # Remove not observed filters from dictionary.
    filters = {k: v for k, v in filters.iteritems() if v}
    if 'V' not in filters.keys():
        print("  WARNING: Filter V is missing.")
        if 'B' not in filters.keys():
            print("  WARNING: Filter B is missing.")

    print("\nWrite final aperture photometry to output file.")
    writeAperPhot(in_out_path, filters)


if __name__ == '__main__':
    main()
