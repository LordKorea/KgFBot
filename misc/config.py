"""This file is adapted from a part of the KgF project by LordKorea. This file
is exempt from the license of EmbedBot and instead licensed under the terms of
the license of the KgF project.

MIT License
Copyright (c) 2017-2018 LordKorea

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from json import dump, load
from os.path import exists

class Config:

    def __init__(self):
        """Constructor."""
        self._config_file = "config.json"
        self._config = {}

        # Initialize the configuration if it does not exist
        if not exists(self._config_file):
            with open(self._config_file, "w") as f:
                dump(self._config, f, indent=4, sort_keys=True)

        # Load the configuration from disk
        with open(self._config_file, "r") as f:
            self._config = load(f)

    def get(self, key, default):
        """Gets the value for the given configuration key.

        If the configuration key has no associated value then a default value
        will be set.

        Args:
            key: The configuration key.
            default: The default value for the configuration key.

        Returns:
            The value of the configuration key (or the default).

        Contract:
            This method locks the configuration lock.
        """
        # Set the default and write-back
        if key not in self._config:
            self._config[key] = default
            with open(self._config_file, "w") as f:
                dump(self._config, f, indent=4, sort_keys=True)

        return self._config[key]
