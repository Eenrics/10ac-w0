import json
import argparse
import os
import io
import shutil
import copy
from datetime import datetime
from pick import pick
from time import sleep
from matplotlib import pyplot as plt
import pandas as pd


# Create wrapper classes for using slack_sdk in place of slacker
class SlackDataLoader:
    '''
    Slack exported data IO class.

    When you open slack exported ZIP file, each channel or direct message 
    will have its own folder. Each folder will contain messages from the 
    conversation, organised by date in separate JSON files.

    You'll see reference files for different kinds of conversations: 
    users.json files for all types of users that exist in the slack workspace
    channels.json files for public channels, 
    
    These files contain metadata about the conversations, including their names and IDs.

    For secruity reason, we have annonymized names - the names you will see are generated using faker library.
    
    '''
    def __init__(self, path):
        '''
        path: path to the slack exported data folder
        '''
        self.path = path
        self.channels = self.get_channels()
        self.users = self.get_ussers()
    

    def get_users(self):
        '''
        write a function to get all the users from the json file
        '''
        with open(os.path.join(self.path, 'users.json'), 'r') as f:
            users = json.load(f)

        return users
    
    def get_channels(self):
        '''
        write a function to get all the channels from the json file
        '''
        with open(os.path.join(self.path, 'channels.json'), 'r') as f:
            channels = json.load(f)

        return channels

    def get_channel_messages(self, channel_name):
        '''
        write a function to get all the messages from a channel
        
        '''
        with open(os.path.join(self.path, 'message.json'), 'r') as f:
            message = json.load(f)
            channel_massage = message[channel_name]

        return channel_massage

    # 
    def get_user_map(self):
        '''
        write a function to get a map between user id and user name
        '''
        userNamesById = {}
        userIdsByName = {}
        for user in self.users:
            userNamesById[user['id']] = user['name']
            userIdsByName[user['name']] = user['id']
        return userNamesById, userIdsByName 

    def map_userid_2_realname(self, user_profile: dict, comm_dict: dict, plot=False):
        """
        map slack_id to realnames
        user_profile: a dictionary that contains users info such as real_names
        comm_dict: a dictionary that contains slack_id and total_message sent by that slack_id
        """
        user_dict = {} # to store the id
        real_name = [] # to store the real name
        ac_comm_dict = {} # to store the mapping
        count = 0
        # collect all the real names
        for i in range(len(user_profile['profile'])):
            real_name.append(dict(user_profile['profile'])[i]['real_name'])

        # loop the slack ids
        for i in user_profile['id']:
            user_dict[i] = real_name[count]
            count += 1

        # to store mapping
        for i in comm_dict:
            if i in user_dict:
                ac_comm_dict[user_dict[i]] = comm_dict[i]

        ac_comm_dict = pd.DataFrame(data= zip(ac_comm_dict.keys(), ac_comm_dict.values()),
        columns=['LearnerName', '# of Msg sent in Threads']).sort_values(by='# of Msg sent in Threads', ascending=False)
        
        if plot:
            ac_comm_dict.plot.bar(figsize=(15, 7.5), x='LearnerName', y='# of Msg sent in Threads')
            plt.title('Student based on Message sent in thread', size=20)
            
        return ac_comm_dict




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export Slack history')

    
    parser.add_argument('--zip', help="Name of a zip file to import")
    args = parser.parse_args()
