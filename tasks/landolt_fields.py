
from astropy.table import Table


def getTable(data_rows):
    """
    """
    t = Table(
        rows=data_rows,
        names=('ID', 'x', 'y', 'V', 'BV', 'UB', 'VR', 'RI', 'VI', 'eV', 'eBV',
               'eUB', 'eVR', 'eRI', 'eVI'))
    return t


def main(field):
    """
    Dictionary of Landolt standard stars.

    http://www.eso.org/sci/observing/tools/standards/Landolt.html
    """

    #  x  y  V  B-V    U-B    V-R    R-I    V-I   e_V   e_BV   e_UB   e_VR
    # e_RI   e_VI

    data_pg1323 = [
        ('86', 211., 158.3, 13.481, -0.14, -0.681, -0.048, -0.078, -0.127, 0.0019, 0.0022, 0.0026, 0.0018, 0.0045, 0.0045),
        ('86A', 162.5, 137.5, 13.591, 0.393, -0.019, 0.252, 0.252, 0.506, 0.0257, 0.0022, 0.0045, 0.0027, 0.0047, 0.006),
        ('86B', 158.1, 128., 13.406, 0.761, 0.265, 0.426, 0.407, 0.833, 0.0019, 0.0029, 0.0042, 0.0023, 0.0023, 0.0031),
        ('86C', 160.1, 171.2, 14.003, 0.707, 0.245, 0.395, 0.363, 0.759, 0.0031, 0.0028, 0.0077, 0.0024, 0.0041, 0.0049),
        ('86D', 89.6, 133.7, 12.080, 0.587, 0.005, 0.346, 0.335, 0.684, 0.0023, 0.0018, 0.0036, 0.0013, 0.0026, 0.0031)]
    PG1323 = getTable(data_pg1323)

    data_SA98 = [
        ('961', 478.41717069892474, 323.93424479166657, 13.09,  1.283,  1.003,  0.701,  0.662,  1.362,  0.0021, 0.0007, 0.0014, 0.0021, 0,  0.0021),
        ('966', 472.76276881720429, 311.7719464045698,  14, 0.469,  0.357,  0.283,  0.331,  0.613,  0.0035, 0.0014, 0.0021, 0.0014, 0.0191, 0.0205),
        ('556', 465.50806451612902, 180.12040070564512, 14.14,  0.338,  0.126,  0.196,  0.243,  0.437,  0.0053, 0.0053, 0.0131, 0.0057, 0.0045, 0.009),
        ('557', 465.50806451612908, 175.15839633736556, 14.78,  1.397,  1.072,  0.755,  0.741,  1.494,  0.0007, 0.0545, 0.0269, 0.0092, 0.0297, 0.0198),
        ('562', 463.05426747311844, 272.10631720430115, 12.19,  0.522,  -0.002, 0.305,  0.303,  0.607,  0.0028, 0.005,  0.0035, 0.0014, 0.0014, 0),
        ('563', 456.33299731182808, 154.74653897849475, 14.16,  0.416,  -0.19,  0.294,  0.317,  0.61,   0.0051, 0.0085, 0.0073, 0.0044, 0.0079, 0.0082),
        ('978', 454.41263440860234, 389.10069304435484, 10.57,  0.609,  0.094,  0.349,  0.322,  0.671,  0.0015, 0.0009, 0.0016, 0.0007, 0.0009, 0.0012),
        ('L1',  427.634240591398,   153.00114247311825, 15.67,  1.243,  0.776,  0.73,   0.712,  1.445,  0.0075, 0.0462, 0.0976, 0.011,  0.0254, 0.0318),
        ('L2',  423.04670698924724, 225.64953797043006, 15.86,  1.34,   1.497,  0.754,  0.572,  1.327,  0,  0,  0,  0,  0,  0),
        ('581', 423.68682795698919, 167.34198588709677, 14.56,  0.238,  0.161,  0.118,  0.244,  0.361,  0.0246, 0.028,  0.02,   0.0193, 0.0197, 0.0155),
        ('580', 424.75369623655905, 151.33896169354836, 14.73,  0.367,  0.303,  0.241,  0.305,  0.547,  0.0255, 0.0185, 0.0185, 0.0125, 0.046,  0.0395),
        ('L3',  419.09929435483861, 320.87766717069877, 14.61,  1.936,  1.837,  1.091,  1.047,  2.142,  0.0145, 0.0265, 0.145,  0.009,  0.007,  0.011),
        ('L4',  418.99260752688139, 314.07158098118259, 16.33,  1.344,  1.086,  0.936,  0.785,  1.726,  0.058,  0.0325, 0.343,  0.0205, 0.0368, 0.058),
        ('1002', 415.47194220430072, 321.93813424059124, 14.57,  0.574,  -0.027, 0.354,  0.379,  0.733,  0.0055, 0.0065, 0.011,  0.007,  0.0125, 0.013),
        ('590', 413.55157930107475, 221.0844086021504,  14.64,  1.352,  0.853,  0.753,  0.747,  1.5,    0.011,  0.012,  0.0525, 0.005,  0.0105, 0.0135),
        ('614', 392.10752688171988, 249.10196992607518, 15.67,  1.063,  0.399,  0.834,  0.645,  1.48,   0.0424, 0.0474, 0.0311, 0.0226, 0.0368, 0.058),
        ('618', 388.48017473118233, 238.56184475806447, 12.72,  2.192,  2.144,  1.254,  1.151,  2.407,  0.0051, 0.0075, 0.0307, 0.0035, 0.0032, 0.0045),
        ('624', 380.05191532258016, 254.21653645833334, 13.81,  0.791,  0.394,  0.417,  0.404,  0.822,  0.0141, 0.024,  0.0042, 0.0014, 0.0212, 0.0198),
        ('626', 377.49143145161241, 246.74845850134409, 14.76,  1.406,  1.067,  0.806,  0.816,  1.624,  0.0071, 0.0028, 0.0438, 0.0092, 0.0205, 0.0113),
        ('627', 374.61088709677364, 226.92657930107532, 14.9,   0.689,  0.078,  0.428,  0.387,  0.817,  0.0064, 0.017,  0.0085, 0.0007, 0.0127, 0.0127),
        ('634', 364.47563844085971, 243.96393229166682, 14.61,  0.647,  0.123,  0.382,  0.372,  0.757,  0.0042, 0.005,  0.0127, 0.0113, 0.0177, 0.0064),
        ('642', 351.45984543010701, 235.185206653226,   15.29,  0.571,  0.318,  0.302,  0.393,  0.697,  0.0191, 0.0453, 0.012,  0.0198, 0.0021, 0.0177),
        ('185', 338.23067876344032, 144.41018565188187, 10.54,  0.202,  0.113,  0.109,  0.124,  0.231,  0.0018, 0.0009, 0.0033, 0.001,  0.0013, 0.0018),
        ('646', 338.76411290322534, 239.89302965389791, 15.84,  1.06,   1.426,  0.583,  0.504,  1.09,   0,  0,  0,  0,  0,  0),
        ('193', 332.36290322580601, 145.35783140120975, 10.03,  1.18,   1.152,  0.615,  0.537,  1.153,  0.0015, 0.0008, 0.0023, 0.0011, 0.0008, 0.0015),
        ('653', 329.80241935483826, 286.44155955981176, 9.54,   -0.004, -0.099, 0.009,  0.008,  0.017,  0.0014, 0.0004, 0.0009, 0.0007, 0.0007, 0.0011),
        ('650', 330.97597446236512, 265.87714003696237, 12.27,  0.157,  0.11,   0.08,   0.086,  0.166,  0.002,  0.0014, 0.0041, 0.0016, 0.0022, 0.0027),
        ('652', 328.94892473118233, 229.46865969422043, 14.82,  0.611,  0.126,  0.276,  0.339,  0.618,  0.0113, 0.0297, 0.0177, 0.0453, 0.024,  0.0226),
        ('666', 308.35836693548339, 205.00910408266134, 12.73,  0.164,  -0.004, 0.091,  0.108,  0.2,    0.0034, 0.0028, 0.0042, 0.0042, 0.003,  0.0048),
        ('671', 302.49059139784896, 285.78650243615618, 13.39,  0.968,  0.719,  0.575,  0.494,  1.071,  0.0037, 0.0048, 0.0108, 0.0033, 0.0035, 0.0046),
        ('670', 304.03755040322579, 272.4241105930779, 11.93,  1.356,  1.313,  0.723,  0.653,  1.375,  0.0016, 0.0018, 0.0058, 0.0018, 0.0012, 0.0023),
        ('676', 295.47593245967744, 271.7039745043682, 13.07,  1.146,  0.666,  0.683,  0.673,  1.352,  0.0032, 0.0041, 0.0107, 0.0015, 0.0218, 0.0032),
        ('675', 296.22274025537632, 266.47631993447573, 13.4,   1.909,  1.936,  1.082,  1.002,  2.085,  0.0026, 0.0035, 0.0283, 0.0018, 0.0018, 0.0024),
        ('L5',  287.44774865591347, 265.59441994287658, 17.8,   1.9,    -0.1,   3.1,    2.6,    5.8,    0.1633, 0.3266, 0.4491, 0.1225, 0.0408, 0.1225),
        ('682', 284.24714381720378, 266.76797505040349, 13.75,  0.632,  0.098,  0.366,  0.352,  0.717,  0.0039, 0.0039, 0.0064, 0.0017, 0.0025, 0.0039),
        ('685', 276.88575268817152, 256.7394132224465,  11.95,  0.463,  0.096,  0.29,   0.28,   0.57,   0.003,  0.0021, 0.0028, 0.0024, 0.0021, 0.0034),
        ('688', 273.25840053763386, 206.35495841733899, 12.75,  0.293,  0.245,  0.158,  0.18,   0.337,  0.0033, 0.0024, 0.0081, 0.0037, 0.005,  0.0074),
        ('1082', 272.29821908602099, 352.21132182459706, 15.01,  0.835,  -0.001, 0.485,  0.619,  1.102,  0.0058, 0.0139, 0.0225, 0.0029, 0.0133, 0.0162),
        ('1087', 268.03074596774144, 326.49979628696269, 14.44,  1.595,  1.284,  0.928,  0.882,  1.812,  0.004,  0.0142, 0.0592, 0.0035, 0.0049, 0.0072),
        ('1102', 242.21253360215005, 360.95964171707021, 12.11,  0.314,  0.089,  0.193,  0.195,  0.388,  0.0034, 0.0026, 0.0059, 0.0026, 0.0036, 0.0052),
        ('1112', 214.68733198924684, 335.11315734207017, 13.98,  0.814,  0.286,  0.443,  0.431,  0.874,  0.0067, 0.004,  0.0152, 0.0054, 0.0031, 0.0076),
        ('1119', 207.96606182795654, 349.62256594422075, 11.88,  0.551,  0.069,  0.312,  0.299,  0.611,  0.0023, 0.0038, 0.0042, 0.0019, 0.0042, 0.0045),
        ('1124', 201.99159946236517, 317.69493237567235, 13.71,  0.315,  0.258,  0.173,  0.201,  0.373,  0.0035, 0.0043, 0.008,  0.0029, 0.0051, 0.0057),
        ('1122', 203.48521505376311, 310.10949890793057, 14.09,  0.595,  -0.297, 0.376,  0.442,  0.816,  0.0034, 0.006,  0.0074, 0.0038, 0.0028, 0.0046),
        ('724', 204.12533602150506, 274.18217615927466, 11.12,  1.104,  0.904,  0.575,  0.527,  1.103,  0.0035, 0.0035, 0.0052, 0.0023, 0.0023, 0.0038),
        ('733', 193.7767137096771,  307.5468813004037,  12.24,  1.285,  1.087,  0.698,  0.65,   1.347,  0.0034, 0.0043, 0.006,  0.0029, 0.0022, 0.004)]
    SA98 = getTable(data_SA98)

    data_SA95 = [
        ('15', 371.5322580645161, 157.94047799059143, 11.3, 0.712, 0.157, 0.424, 0.385, 0.809, 0.0007, 0.0007, 0.0035, 0.0014, 0.0014, 0.0028),
        ('301', 375.30561155913983, 408.62831653225828, 11.22, 1.29, 1.296, 0.692, 0.62, 1.311, 0.0015, 0.0015, 0.0048, 0.0009, 0.0007, 0.0013),
        ('16', 371.43027553763443, 159.99262138776891, 14.31, 1.306, 1.322, 0.796, 0.676, 1.472, 0.012, 0.016, 0.031, 0.0135, 0.006, 0.009),
        ('302', 372.98550907258067, 408.58255187331997, 11.69, 0.825, 0.447, 0.471, 0.42, 0.891, 0.002, 0.0015, 0.0056, 0.0013, 0.0011, 0.0017),
        ('96', 348.89213709677438, 197.1995440608199, 10.01, 0.147, 0.072, 0.079, 0.095, 0.174, 0.0016, 0.0012, 0.0032, 0.001, 0.0011, 0.0014),
        ('97', 343.181115591398, 193.22222551243283, 14.82, 0.906, 0.38, 0.522, 0.546, 1.068, 0.0007, 0.0226, 0.0212, 0.0028, 0.0191, 0.0212),
        ('98', 338.89784946236574, 214.53657363071238, 14.45, 1.181, 1.092, 0.723, 0.62, 1.342, 0.0007, 0.0014, 0.0177, 0.0092, 0.0071, 0.0163),
        ('100', 337.36811155913995, 197.07053616431455, 15.63, 0.791, 0.051, 0.538, 0.421, 0.961, 0.0283, 0.0785, 0.1132, 0.0144, 0.0572, 0.0439),
        ('101', 331.86105510752702, 215.12144342237906, 12.68, 0.778, 0.263, 0.436, 0.426, 0.863, 0.0028, 0.0028, 0.0099, 0.0064, 0.0064, 0.012),
        ('102', 326.04805107526897, 203.69940041162641, 15.62, 1.001, 0.162, 0.448, 0.618, 1.065, 0.0335, 0.0803, 0.0612, 0.0116, 0.0508, 0.0618),
        ('252', 324.41633064516157, 382.3875749747985, 15.39, 1.452, 1.178, 0.816, 0.747, 1.566, 0.0065, 0.0257, 0.0433, 0.009, 0.0086, 0.0131),
        ('190', 318.19539650537666, 307.34934160786298, 12.63, 0.287, 0.236, 0.195, 0.22, 0.415, 0.002, 0.0017, 0.0039, 0.0017, 0.0015, 0.0021),
        ('193', 306.16145833333366, 309.38899214549741, 14.34, 1.211, 1.239, 0.748, 0.616, 1.366, 0.0049, 0.0063, 0.0255, 0.0043, 0.0034, 0.0058),
        ('105', 302.69405241935516, 193.85757665490604, 13.57, 0.976, 0.627, 0.55, 0.536, 1.088, 0, 0, 0, 0, 0, 0),
        ('107', 295.8612231182799, 211.90848391297055, 16.28, 1.324, 1.115, 0.947, 0.962, 1.907, 0.0035, 0.1068, 0.1732, 0.0438, 0.0226, 0.0212),
        ('106', 296.26915322580675, 205.38160219254047, 15.14, 1.251, 0.369, 0.394, 0.508, 0.903, 0.0064, 0.0615, 0.024, 0.152, 0.0127, 0.1407),
        ('112', 270.67153897849488, 188.51394720262101, 15.5, 0.662, 0.077, 0.605, 0.62, 1.227, 0, 0, 0, 0, 0, 0),
        ('41', 269.03981854838736, 179.43750231014786, 14.06, 0.903, 0.297, 0.589, 0.585, 1.176, 0, 0, 0, 0, 0, 0),
        ('317', 268.22395833333371, 400.3464430023522, 13.45, 1.32, 1.12, 0.768, 0.708, 1.476, 0.0035, 0.0067, 0.0131, 0.0033, 0.0012, 0.0035),
        ('42', 264.14465725806497, 166.56322811659942, 15.61, -0.215, -1.111, -0.119, -0.18, -0.3, 0.0058, 0.0073, 0.0064, 0.0075, 0.0269, 0.0276),
        ('263', 262.51293682795699, 378.83463121639795, 12.68, 1.5, 1.559, 0.801, 0.711, 1.513, 0.003, 0.0034, 0.0094, 0.0023, 0.0012, 0.0028),
        ('115', 257.61777553763449, 191.30355174731187, 14.68, 0.836, 0.096, 0.577, 0.579, 1.157, 0, 0, 0, 0, 0, 0),
        ('43', 256.08803763440869, 176.48905997983871, 10.8, 0.51, -0.016, 0.308, 0.316, 0.624, 0.0023, 0.002, 0.0028, 0.0028, 0.0018, 0.0035),
        ('271', 211.11374327957009, 327.11980174731184, 13.67, 1.287, 0.916, 0.734, 0.717, 1.453, 0.0057, 0.008, 0.0127, 0.0023, 0.0023, 0.0036),
        ('328', 208.66616263440892, 447.37198840725824, 13.53, 1.532, 1.298, 0.908, 0.868, 1.776, 0.0029, 0.0054, 0.0186, 0.0027, 0.0015, 0.0031),
        ('329', 200.91549059139814, 451.75723706317223, 14.62, 1.184, 1.093, 0.766, 0.642, 1.41, 0.0047, 0.0103, 0.0311, 0.0044, 0.0094, 0.0089),
        ('330', 188.47362231182825, 396.8906376008066, 12.17, 1.999, 2.233, 1.166, 1.1, 2.268, 0.0025, 0.0026, 0.0137, 0.002, 0.0016, 0.0028),
        ('275', 165.6295362903229, 385.84949932795712, 13.48, 1.763, 1.74, 1.011, 0.931, 1.944, 0.0029, 0.0054, 0.0201, 0.0022, 0.0016, 0.0025),
        ('276', 162.57006048387129, 376.05917674731199, 14.12, 1.225, 1.218, 0.748, 0.646, 1.395, 0.0062, 0.0102, 0.0217, 0.004, 0.0032, 0.0051),
        ('60', 151.96387768817243, 150.3866322244624, 13.43, 0.776, 0.197, 0.464, 0.449, 0.914, 0.0031, 0.0031, 0.006, 0.0029, 0.0025, 0.0034),
        ('218', 152.77973790322619, 269.31916498655926, 12.1, 0.708, 0.208, 0.397, 0.37, 0.767, 0.0034, 0.0022, 0.0034, 0.002, 0.002, 0.0027),
        ('132', 149.210349462366, 235.94385332661301, 12.06, 0.448, 0.3, 0.259, 0.287, 0.545, 0.0023, 0.0021, 0.0057, 0.0016, 0.0017, 0.0026),
        ('62', 133.60702284946277, 179.82643817204303, 13.54, 1.355, 1.181, 0.742, 0.685, 1.428, 0.003, 0.0053, 0.0136, 0.0019, 0.0019, 0.0028),
        ('137', 127.99798387096817, 223.61340095766133, 14.44, 1.457, 1.136, 0.893, 0.845, 1.737, 0, 0, 0, 0, 0, 0),
        ('139', 126.4172547043015, 221.47176789314517, 12.2, 0.923, 0.677, 0.562, 0.476, 1.039, 0.0017, 0.0046, 0.0191, 0.0023, 0.0017, 0.0035),
        ('66', 122.43993615591442, 134.53905745967734, 12.89, 0.715, 0.167, 0.426, 0.438, 0.864, 0.0021, 0.0071, 0.0035, 0.0007, 0.0057, 0.005),
        ('227', 121.31812836021554, 300.16607484879034, 15.78, 0.771, 0.034, 0.515, 0.552, 1.067, 0.0118, 0.0289, 0.0417, 0.0115, 0.0107, 0.015),
        ('142', 118.56460013440919, 209.14794438844086, 12.93, 0.588, 0.097, 0.371, 0.375, 0.745, 0.003, 0.003, 0.0036, 0.0019, 0.0017, 0.0028),
        ('74', 80.423135080645778, 137.51363281249991, 11.53, 1.126, 0.686, 0.6, 0.567, 1.165, 0.0016, 0.0013, 0.0035, 0.0013, 0.001, 0.0013),
        ('231', 69.205057123656559, 274.59293640792987, 14.22, 0.452, 0.297, 0.27, 0.29, 0.56, 0.0043, 0.0045, 0.0071, 0.0045, 0.0053, 0.0077),
        ('284', 67.267389112903899, 383.02126890120945, 13.67, 1.398, 1.073, 0.818, 0.766, 1.586, 0.004, 0.0078, 0.0239, 0.0027, 0.0036, 0.0049),
        ('149', 59.312752016129728, 249.71251428091364, 10.94, 1.593, 1.564, 0.874, 0.811, 1.685, 0.0051, 0.0039, 0.0095, 0.0024, 0.0017, 0.0029),
        ('285', 63.035114247312563, 373.42471312163957, 15.56, 0.937, 0.703, 0.607, 0.602, 1.21, 0.0071, 0.0255, 0.0636, 0.0071, 0.0064, 0.0134),
        ('236', 10.106182795699743, 262.41800739247287, 11.49, 0.736, 0.162, 0.42, 0.411, 0.831, 0.001, 0.0014, 0.0036, 0.0012, 0.0009, 0.0015)]
    SA95 = getTable(data_SA95)

    data_tphe = [
        ('A', 322.53944052419467, 111.76489478326656, 14.65, 0.793, 0.38, 0.435, 0.405, 0.841, 0.0028, 0.0046, 0.0071, 0.0019, 0.0035, 0.0032),
        ('B', 301.45749327957128, 180.15218245967779, 12.33, 0.405, 0.156, 0.262, 0.271, 0.535, 0.0115, 0.0026, 0.0039, 0.002, 0.0019, 0.0035),
        ('C', 297.99655577957105, 95.542122395833729, 14.38, -0.298, -1.217, -0.148, -0.211, -0.36, 0.0022, 0.0024, 0.0043, 0.0038, 0.0133, 0.0149),
        ('D', 293.56804435483991, 115.45451465893854, 13.12, 1.551, 1.871, 0.849, 0.81, 1.663, 0.0033, 0.003, 0.0118, 0.0015, 0.0023, 0.003),
        ('E', 291.07468077957157, 245.57106497815909, 11.63, 0.443, -0.103, 0.276, 0.283, 0.564, 0.0017, 0.0012, 0.0024, 0.0007, 0.0015, 0.0019),
        ('F', 189.31195396505387, 77.464957367271609, 12.47, 0.855, 0.532, 0.492, 0.435, 0.926, 0.0005, 0.0058, 0.0161, 0.0005, 0.004, 0.0036),
        ('G', 143.24054939516193, 281.38237147177455, 10.44, 1.546, 1.915, 0.934, 1.085, 2.025, 0.0005, 0.0013, 0.0036, 0.0005, 0.0009, 0.0009)]
    TPHE = getTable(data_tphe)

    # # Check that stars are properly placed over the field
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # ax.imshow(plt.imread("landolt/" + field + ".gif"))
    # max_y = ax.get_ylim()[0]
    # ax.scatter(TPHE['x'], max_y - TPHE['y'])
    # plt.show()

    all_fields = {'PG1323': PG1323, 'SA98': SA98, 'SA95': SA95, 'TPHE': TPHE}

    return all_fields[field]


if __name__ == '__main__':
    """
    Use the commented code to print the (x,y) coordinates of standard stars
    to screen on mouse click.
    """

    field = 'SA98'

    # Load Landolt standard file. Notice that y axis is inverted.
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(plt.imread("landolt/" + field + ".gif"))

    max_y = ax.get_ylim()[0]

    def onclick(event):
        if event.button == 1:
            # Write to figure
            circ = plt.Circle(
                (event.xdata, event.ydata), radius=1, color='g')
            ax.add_patch(circ)
            ax.figure.canvas.draw()
            print(event.xdata, max_y - event.ydata)
        else:
            pass

    def zoom_fun(event):
        """
        https://gist.github.com/tacaswell/3144287
        """
        base_scale = 2.
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        # set the range
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print event.button
        # set new limits
        ax.set_xlim([xdata - cur_xrange*scale_factor,
                     xdata + cur_xrange*scale_factor])
        ax.set_ylim([ydata - cur_yrange*scale_factor,
                     ydata + cur_yrange*scale_factor])
        ax.figure.canvas.draw() # force re-draw

    # attach the call back
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    main(field)
