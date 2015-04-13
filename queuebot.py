import sys
import argparse
import re
import configparser
import time
import random

import irc.client
import irc.logging

class QueueBot(irc.client.SimpleIRCClient):
    sub_queue = []
    queue = []
    admins = []
    subscribers = []
    moderators = []
    queue_active = False
    commands = {}

    def get_queue(self):
        return self.sub_queue + self.queue

    def c_queue_join(self, chatconn, username, extra_message):
        if self.queue_active:
            combined_queue = self.get_queue()
            if username not in combined_queue:
                msg = 'You have been added to the queue {0}'.format(username)

                if username in self.subscribers:
                    msg += ' (sub prio!)'
                    self.sub_queue.append(username)
                else:
                    self.queue.append(username)

                self.say(msg)
        else:
            print('The queue is not active! Admins can type \'!queue enable\' to enable the queue.')

    def c_queue_remove(self, chatconn, username, extra_message):
        to_remove = extra_message.lower()
        if self.queue_active:
            if to_remove in self.sub_queue:
                self.sub_queue.remove(to_remove)
                self.say('Removed {0} from the queue!'.format(to_remove))
            elif to_remove in self.queue:
                self.queue.remove(to_remove)
                self.say('Removed {0} from the queue!'.format(to_remove))
            else:
                self.say('{0} is not in the queue!'.format(to_remove))

    def c_queue_add(self, chatconn, username, extra_message):
        if username in self.admins:
            to_add = extra_message.lower()
            if self.queue_active:
                combined_queue = self.get_queue()
                if to_add not in combined_queue:
                    msg = '{0} has been added to the queue!'.format(to_add)

                    if to_add in self.subscribers:
                        msg += ' (sub prio!)'
                        self.sub_queue.append(to_add)
                    else:
                        self.queue.append(to_add)

                    self.say(msg)

    def c_queue_enable(self, chatconn, username, extra_message):
        if username in self.admins:
            if self.queue_active:
                self.say('The queue is already enabled!')
            else:
                self.queue.clear()
                self.sub_queue.clear()
                self.queue_active = True
                self.say('Queue is now active! Type \'!queue join\' to join the queue')

    def c_queue_disable(self, chatconn, username, extra_message):
        if username in self.admins:
            if not self.queue_active:
                self.say('The queue is already disabled!')
            else:
                self.queue.clear()
                self.sub_queue.clear()
                self.queue_active = False
                self.say('Queue is now disabled')

    def c_queue_clear(self, chatconn, username, extra_message):
        if self.queue_active:
            if username in self.admins:
                self.queue.clear()
                self.sub_queue.clear()
                self.say('The queue has been cleared PogChamp')

    def c_queue_list(self, chatconn, username, extra_message):
        if username in self.admins:
            if self.queue_active:
                combined_queue = self.get_queue()
                if len(combined_queue) > 0:
                    queue_str = 'Current queue: {0}'.format(', '.join(combined_queue[:15]))
                    if len(combined_queue) > 15:
                        queue_str += '...'
                    self.say(queue_str)
                else:
                    self.say('The queue is empty BibleThump')
            else:
                self.say('The queue is not active! Admins can type \'!queue enable\' to enable the queue.')

    def c_queue_pop(self, chatconn, username, extra_message):
        if username in self.admins:
            if self.queue_active:
                combined_queue = self.get_queue()
                if len(combined_queue) > 0:
                    winner = combined_queue.pop(0)
                    self.say('{0} is next in queue!'.format(winner))
                    if winner in self.sub_queue:
                        self.sub_queue.remove(winner)
                    elif winner in self.queue:
                        self.queue.remove(winner)
                else:
                    self.say('The queue is empty BibleThump')
            else:
                self.say('Queue is not active. Enable it by typing !queue enable')

    def c_queue_pos(self, chatconn, username, extra_message):
        if self.queue_active:
            combined_queue = self.get_queue()
            check_self = True
            i = 1
            found = False

            if len(extra_message) > 0 and username in self.admins:
                check_self = False
                un_check = extra_message
            else:
                un_check = username

            for un in combined_queue:
                if un_check == un:
                    found = True
                    break
                i += 1

            if found:
                if check_self:
                    self.say('You are at position #{0} in the queue!'.format(i))
                else:
                    self.say('{0} is at position #{1} in the queue!'.format(un_check, i))
            else:
                if check_self:
                    self.say('You are not queued BibleThump')
                else:
                    self.say('{0} is not queued BibleThump'.format(un_check))

    def __init__(self, target, config):
        irc.client.SimpleIRCClient.__init__(self)
        self.target = target

        self.server = config['main']['server']
        self.port = int(config['main']['port'])
        self.nickname = config['main']['nickname']
        self.password = config['main']['password']

        self.commands['!queue join'] = self.c_queue_join
        self.commands['!queue remove'] = self.c_queue_remove
        self.commands['!queue add'] = self.c_queue_add
        self.commands['!queue enable'] = self.c_queue_enable
        self.commands['!queue on'] = self.c_queue_enable
        self.commands['!queue disable'] = self.c_queue_disable
        self.commands['!queue off'] = self.c_queue_disable
        self.commands['!queue clear'] = self.c_queue_clear
        self.commands['!queue list'] = self.c_queue_list
        self.commands['!queue show'] = self.c_queue_list
        self.commands['!queue pop'] = self.c_queue_pop
        self.commands['!queue winner'] = self.c_queue_pop
        self.commands['!queue next'] = self.c_queue_pop
        self.commands['!queue pos'] = self.c_queue_pos

    def on_mode(self, chatconn, event):
        if len(event.arguments) > 1:
            username = event.arguments[1].lower()
            if event.arguments[0] == '+o':
                if username not in self.admins:
                    self.admins.append(username)

    def on_welcome(self, chatconn, event):
        chatconn.send_raw('twitchclient 2')
        if irc.client.is_channel(self.target):
            chatconn.join(self.target)

    def on_disconnect(self, chatconn, event):
        sys.exit(0)

    def on_privmsg(self, chatconn, event):
        if len(event.arguments) > 0:
            split_msg = event.arguments[0].split(' ')

            if len(split_msg) == 3:
                username = split_msg[1].lower()
                if split_msg[0] == 'SPECIALUSER' and split_msg[2] == 'subscriber':
                    if username not in self.subscribers:
                        self.subscribers.append(username)
                elif split_msg[0] == 'SPECIALUSER' and split_msg[2] == 'subscriber':
                    if username not in self.subscribers:
                        self.subscribers.append(username)

    def say(self, message):
        print(message)
        self.connection.privmsg(self.target, message)

    def on_disconnect(self, chatconn, event):
        self.info('Disconnected... {0}'.format('|'.join(event.arguments)))
        self.connection.execute_delayed(self.reconnection_interval,
                                        self._connected_checker)

    def _connected_checker(self):
        if not self.connection.is_connected():
            self.connection.execute_delayed(self.reconnection_interval,
                                            self._connected_checker)

            self.connect()

    def on_join(self, chatconn, event):
        print('Joined {0}!'.format(event.target))

    def connect(self):
        try:
            irc.client.SimpleIRCClient.connect(self, self.server, self.port, self.nickname, self.password, self.nickname)
        except irc.client.ServerConnectionError:
            pass

    def on_pubmsg(self, chatconn, event):
        cur_time = time.time()
        username = event.source.user.lower()

        msg_parts = event.arguments[0].lower().split(' ')

        if len(msg_parts) > 0:
            tp_cmd = ' '.join(msg_parts[:2])
            if tp_cmd in self.commands:
                self.commands[tp_cmd](chatconn, username, ' '.join(msg_parts[2:]))
            elif msg_parts[0] in self.commands:
                self.commands[msg_parts[0]](chatconn, username, ' '.join(msg_parts[1:]))

    def quit(self):
        self.connection.quit("bye")
