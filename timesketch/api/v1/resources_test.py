# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for v1 of the Timesketch API."""
from __future__ import print_function
from __future__ import unicode_literals

import json
import mock

from timesketch.lib.definitions import HTTP_STATUS_CODE_CREATED
from timesketch.lib.definitions import HTTP_STATUS_CODE_OK
from timesketch.lib.definitions import HTTP_STATUS_CODE_BAD_REQUEST
from timesketch.lib.testlib import BaseTest
from timesketch.lib.testlib import MockDataStore

from timesketch.api.v1.resources import ResourceMixin


class ResourceMixinTest(BaseTest):
    """Test ResourceMixin."""

    def test_to_json_empty_list(self):
        """Behavior of to_json when given an empty list."""
        response = ResourceMixin().to_json([])
        self.assertEqual(
            response.json,
            {
                "meta": {},
                "objects": [],
            },
        )


class SketchListResourceTest(BaseTest):
    """Test SketchListResource."""

    resource_url = "/api/v1/sketches/"

    def test_sketch_list_resource(self):
        """Authenticated request to get list of sketches."""
        self.login()
        response = self.client.get(self.resource_url)
        self.assertEqual(len(response.json["objects"]), 2)
        result = sorted(i["name"] for i in response.json["objects"])
        self.assertEqual(result, ["Test 1", "Test 3"])
        self.assert200(response)

    def test_sketch_post_resource(self):
        """Authenticated request to create a sketch."""
        self.login()
        data = dict(name="test", description="test")
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)


class SketchResourceTest(BaseTest):
    """Test SketchResource."""

    resource_url = "/api/v1/sketches/1/"

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_sketch_resource(self):
        """Authenticated request to get a sketch."""
        self.login()
        response = self.client.get(self.resource_url)
        self.assertEqual(len(response.json["objects"]), 1)
        self.assertEqual(len(response.json["objects"][0]["timelines"]), 1)
        self.assertEqual(response.json["objects"][0]["name"], "Test 1")
        self.assertIsInstance(response.json["meta"]["emojis"], dict)
        self.assert200(response)

    def test_sketch_acl(self):
        """
        Authenticated request to get a sketch that the user do not have read
        permission on.
        """
        self.login()
        response = self.client.get("/api/v1/sketches/2/")
        self.assert403(response)


class ViewListResourceTest(BaseTest):
    """Test ViewListResource."""

    resource_url = "/api/v1/sketches/1/views/"

    def test_post_view_list_resource(self):
        """Authenticated request to create a view."""
        self.login()
        data = dict(
            name="test",
            new_searchtemplate=False,
            query="test",
            filter={},
            dsl={},
        )
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        data["from_searchtemplate_id"] = 1
        response_with_searchtemplate = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)
        self.assertEqual(
            response_with_searchtemplate.status_code, HTTP_STATUS_CODE_CREATED
        )


class ViewResourceTest(BaseTest):
    """Test ViewResource."""

    resource_url = "/api/v1/sketches/1/views/1/"

    def test_view_resource(self):
        """Authenticated request to get a view."""
        self.login()
        response = self.client.get(self.resource_url)
        self.assertEqual(len(response.json["objects"]), 1)
        self.assertEqual(response.json["objects"][0]["name"], "View 1")
        self.assert200(response)

    def test_post_view_resource(self):
        """Authenticated request to update a view."""
        self.login()
        data = dict(name="test", query="test", filter="{}")
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)

    def test_invalid_user_in_view(self):
        """Authenticated request to get a view for another user."""
        self.login()
        response = self.client.get("/api/v1/sketches/1/views/3/")
        self.assert403(response)

    def test_invalid_view(self):
        """Authenticated request to get a view for non existing view."""
        self.login()
        response = self.client.get("/api/v1/sketches/1/views/2/")
        self.assert404(response)


class SearchTemplateResourceTest(BaseTest):
    """Test Search template resource."""

    resource_url = "/api/v1/searchtemplate/1/"

    def test_searchtemplate_resource(self):
        """Authenticated request to get a search template."""
        self.login()
        response = self.client.get(self.resource_url)
        self.assertEqual(len(response.json["objects"]), 1)
        self.assertEqual(response.json["objects"][0]["name"], "template")
        self.assert200(response)

    def test_invalid_searchtemplate(self):
        """Authenticated request to get a non existing search template."""
        self.login()
        response = self.client.get("/api/v1/searchtemplate/2/")
        self.assert404(response)


class ExploreResourceTest(BaseTest):
    """Test ExploreResource."""

    resource_url = "/api/v1/sketches/1/explore/"
    expected_response = {
        "meta": {
            "es_time": 5,
            "es_total_count": 1,
            "es_total_count_complete": 0,
            "timeline_colors": {"test": "FFFFFF"},
            "timeline_names": {"test": "Timeline 1"},
            "count_per_index": {},
            "count_per_timeline": {},
            "count_over_time": {"data": {}, "interval": ""},
            "scroll_id": "",
            "search_node": {
                "children": [],
                "description": None,
                "id": 1,
                "labels": [],
                "parent": None,
                "query_dsl": None,
                "query_filter": "{}",
                "query_result_count": 0,
                "query_string": "test",
            },
        },
        "objects": [
            {
                "sort": [1410593223000],
                "_type": "plaso_event",
                "_source": {
                    "timestamp": 1410593222543942,
                    "message": "Test event",
                    "label": ["__ts_star"],
                    "timestamp_desc": "Content Modification Time",
                    "datetime": "2014-09-13T07:27:03+00:00",
                    "__ts_timeline_id": 1,
                },
                "_score": "null",
                "selected": False,
                "_index": "test",
                "_id": "test",
            }
        ],
    }

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_search(self):
        """Authenticated request to query the datastore."""
        self.login()
        data = dict(query="test", filter={})
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        response_json = response.json
        # Remove flaky properties (dynamically generated)
        del response_json["meta"]["search_node"]["created_at"]
        del response_json["meta"]["search_node"]["query_time"]
        self.assertDictEqual(response_json, self.expected_response)
        self.assert200(response)


class AggregationExploreResourceTest(BaseTest):
    """Test AggregationExploreResource."""

    resource_url = "/api/v1/sketches/1/aggregation/explore/"

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_heatmap_aggregation(self):
        """Authenticated request to get aggregation requests."""
        self.login()
        data = dict(aggregation_dsl="test")
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assert200(response)


class EventResourceTest(BaseTest):
    """Test EventResource."""

    resource_url = "/api/v1/sketches/1/event/"
    expected_response = {
        "objects": {
            "timestamp_desc": "",
            "timestamp": 1410895419859714,
            "label": "",
            "source_long": "",
            "source_short": "",
            "es_index": "",
            "es_id": "",
            "message": "",
            "datetime": "2014-09-16T19:23:40+00:00",
            "__ts_timeline_id": 1,
        }
    }

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_get_event(self):
        """Authenticated request to get an event from the datastore."""
        self.login()
        response = self.client.get(
            self.resource_url + "?searchindex_id=test&event_id=test"
        )
        self.assertDictContainsSubset(self.expected_response, response.json)
        self.assert200(response)

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_invalid_index(self):
        """
        Authenticated request to get an event from the datastore, but in the
        wrong index.
        """
        self.login()
        response_400 = self.client.get(
            self.resource_url + "?searchindex_id=wrong_index&event_id=test"
        )
        self.assert400(response_400)


class EventAnnotationResourceTest(BaseTest):
    """Test EventAnnotationResource."""

    resource_url = "/api/v1/sketches/1/event/annotate/"

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_post_annotate_resource(self):
        """Authenticated request to create an annotation."""
        self.login()
        for annotation_type in ["comment", "label"]:
            event = {"_type": "test_event", "_index": "test", "_id": "test"}
            data = dict(
                annotation="test",
                annotation_type=annotation_type,
                events=[event],
            )
            response = self.client.post(
                self.resource_url,
                data=json.dumps(data),
                content_type="application/json",
            )
            self.assertIsInstance(response.json, dict)
            self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)

    def test_post_annotate_invalid_index_resource(self):
        """
        Authenticated request to create an annotation, but in the wrong index.
        """
        self.login()
        data = dict(
            annotation="test",
            annotation_type="comment",
            event_id="test",
            searchindex_id="invalid_searchindex",
        )
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_BAD_REQUEST)


class SearchIndexResourceTest(BaseTest):
    """Test SearchIndexResource."""

    resource_url = "/api/v1/searchindices/"

    @mock.patch(
        "timesketch.api.v1.resources.OpenSearchDataStore", MockDataStore
    )
    def test_post_create_searchindex(self):
        """Authenticated request to create a searchindex."""
        self.login()
        data = dict(
            searchindex_name="test3", es_index_name="test3", public=False
        )
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)


class TimelineListResourceTest(BaseTest):
    """Test TimelineList resource."""

    resource_url = "/api/v1/sketches/1/timelines/"

    def test_add_existing_timeline_resource(self):
        """Authenticated request to add a timeline to a sketch."""
        self.login()
        data = dict(timeline=1)
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_OK)

    def test_add_new_timeline_resource(self):
        """Authenticated request to add a timeline to a sketch."""
        self.login()
        data = dict(timeline=2)
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_CREATED)


class SigmaResourceTest(BaseTest):
    """Test Sigma resource."""

    resource_url = "/api/v1/sigma/rule/"
    expected_response = {
        "objects": {
            "description": "Detects suspicious installation of ZMap",
            "id": "5266a592-b793-11ea-b3de-0242ac130004",
            "level": "high",
            "logsource": {"product": "linux", "service": "shell"},
            "title": "Suspicious Installation of ZMap",
        }
    }

    def test_get_sigma_rule(self):
        """Authenticated request to get an sigma rule."""
        self.login()
        response = self.client.get(
            self.resource_url + "5266a592-b793-11ea-b3de-0242ac130004"
        )
        self.assertIsNotNone(response)


class SigmaListResourceTest(BaseTest):
    """Test Sigma resource."""

    resource_url = "/api/v1/sigma/"
    expected_response = {
        "meta": {"current_user": "test1", "rules_count": 1},
        "objects": [
            {
                'author': 'Alexander Jaeger',
                'date': '2020/06/26',
                'description': 'Detects suspicious installation of ZMap',
                'detection': {
                    'condition': 'keywords',
                    'keywords': ['*apt-get install zmap*'],
                },
                'es_query': '(data_type:("shell:zsh:history" OR "bash:history:command" OR "apt:history:line" OR "selinux:line") AND "apt-get install zmap")',  # pylint: disable=line-too-long
                'falsepositives': ['Unknown'],
                'file_name': 'lnx_susp_zmap.yml',
                'file_relpath': 'lnx_susp_zmap.yml',
                'id': '5266a592-b793-11ea-b3de-0242ac130004',
                'level': 'high',
                'logsource': {'product': 'linux', 'service': 'shell'},
                'modified': '2020/06/26',
                'references': [
                    'https://rmusser.net/docs/ATT&CK-Stuff/ATT&CK/Discovery.html'  # pylint: disable=line-too-long
                ],
                'tags': ['attack.discovery', 'attack.t1046'],
                'title': 'Suspicious Installation of ZMap',
                'ts_comment': 'Part of Timesketch repo',
                'ts_use_in_analyzer': True,
            }
        ],
    }

    def test_get_sigma_rule_list(self):
        self.login()
        response = self.client.get(self.resource_url)
        data = json.loads(response.get_data(as_text=True))
        print(data)
        self.assertDictContainsSubset(self.expected_response, response.json)
        self.assertIsNotNone(response)


class SigmaByTextResourceTest(BaseTest):
    """Test Sigma by text resource."""

    resource_url = "/api/v1/sigma/text/"
    correct_rule = """
        title: Installation of foobar
        id: bb1e0d1d-cd13-4b65-bf7e-69b4e740266b
        description: Detects suspicious installation of foobar
        references:
            - https://samle.com/foobar
        author: Alexander Jaeger
        date: 2020/12/10
        modified: 2020/12/10
        tags:
            - attack.discovery
            - attack.t1046
        logsource:
            product: linux
            service: shell
        detection:
            keywords:
                # Generic suspicious commands
                - '*apt-get install foobar*'
            condition: keywords
        falsepositives:
            - Unknown
        level: high
        """
    expected_response = {
        "meta": {"parsed": True},
        "objects": [
            {
                "title": "Installation of foobar",
                "id": "bb1e0d1d-cd13-4b65-bf7e-69b4e740266b",
                "description": "Detects suspicious installation of foobar",
                "references": ["https://samle.com/foobar"],
                "author": "Alexander Jaeger",
                "date": "2020/12/10",
                "modified": "2020/12/10",
                "tags": ["attack.discovery", "attack.t1046"],
                "logsource": {"product": "linux", "service": "shell"},
                "detection": {
                    "keywords": ["*apt-get install foobar*"],
                    "condition": "keywords",
                },
                "falsepositives": ["Unknown"],
                "level": "high",
                "es_query": '(data_type:("shell:zsh:history" OR "bash:history:command" OR "apt:history:line" OR "selinux:line") AND "apt-get install foobar")',  # pylint: disable=line-too-long
                "file_name": "N/A",
                "file_relpath": "N/A",
            }
        ],
    }

    def test_get_sigma_rule(self):
        """Authenticated request to get an sigma rule by text."""
        self.login()

        data = dict(content=self.correct_rule)
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_OK)
        self.assertDictContainsSubset(self.expected_response, response.json)
        self.assert200(response)

        # wrong sigma rule
        data = dict(content="foobar: asd")
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        data = json.loads(response.get_data(as_text=True))

        self.assertIn("No detection definitions found", data["message"])
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_BAD_REQUEST)

        # no content given
        data = dict(action="post")
        response = self.client.post(
            self.resource_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type="application/json",
        )
        data = json.loads(response.get_data(as_text=True))

        self.assertIn("Missing values from the request", data["message"])
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_BAD_REQUEST)


class IntelligenceResourceTest(BaseTest):
    """Test Intelligence resource."""

    def test_get_intelligence_tag_metadata(self):
        """Authenticated request to get intelligence tag metadata."""
        expected_tag_metadata = {
            "default": {"class": "info", "weight": 0},
            "legit": {"class": "success", "weight": 10},
            "malware": {"class": "danger", "weight": 100},
            "suspicious": {"class": "warning", "weight": 50},
        }
        self.login()
        response = self.client.get("/api/v1/intelligence/tagmetadata/")
        data = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, HTTP_STATUS_CODE_OK)
        self.assertEqual(data, expected_tag_metadata)
