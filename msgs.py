# coding: utf-8
from __future__ import unicode_literals
from .api import VkApi
from projects.abstract import load_module


class MsgWorker:
    c = load_module('projects.shevit_bot.constants', globals())
    t = load_module('projects.shevit_bot.text', globals())
    vk_api = VkApi()

    def __init__(self):
        self.possible_states = set()
        self.states = {'menu': self.multiple_choice(self.t.WELCOME,
                                                    {'bill': 'bill',
                                                     'eduroam': 'eduroam',
                                                     'інше': 'etc',
                                                     'мапа': 'bill_show_icc'},
                                                    errors=self.t.WELCOME),
                       'error': self.show_text_and_exit(self.t.ERROR, wait_next=False),
                       'bill': self.multiple_choice(self.t.BILL,
                                                    {'так': 'check_bill_available',
                                                     'ні': 'bill_already_pwned'}),
                       'check_bill_available': self.multiple_choice(self.t.BILL_FIRST_ROOM_CABLE,
                                                                    {'так': 'bill_first_fuck',
                                                                     'ні': 'bill_cable_not_found'}),
                       'bill_first_fuck': self.multiple_choice(self.t.BILL_FIRST_FUCK,
                                                               {'так': 'bill_first_router',
                                                                'ні': 'bill_first_account',
                                                                'не знаю': 'bill_check_if_account'}),
                       'bill_cable_not_found': self.multiple_choice(self.t.BILL_CABLE_NOT_FOUND,
                                                                    {'так': 'bill_first_fuck',
                                                                     'ні': 'bill_no_cable_redirect'}),
                       'bill_no_cable_redirect': self.show_text_and_exit([self.t.BILL_NO_CABLE_REDIRECT,
                                                                          self.t.BILL_ICC]),
                       'bill_first_router': self.multiple_choice(self.t.BILL_FIRST_ROUTER,
                                                                 {'так': 'bill_first_config_router',
                                                                  'ні': 'bill_first_computer'}),
                       'bill_first_config_router': self.multiple_choice(self.t.BILL_ROUTER_SETTINGS,
                                                                        {'так': 'bill_should_work',
                                                                         'ні': 'bill_router_config_error'}),
                       'bill_router_config_error': self.show_text_and_exit([self.t.BILL_ROUTER_CONFIG_ERROR,
                                                                            self.t.BILL_ADMIN_CONTACTS]),
                       'bill_first_computer': self.multiple_choice(self.t.BILL_FIRST_COMPUTER,
                                                                   {'так': 'bill_first_config_computer',
                                                                    'ні': 'bill_should_work'}),
                       'bill_first_config_computer': self.multiple_choice(self.t.BILL_COMPUTER_SETTINGS,
                                                                          {'так': 'bill_should_work',
                                                                           'ні': 'bill_computer_config_error'}),
                       'bill_computer_config_error': self.show_text_and_exit([self.t.BILL_COMPUTER_CONFIG_ERROR,
                                                                              self.t.BILL_ICC,
                                                                              self.t.BILL_ADMIN_CONTACTS]),
                       'bill_should_work': self.show_text_and_exit(self.t.BILL_SHOULD_WORK),
                       'bill_first_account': self.multiple_choice([self.t.BILL_REGISTER,
                                                                   self.t.BILL_ICC],
                                                                  {'так': 'bill_first_pay'},
                                                                  errors=False, error_state='menu'),
                       'bill_first_pay': self.show_text_and_exit(self.t.BILL_PAY, 'bill_first_pay_check'),
                       'bill_first_pay_check': self.multiple_choice(self.t.BILL_PAY_CHECK,
                                                                    {'так': 'bill_first_router',
                                                                     'ні': 'bill_first_pay_failed'}),
                       'bill_first_pay_failed': self.show_text_and_exit(self.t.BILL_PAY_FAILED),
                       'bill_check_if_account': self.show_text_and_exit(self.t.BILL_CHECK_IF_ACCOUNT,
                                                                        exit_state='bill_first_fuck', wait_next=False),
                       'bill_show_icc': self.show_text_and_exit(self.t.BILL_ICC)}
        self.user_state = dict()
        errors = self.possible_states - set(self.states.keys())
        if errors and self.c.ONLOAD_CHECK:
            print 'errors:', errors
            raise NotImplementedError

    def proceed(self, msg):
        sender = msg['user_id']
        if self.c.DEBUG and sender not in self.c.ADMINS:
            return

        state = self.user_state.get(sender, self.t.DEFAULT_STATE)
        state_f = self.states.get(state)

        new_state = state_f(sender, state, msg) if state_f else 'error'

        while new_state:
            self.user_state[sender] = new_state
            new_state_f = self.states.get(new_state)
            new_state = new_state_f(sender, new_state) if new_state_f else 'error'

    def multiple_choice(self, state_welcomes, choices_dict, errors=t.YES_NO_ERROR, error_state=None):
        self.register_states(choices_dict.values())

        def state_multiple_choice(sender, state, msg=None):
            if msg is None:
                if type(state_welcomes) is not list:
                    self.vk_api.send_msg(sender, state_welcomes)
                else:
                    for msg in state_welcomes:
                        self.vk_api.send_msg(sender, msg)
                return

            text = msg['body'].strip()
            if text == 'меню':
                return 'menu'

            for choice in choices_dict:
                if text == choice:
                    return choices_dict[choice]

            if errors:
                if type(errors) is not list:
                    self.vk_api.send_msg(sender, errors)
                else:
                    for msg in errors:
                        self.vk_api.send_msg(sender, msg)
            if error_state:
                return error_state

        return state_multiple_choice

    def show_text_and_exit(self, states, exit_state='menu', wait_next=True):
        self.register_states([exit_state])

        def state_text_exit(sender, state, msg=None):
            if msg is None:
                if type(states) is not list:
                    self.vk_api.send_msg(sender, states)
                else:
                    for msg in states:
                        self.vk_api.send_msg(sender, msg)
                if not wait_next:
                    return exit_state
                return

            return exit_state

        return state_text_exit

    def register_states(self, state_names):
        self.possible_states.update(state_names)
