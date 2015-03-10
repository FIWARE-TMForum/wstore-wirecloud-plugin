
Wirecloud Plugin
================

This plugin is inteded to allow the automatic loading and validation of information contained in the wgt file of a Wirecloud component.

## Extra Requirements

The installation of the current plugin in WStore requires the following extra python packges not required by WStore:
* regex

<pre>
    pip install regex
</pre>

## Management

The Wirecloud plugin can be managed in WStore with the following commands:

* Installation

<pre>
    python manage.py loadplugin wirecloud_plugin.zip
</pre>

* Uninstallation

<pre>
    python manage.py removeplugin "Wirecloud component"
</pre>
