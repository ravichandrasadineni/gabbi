#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Test response handlers.
"""

import unittest

from gabbi import case
from gabbi import driver
from gabbi import handlers


class HandlersTest(unittest.TestCase):
    """Test the response handlers.

    Note that this does not test the magic template variables, that
    should be tested somewhere else.
    """

    def setUp(self):
        super(HandlersTest, self).setUp()
        self.test_class = case.HTTPTestCase
        self.test = driver.TestBuilder('mytest', (self.test_class,),
                                       {'test_data': {}})

    def test_response_strings(self):
        handler = handlers.StringResponseHandler(self.test_class)
        self.test.test_data = {'response_strings': ['alpha', 'beta']}
        self.test.output = 'alpha\nbeta\n'
        self._assert_handler(handler)

    def test_response_strings_fail(self):
        handler = handlers.StringResponseHandler(self.test_class)
        self.test.test_data = {'response_strings': ['alpha', 'beta']}
        self.test.output = 'alpha\nbta\n'
        with self.assertRaises(AssertionError):
            self._assert_handler(handler)

    def test_response_json_paths(self):
        handler = handlers.JSONResponseHandler(self.test_class)
        self.test.test_data = {'response_json_paths': {
            '$.objects[0].name': 'cow',
            '$.objects[1].location': 'house',
        }}
        self.test.json_data = {
            'objects': [{'name': 'cow',
                         'location': 'barn'},
                        {'name': 'chris',
                         'location': 'house'}]
        }
        self._assert_handler(handler)

    def test_response_json_paths_fail_data(self):
        handler = handlers.JSONResponseHandler(self.test_class)
        self.test.test_data = {'response_json_paths': {
            '$.objects[0].name': 'cow',
            '$.objects[1].location': 'house',
        }}
        self.test.json_data = {
            'objects': [{'name': 'cw',
                         'location': 'barn'},
                        {'name': 'chris',
                         'location': 'house'}]
        }
        with self.assertRaises(AssertionError):
            self._assert_handler(handler)

    def test_response_json_paths_fail_path(self):
        handler = handlers.JSONResponseHandler(self.test_class)
        self.test.test_data = {'response_json_paths': {
            '$.objects[1].name': 'cow',
        }}
        self.test.json_data = {
            'objects': [{'name': 'cow',
                         'location': 'barn'},
                        {'name': 'chris',
                         'location': 'house'}]
        }
        with self.assertRaises(AssertionError):
            self._assert_handler(handler)

    def test_response_headers(self):
        handler = handlers.HeadersResponseHandler(self.test_class)
        self.test.response = {'content-type': 'text/plain'}

        self.test.test_data = {'response_headers': {
            'content-type': 'text/plain',
        }}
        self._assert_handler(handler)

        self.test.test_data = {'response_headers': {
            'Content-Type': 'text/plain',
        }}
        self._assert_handler(handler)

    def test_response_headers_regex(self):
        handler = handlers.HeadersResponseHandler(self.test_class)
        self.test.test_data = {'response_headers': {
            'content-type': '/text/plain/',
        }}
        self.test.response = {'content-type': 'text/plain; charset=UTF-8'}
        self._assert_handler(handler)

    def test_response_headers_fail_data(self):
        handler = handlers.HeadersResponseHandler(self.test_class)
        self.test.test_data = {'response_headers': {
            'content-type': 'text/plain',
        }}
        self.test.response = {'content-type': 'application/json'}
        with self.assertRaises(AssertionError) as failure:
            self._assert_handler(handler)
        self.assertIn("Expect header content-type with value text/plain,"
                      " got application/json",
                      str(failure.exception))

    def test_response_headers_fail_header(self):
        handler = handlers.HeadersResponseHandler(self.test_class)
        self.test.test_data = {'response_headers': {
            'location': '/somewhere',
        }}
        self.test.response = {'content-type': 'application/json'}
        with self.assertRaises(AssertionError) as failure:
            self._assert_handler(handler)
        self.assertIn("'location' header not present in response:",
                      str(failure.exception))

    def _assert_handler(self, handler):
        # Instantiate our contained test class by naming its test
        # method and then run its tests to confirm.
        test = self.test('test_request')
        handler(test)
