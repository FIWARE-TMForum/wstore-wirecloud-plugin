# -*- coding: utf-8 -*-

# Copyright (c) 2012-2014 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import os
import urllib

from django.conf import settings

from wstore.offerings.resource_plugins.plugin import Plugin
from .wgt import WgtFile, InvalidContents
from .template import TemplateParser, TemplateParseException
from .version import Version


class WirecloudPlugin(Plugin):

    _tmp_files = []
    _template_parser = None

    def _download_wgt(self, url, name):
        """
        Downloads a wgt file for a given location and saves it in
        a temporal file
        """
        tmp_path = os.path.join(settings.BASEDIR, 'tmp')

        if not os.path.isdir(tmp_path):
            os.mkdir(tmp_path)

        file_name = name + '_tmp.wgt'
        wgt_path = os.path.join(tmp_path, file_name)

        try:
            urllib.urlretrieve(url, wgt_path)
        except:
            # The URL is not valid
            raise ValueError('The URL provided is not valid: does not exists')

        self._tmp_files.append(wgt_path)

        return wgt_path

    def _get_template_parser(self, download_link, resource_path, name):
        """
        """
        wgt_path = None
        if download_link != '':
            wgt_path = self._download_wgt(download_link, name)
        else:
            # Build wgt object from path
            content_path = resource_path

            if resource_path[0] == '/':
                content_path = resource_path[1:]

            wgt_path = os.path.join(settings.BASEDIR, content_path)

        wgt_file = WgtFile(wgt_path)

        # Get template file
        template_file = wgt_file.get_template()
        template_parser = TemplateParser(template_file)

        return template_parser

    def _remove_tmp_files(self):
        # Remote tmp file if needed
        for tmp in self._tmp_files:
            try:
                os.remove(tmp)
            except:
                pass

        self._tmp_files = []

    def _get_media_type(self):
        # Include widget type
        valid_types = {
            'widget': 'application/x-widget+mashable-application-component',
            'mashup': 'application/x-mashup+mashable-application-component',
            'operator': 'application/x-operator+mashable-application-component'
        }

        mac_type = self._template_parser.get_resource_type()
        return valid_types[mac_type]

    def on_pre_create(self, provider, data):
        # Build WGT object from the provided WGT file
        try:
            self._template_parser = self._get_template_parser(data['link'], data['content_path'], data['name'])
        except InvalidContents as e:
            raise e
        except TemplateParseException as e:
            raise e
        except ValueError as e:
            raise e
        except:
            raise Exception("The Wirecloud resource could not be created")

    def on_post_create(self, resource):

        resource.content_type = self._get_media_type()

        # Include meta info
        resource.meta_info = self._template_parser.get_resource_info()

        # If the resource file has been provided the resource should be open
        if resource.resource_path != '':
            resource.open = True

        resource.save()
        self._remove_tmp_files()

    def on_post_update(self, resource):
        # Fix content type
        self._template_parser = self._get_template_parser(resource.download_link, resource.resource_path, resource.name)
        resource.content_type = self._get_media_type()
        resource.save()

        self._remove_tmp_files()

    def on_pre_upgrade(self, resource):
        # Check that the new mac is a bigger version of the existing one
        # Open old wgt file
        old_resource = resource.old_versions[-1]
        old_wgt_parser = self._get_template_parser(old_resource.download_link, old_resource.resource_path, resource.name + '_old')

        # Open new wgt file
        self._template_parser = self._get_template_parser(resource.download_link, resource.resource_path, resource.name)

        # Compare name, vendor and version
        old_version = Version(old_wgt_parser.get_resource_version())
        new_version = Version(self._template_parser.get_resource_version())

        if old_wgt_parser.get_resource_name() != self._template_parser.get_resource_name() \
        or old_wgt_parser.get_resource_vendor() != self._template_parser.get_resource_vendor() \
        or new_version <= old_version:
            raise ValueError('The provided wgt file is not a new version of the existing one')

    def on_post_upgrade(self, resource):
        # Include new meta info
        resource.meta_info = self._template_parser.get_resource_info()
        resource.save()
        self._remove_tmp_files()
