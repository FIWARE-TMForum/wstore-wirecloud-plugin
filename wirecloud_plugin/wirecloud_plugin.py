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


class WirecloudPlugin(Plugin):

    _tmp_file = False
    _wgt_path = None
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

        return wgt_path

    def on_pre_create(self, provider, data):
        # Build WGT object from the provided WGT file
        try:
            if data['link'] != '':
                self._wgt_path = self._download_wgt(data['link'], data['name'])
            else:
                # build wgt object from path
                content_path = data['content_path']

                if data['content_path'][0] == '/':
                    content_path = data['content_path'][1:]

                self._wgt_path = os.path.join(settings.BASEDIR, content_path)

            wgt_file = WgtFile(self._wgt_path)

            # Get template file
            template_file = wgt_file.get_template()
            self._template_parser = TemplateParser(template_file)
        except InvalidContents as e:
            raise e
        except TemplateParseException as e:
            raise e
        except:
            raise Exception("The Wirecloud resource could not be created")

    def on_post_create(self, resource):
        # Include widget type
        valid_types = {
            'widget': 'application/x-widget+mashable-application-component',
            'mashup': 'application/x-mashup+mashable-application-component',
            'operator': 'application/x-operator+mashable-application-component'
        }
        mac_type = self._template_parser.get_resource_type()

        resource.content_type = valid_types[mac_type]

        # Include meta info
        resource.meta_info = self._template_parser.get_resource_info()

        resource.save()

        # Remote tmp file if needed
        if self._tmp_file:
            os.remove(self._wgt_path)

    def on_pre_update(self, resource):
        pass

    def on_post_update(self, resource):
        pass

    def on_pre_upgrade(self, resource):
        pass

    def on_post_upgrade(self, resource):
        pass
