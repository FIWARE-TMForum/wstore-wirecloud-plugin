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


def parse_mime_type(mime_type):
    parts = mime_type.split(';')
    params = dict([tuple([s.strip() for s in param.split('=', 1)])
        for param in parts[1:]
    ])

    full_type = parts[0].strip()
    if full_type == '*':
        full_type = '*/*'

    return (full_type, params)
