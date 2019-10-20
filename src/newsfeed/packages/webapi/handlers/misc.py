"""Miscellaneous handlers."""

import copy
from typing import Dict

from aiohttp import web


async def get_status_handler(_: web.Request) -> web.Response:
    """Handle status requests."""
    return web.json_response({'status': 'OK'})


async def get_openapi_schema_handler(_: web.Request, *, base_path: str) -> web.Response:
    """Handle OpenAPI schema requests."""
    schema: Dict = copy.deepcopy(OPENAPI_SCHEMA)
    schema['servers'] = [{'url': base_path}]
    return web.json_response(schema)


OPENAPI_SCHEMA = {
    'openapi': '3.0.2',
    'info': {
        'version': '1.0.0',
        'title': 'NewsFeed Microservice',
    },
    'paths': {
        '/newsfeed/{newsfeed_id}/events/': {
            'get': {
                'summary': 'Return newsfeed events',
                'operationId': 'get_newsfeed_events',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed events',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/EventsList',
                                },
                            },
                        },
                    },
                },
            },
            'post': {
                'summary': 'Post newsfeed event',
                'operationId': 'post_newsfeed_event',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'properties': {
                                    'data': {
                                        'type': 'object',
                                        'example': {
                                            'field_1': 'some_data',
                                            'field_2': 'other_data',
                                            'field_etc': 'etc_data',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                'responses': {
                    '202': {
                        'description': 'Event has been successfully posted',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/Event',
                                },
                            },
                        },
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/events/{event_id}/': {
            'delete': {
                'summary': 'Delete newsfeed event',
                'operationId': 'delete_newsfeed_event',
                'tags': [
                    'Events',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                    {
                        'in': 'path',
                        'name': 'event_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                    },
                ],
                'responses': {
                    '204': {
                        'description': 'Newsfeed event has been successfully deleted',
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscriptions/': {
            'get': {
                'summary': 'Return newsfeed subscriptions',
                'operationId': 'get_newsfeed_subscriptions',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed subscriptions',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/SubscriptionsList',
                                },
                            },
                        },
                    },
                },
            },
            'post': {
                'summary': 'Post newsfeed subscription',
                'operationId': 'post_newsfeed_subscription',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'properties': {
                                    'to_newsfeed_id': {
                                        'type': 'string',
                                        'example': '123',
                                    },
                                },
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Subscription has been successfully created',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/Subscription',
                                },
                            },
                        },
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscriptions/{subscription_id}/': {
            'delete': {
                'summary': 'Delete newsfeed subscription',
                'operationId': 'delete_newsfeed_subscription',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                    {
                        'in': 'path',
                        'name': 'subscription_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                    },
                ],
                'responses': {
                    '204': {
                        'description': 'Newsfeed subscription has been successfully deleted',
                    },
                },
            },
        },
        '/newsfeed/{newsfeed_id}/subscribers/subscriptions/': {
            'get': {
                'summary': 'Return newsfeed subscriber subscriptions',
                'operationId': 'get_newsfeed_subscriber_subscriptions',
                'tags': [
                    'Subscriptions',
                ],
                'parameters': [
                    {
                        'in': 'path',
                        'name': 'newsfeed_id',
                        'required': True,
                        'schema': {
                            'type': 'string',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'List of newsfeed subscriber subscriptions',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/SubscriptionsList',
                                },
                            },
                        },
                    },
                },
            },
        },
        '/status/': {
            'get': {
                'summary': 'Return current microservice status',
                'operationId': 'get_status',
                'tags': [
                    'Miscellaneous',
                ],
                'responses': {
                    '200': {
                        'description': 'Information about current service status',
                    },
                },
            },
        },
        '/docs/': {
            'get': {
                'summary': 'Return microservice OpenAPI v3 documentation',
                'operationId': 'get_docs',
                'tags': [
                    'Miscellaneous',
                ],
                'responses': {
                    '200': {
                        'description': 'Service OpenAPI v3 documentation',
                    },
                },
            },
        },
    },
    'components': {
        'schemas': {
            'Event': {
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                    'newsfeed_id': {
                        'type': 'string',
                        'example': '123',
                    },
                    'data': {
                        'type': 'object',
                        'example': {
                            'payload_id': 835,
                        },
                    },
                    'parent_fqid': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        },
                        'example': ['123', '9d75e08f-f73f-4d80-a581-d3f9290520e6'],
                    },
                    'child_fqids': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'example': ['123', '9d75e08f-f73f-4d80-a581-d3f9290520e6'],
                        },
                    },
                    'first_seen_at': {
                        'type': 'integer',
                        'example': 1571436411,
                    },
                    'published_at': {
                        'type': 'integer',
                        'example': 1571436411,
                    },
                },
            },
            'EventsList': {
                'properties': {
                    'results': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/components/schemas/Event',
                        },
                    },
                },
            },
            'Subscription': {
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                    'newsfeed_id': {
                        'type': 'string',
                        'example': '123',
                    },
                    'to_newsfeed_id': {
                        'type': 'string',
                        'example': '124',
                    },
                    'subscribed_at': {
                        'type': 'integer',
                        'example': 1571436411,
                    },
                },
            },
            'SubscriptionsList': {
                'properties': {
                    'results': {
                        'type': 'array',
                        'items': {
                            '$ref': '#/components/schemas/Subscription',
                        },
                    },
                },
            },
        },
    },
}
