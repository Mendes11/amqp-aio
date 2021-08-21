from amqp_aio.amqp import consts


def select_method_frame(frame):
    """
    Returns the Method Frame based on the Frame's class_id and method_id
    values.
    :param MethodFrame frame: MethodFrame instance
    :return: The method's corresponding frame class
    """
    from amqp_aio.amqp import connection, channel, exchange, queue
    methods_map = {
        consts.CONNECTION_CLASS_ID: {
            consts.CONNECTION_START_ID: connection.Start,
            consts.CONNECTION_START_OK_ID: connection.StartOk,
            consts.CONNECTION_SECURE_ID: connection.Secure,
            consts.CONNECTION_SECURE_OK_ID: connection.SecureOK,
            consts.CONNECTION_TUNE_ID: connection.Tune,
            consts.CONNECTION_TUNE_OK_ID: connection.TuneOK,
            consts.CONNECTION_OPEN_ID: connection.Open,
            consts.CONNECTION_OPEN_OK_ID: connection.OpenOK,
            consts.CONNECTION_CLOSE_ID: connection.Close,
            consts.CONNECTION_CLOSE_OK_ID: connection.CloseOK,
        },
        consts.CHANNEL_CLASS_ID: {
            consts.CHANNEL_OPEN_ID: channel.Open,
            consts.CHANNEL_OPEN_OK_ID: channel.OpenOk,
            consts.CHANNEL_FLOW_ID: channel.Flow,
            consts.CHANNEL_FLOW_OK_ID: channel.FlowOK,
            consts.CHANNEL_CLOSE_ID: channel.Close,
            consts.CHANNEL_CLOSE_OK_ID: channel.CloseOK
        },
        consts.EXCHANGE_CLASS_ID: {
            consts.EXCHANGE_DECLARE_ID: exchange.Declare,
            consts.EXCHANGE_DECLARE_OK_ID: exchange.DeclareOK,
            consts.EXCHANGE_DELETE_ID: exchange.Delete,
            consts.EXCHANGE_DELETE_OK_ID: exchange.DeleteOK
        },
        consts.QUEUE_CLASS_ID: {
            consts.QUEUE_DECLARE_ID: queue.Declare,
            consts.QUEUE_DECLARE_OK_ID: queue.DeclareOK,
            consts.QUEUE_BIND_ID: queue.Bind,
            consts.QUEUE_BIND_OK_ID: queue.BindOK,
            consts.QUEUE_UNBIND_ID: queue.Unbind,
            consts.QUEUE_UNBIND_OK_ID: queue.UnbindOK,
            consts.QUEUE_PURGE_ID: queue.Purge,
            consts.QUEUE_PURGE_OK_ID: queue.PurgeOK,
            consts.QUEUE_DELETE_ID: queue.Delete,
            consts.QUEUE_DELETE_OK_ID: queue.DeleteOK
        }
    }
    cls_methods = methods_map[frame.class_id]
    return cls_methods[frame.method_id]


