class SugarNetworkStack:
    def __init__(self, activity):
        self.__activity = activity

    def joined_cb(self, activity):
        self.__activity._alert("Activity Joined", "Someone has joined the activity")

    def shared_cb(self, activity):
        self.__activity._alert("Activity Shared", "The activity has been shared")
