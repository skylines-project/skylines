'''
The geoid library was adopted by Tobias Lohner from RTKLIB under the
following license:


The RTKLIB software package is distributed under the following BSD 2-clause
license (http://opensource.org/licenses/BSD-2-Clause) and additional two
exclusive clauses. Users are permitted to develop, produce or sell their own
non-commercial or commercial products utilizing, linking or including RTKLIB as
long as they comply with the license.

          Copyright (c) 2007-2013, T. Takasu, All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

- The software package includes some companion executive binaries or shared
  libraries necessary to execute APs on Windows. These licenses succeed to the
  original ones of these software.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import csv
import os


'''
geoid model
notes  : geoid heights are derived from EGM96 (1 x 1 deg grid)
'''
geoid_egm96 = None


def egm96_height(location):
    '''
    Calculate the geoid height from the egm96 1" x 1" grid geoid
    '''

    if geoid_egm96 is None:
        return 0

    a = location.longitude
    b = location.latitude + 90.0

    i1 = int(a)
    a -= i1
    i2 = i1 + 1 if i1 < 360 else i1

    j1 = int(b)
    b -= j1
    j2 = j1 + 1 if j1 < 180 else j1

    y = [geoid_egm96[i1][j1],
         geoid_egm96[i2][j1],
         geoid_egm96[i1][j2],
         geoid_egm96[i2][j2]]

    # bilinear interpolation
    return y[0] * (1.0 - a) * (1.0 - b) + \
        y[1] * a * (1.0 - b) + \
        y[2] * (1.0 - a) * b + \
        y[3] * a * b


def load_geoid(app):
    global geoid_egm96
    geoid_file = os.path.join(app.config.get('SKYLINES_BACKEND_PATH'),
                              'geoid_egm96.csv')

    with open(geoid_file, 'rb') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        geoid_egm96 = list(reader)
