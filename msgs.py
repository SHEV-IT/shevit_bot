# coding: utf-8
from __future__ import unicode_literals
from .api import VkApi
import text as t


class MsgWorker:
    def __init__(self):
        self.states = {'menu': self.multiple_choice(t.WELCOME_MSG,
                                                    {'bill': 'bill',
                                                     'eduroam': 'eduroam',
                                                     'інше': 'etc'},
                                                    error_msg=t.WELCOME_MSG),
                       'error': self.show_text_and_exit(t.ERROR_MSG, wait_next_msg=False),
                       'bill': self.multiple_choice(t.BILL_MSG,
                                                    {'так': 'bill_first_fuck',
                                                     'ні': 'bill_already_pwned'}),
                       'bill_first_fuck': self.multiple_choice(t.BILL_FIRST_FUCK_MSG,
                                                               {'так': 'bill_first_router',
                                                                'ні': 'bill_first_account'}),
                       'bill_first_router': self.multiple_choice(t.BILL_FIRST_ROUTER_MSG,
                                                                 {'так': 'bill_first_config_router',
                                                                  'ні': 'bill_first_config_computer'}),
                       'bill_first_account': self.show_text_and_exit(t.BILL_FIRST_ACCOUNT_MSG),
                       'bill_first_config_router': self.multiple_choice(t.BILL_ROUTER_SETTINGS,
                                                                        {'так': 'bill_first_config_computer',
                                                                         'ні': 'bill_router_config_error'})}
        self.user_state = dict()

    def proceed(self, msg):
        sender = msg['user_id']
        state = self.user_state.get(sender, t.DEFAULT_STATE)
        state_f = self.states.get(state)

        new_state = state_f(sender, state, msg) if state_f else 'error'

        while new_state:
            self.user_state[sender] = new_state
            new_state_f = self.states.get(new_state)
            new_state = new_state_f(sender, new_state) if new_state_f else 'error'

    def multiple_choice(self, state_welcome_msg, choices_dict, error_msg=t.YES_NO_ERROR_MSG):
        def state_multiple_choice(sender, state, msg=None):
            if msg is None:
                VkApi.send_msg(sender, state_welcome_msg)
                return

            text = msg['body'].strip()
            if text == 'меню':
                return 'menu'

            for choice in choices_dict:
                if text == choice:
                    return choices_dict[choice]

            VkApi.send_msg(sender, error_msg)

        return state_multiple_choice

    def show_text_and_exit(self, state_msg, wait_next_msg=True):
        def state_text_exit(sender, state, msg=None):
            if msg is None:
                VkApi.send_msg(sender, state_msg)
                if not wait_next_msg:
                    return 'menu'

            return 'menu'

        return state_text_exit
