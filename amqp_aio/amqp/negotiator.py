from typing import Union, List

from amqp_aio.amqp.exceptions import AMQPException


class ProtocolNegotiator:

    def negotiate_auth_mechanism(self, client: str, server: List[str]) -> str:
        """
        Ensures the client authentication mechanism is enabled on the server

        :param client: Selected mechanism
        :param server: List of mechanisms supported by the server
        :return: Selected Mechanism
        :rtype: str
        """
        if client not in server:
            raise AMQPException(
                "The server doesn't support {} authentication mechanism. "
                "The supported mechanisms are : {}".format(client, server)
            )

        return client

    def negotiate_numeric(self, client, server) -> Union[float, int]:
        """
        Selects the lowest value from client or server configuration.

        # This logic uses the same logic from pika. Since they implemented
        it based on other libraries

        :param float|int client: Client Value
        :param float|int server: Server Value
        :return: Selected value
        :rtype: float|int
        """
        if client is None:
            client = 0
        if server is None:
            server = 0

        if server == 0 or client == 0:
            return max(server, client)

        return min(server, client)
