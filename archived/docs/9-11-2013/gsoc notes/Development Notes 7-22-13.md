
# Development Notes 7-22-13

Working at getting a channel created.

So, the text_handler example is only for handling chat over an existing channel.

It is very likely then that ensure creates the channel.

Alright, so yes ensure creates a channel.


Dynamic channel creation arguments:

    def create_request_dict(action, contact_id):
        if action == 'text':
            return {
                TelepathyGLib.PROP_CHANNEL_CHANNEL_TYPE:
                    TelepathyGLib.IFACE_CHANNEL_TYPE_TEXT,
                TelepathyGLib.PROP_CHANNEL_TARGET_HANDLE_TYPE:
                    int(TelepathyGLib.HandleType.CONTACT),
                TelepathyGLib.PROP_CHANNEL_TARGET_ID: contact_id}
        elif action in ['audio', 'video']:
            return {
                TelepathyGLib.PROP_CHANNEL_CHANNEL_TYPE:
                    TelepathyGLib.IFACE_CHANNEL_TYPE_STREAMED_MEDIA,
                TelepathyGLib.PROP_CHANNEL_TARGET_HANDLE_TYPE:
                    int(TelepathyGLib.HandleType.CONTACT),
                TelepathyGLib.PROP_CHANNEL_TARGET_ID: contact_id,
                TelepathyGLib.PROP_CHANNEL_TYPE_STREAMED_MEDIA_INITIAL_AUDIO:
                    True,
                TelepathyGLib.PROP_CHANNEL_TYPE_STREAMED_MEDIA_INITIAL_VIDEO:
                    action == 'video'}
        else:
            usage()


Which means we can define them separately quite easily.
We need two text based channels, one for chat and one for commands.
If we can get them working independently and between only two connected users we'll be set to move onto GStreamer!


The correct setup process needs an account_id and a contact_id?

    dbus = TelepathyGLib.DBusDaemon.dup()

    if len(sys.argv) != 4:
        usage()

    _, account_id, action, contact_id = sys.argv

    account_manager = TelepathyGLib.AccountManager.dup()

    account = account_manager.ensure_account("%s%s" %
        (TelepathyGLib.ACCOUNT_OBJECT_PATH_BASE, account_id))

    request_dict = create_request_dict(action, contact_id)

    request = TelepathyGLib.AccountChannelRequest.new(account, request_dict, 0)
    # FIXME: for some reason TelepathyGLib.USER_ACTION_TIME_CURRENT_TIME is
    # not defined (bgo #639206)

    main_loop = GObject.MainLoop()

    request.ensure_channel_async("", None, ensure_channel_cb, main_loop)

    main_loop.run()


