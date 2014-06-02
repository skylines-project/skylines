from flask.ext.script import Command, Option

from skylines.model import db, Boundaries
from geoalchemy2.shape import from_shape
import shapely


class BoundariesCommand(Command):
    """ Import world boundaries and import them into the database """

    option_list = (
        Option('shapefile', nargs='?', metavar='ne_10m_admin_0_countries.shp',
               help='Boundaries Shapefile from naturalearthdata.com, Admin 0 - Countries'),
        Option('--verbose', action='store_true',
               help='Be more verbose'),
    )

    def run(self, shapefile, verbose):
        from osgeo import ogr

        if not shapefile:
            print "Please add shapefile path as first argument."
            return
        else:
            print "Reading " + shapefile

        boundaries_file = ogr.Open(shapefile)
        if not boundaries_file:
            if verbose:
                print "OGR doesn't think that's a valid shapefile..."
            return

        layer = boundaries_file.GetLayerByIndex(0)

        feature = layer.GetFeature(0)
        i = 0
        while(feature):
            feature = layer.GetFeature(i)
            i += 1

            if not feature:
                continue

            name = unicode(feature.GetFieldAsString('NAME'), 'latin1').strip()
            name_long = unicode(feature.GetFieldAsString('NAME_LONG'), 'latin1').strip()
            abbrev = unicode(feature.GetFieldAsString('ABBREV'), 'latin1').strip()
            iso_a2 = unicode(feature.GetFieldAsString('ISO_A2'), 'latin1').strip()
            iso_a3 = unicode(feature.GetFieldAsString('ISO_A3'), 'latin1').strip()
            region = unicode(feature.GetFieldAsString('REGION_UN'), 'latin1').strip()
            subregion = unicode(feature.GetFieldAsString('SUBREGION'), 'latin1').strip()
            continent = unicode(feature.GetFieldAsString('CONTINENT'), 'latin1').strip()
            boundary = shapely.wkt.loads(feature.geometry().ExportToWkt())

            if isinstance(boundary, shapely.geometry.polygon.Polygon):
                boundary = shapely.geometry.MultiPolygon([boundary])

            print type(boundary)

            if verbose:
                print name + ":"
                print " " + name_long
                print " " + abbrev
                print " " + iso_a2
                print " " + iso_a3
                print " " + region
                print " " + subregion
                print " " + continent

            country = Boundaries()
            country.name = name
            country.name_long = name_long
            country.abbrev = abbrev
            country.iso_a2 = iso_a2 if iso_a2 != '-99' else ''
            country.iso_a3 = iso_a3 if iso_a3 != '-99' else ''
            country.region = region
            country.subregion = subregion
            country.continent = continent
            country.geometry = from_shape(boundary, srid=4326)

            Boundaries.query().filter(Boundaries.name == name).delete()
            db.session.add(country)

        boundaries_file.Destroy()
        db.session.commit()

        print "added " + str(i) + " boundaries"
