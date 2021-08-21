# import pytest
#
# from amqp_aio.amqp.connection import Start
#
#
# @pytest.fixture
# def start_payload():
#     return b'\x00\t\x00\x00\x01\xce\x0ccapabilitiesF\x00\x00\x00\xc7\x12publisher_confirmst\x01\x1aexchange_exchange_bindingst\x01\nbasic.nackt\x01\x16consumer_cancel_notifyt\x01\x12connection.blockedt\x01\x13consumer_prioritiest\x01\x1cauthentication_failure_closet\x01\x10per_consumer_qost\x01\x0fdirect_reply_tot\x01\x0ccluster_nameS\x00\x00\x00\rrabbit@mendes\tcopyrightS\x00\x00\x007Copyright (c) 2007-2020 VMware, Inc. or its affiliates.\x0binformationS\x00\x00\x009Licensed under the MPL 2.0. Website: https://rabbitmq.com\x08platformS\x00\x00\x00\x11Erlang/OTP 23.2.6\x07productS\x00\x00\x00\x08RabbitMQ\x07versionS\x00\x00\x00\x053.8.9\x00\x00\x00\x0ePLAIN AMQPLAIN\x00\x00\x00\x05en_US'
#
#
# def test_parse_start_method(start_payload):
#     res = Start.from_bytes(start_payload)
#     assert isinstance(res, Start)
