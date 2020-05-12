# EXIF might work again with exif2 for python 3, which is now available again:

# # TODO remove
# def _get_if_exist(self, data, key):
#     return data[key] if key in data else None
#
# # TODO remove
# def _convert_to_degress(self, value):
#     """
#     Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
#     :param value:
#     :type value: exifread.utils.Ratio
#     :rtype: float
#     """
#     return float(value.values[0].num) / float(value.values[0].den) + (float(value.values[1].num) / float(value.values[1].den) / 60.0) + (float(value.values[2].num) / float(value.values[2].den) / 3600.0)

# # TODO remove
# def getExifForImage(self, imageNumber):
#     exif = [None, None, None, None, None, None]
#
#     dirName = self.settings.value("APIS/image_dir")
#     imageName = imageNumber.replace('.', '_') + '.jpg'
#     image = os.path.normpath(dirName + '\\' + self.filmId + '\\' + imageName)
#     if os.path.isfile(image):
#         with open(image, 'rb') as f:
#             tags = exifread.process_file(f, details=False)
#
#             gps_altitude = self._get_if_exist(tags, 'GPS GPSAltitude')
#             gps_altitude_ref = self._get_if_exist(tags, 'GPS GPSAltitudeRef')
#             if gps_altitude and gps_altitude_ref:
#                 alt = float(gps_altitude.values[0].num / gps_altitude.values[0].den)
#                 if gps_altitude_ref.values[0] == 1:
#                     alt *= -1
#                 exif[0] = alt
#
#             gps_longitude = self._get_if_exist(tags, 'GPS GPSLongitude')
#             gps_longitude_ref = self._get_if_exist(tags, 'GPS GPSLongitudeRef')
#             if gps_longitude and gps_longitude_ref:
#                 lon = self._convert_to_degress(gps_longitude)
#                 if gps_longitude_ref.values[0] != 'E':
#                     lon = 0 - lon
#                 exif[1] = lon
#
#             gps_latitude = self._get_if_exist(tags, 'GPS GPSLatitude')
#             gps_latitude_ref = self._get_if_exist(tags, 'GPS GPSLatitudeRef')
#             if gps_latitude and gps_latitude_ref:
#                 lat = self._convert_to_degress(gps_latitude)
#                 if gps_latitude_ref.values[0] != 'N':
#                     lat = 0 - lat
#                 exif[2] = lat
#
#             exif_exposure_time = self._get_if_exist(tags, 'EXIF ExposureTime')
#             if exif_exposure_time:
#                 exif[3] = float(exif_exposure_time.values[0].num / exif_exposure_time.values[0].den)
#
#             exif_focal_length = self._get_if_exist(tags, 'EXIF FocalLength')
#             if exif_focal_length:
#                 exif[4] = float(exif_focal_length.values[0].num / exif_focal_length.values[0].den)
#
#             exif_fnumber = self._get_if_exist(tags, 'EXIF FNumber')
#             if exif_fnumber:
#                 exif[5] = float(exif_fnumber.values[0].num / exif_fnumber.values[0].den)
#
#     return exif
#
# # TODO remove
# def OLDgetExifForImage(self, imageNumber):
#     exif = [None, None, None, None, None, None]
#     dirName = self.settings.value("APIS/image_dir")
#     imageName = imageNumber.replace('.', '_') + '.jpg'
#     image = os.path.normpath(dirName+'\\'+self.filmId+'\\'+imageName)
#
#     if os.path.isfile(image):
#         md = exiv.ImageMetadata(image)
#         md.read()
#
#         if "Exif.GPSInfo.GPSAltitude" in md.exif_keys:
#             exif[0] = float(md["Exif.GPSInfo.GPSAltitude"].value)
#
#         if "Exif.GPSInfo.GPSLongitude" in md.exif_keys:
#             lon = md["Exif.GPSInfo.GPSLongitude"].value
#             exif[1] = float(lon[0])+((float(lon[1])+(float(lon[2])/60))/60)
#
#         if "Exif.GPSInfo.GPSLatitude" in md.exif_keys:
#             lat = md["Exif.GPSInfo.GPSLatitude"].value
#             exif[2] = float(lat[0])+((float(lat[1])+(float(lat[2])/60))/60)
#
#         if "Exif.Photo.ExposureTime" in md.exif_keys:
#             exif[3] = float(md["Exif.Photo.ExposureTime"].value)
#
#         if "Exif.Photo.FocalLength" in md.exif_keys:
#             exif[4] = float(md["Exif.Photo.FocalLength"].value)
#
#         if "Exif.Photo.FNumber" in md.exif_keys:
#             exif[5] = md["Exif.Photo.FNumber"].value
#
#     return exif
