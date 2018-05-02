from twisted.trial import unittest

from lbrynet.wallet.coins.lbc import LBC
from lbrynet.wallet.manager import WalletManager
from lbrynet.wallet.account import Account, VanityAccount, account_from_dict


class TestAccountBase:
    ACCOUNT_CLASS = None

    def setUp(self):
        ledger = WalletManager().get_or_create_ledger(LBC.get_id())
        self.coin = LBC(ledger)

    def test_generate_account(self):
        account = self.ACCOUNT_CLASS.generate(self.coin)
        self.assertEqual(account.coin, self.coin)
        self.assertIsNotNone(account.seed)
        self.assertEqual(account.public_key.coin, self.coin)
        self.assertEqual(account.private_key.public_key, account.public_key)

        self.assertEqual(len(account.receiving_keys.child_keys), 0)
        self.assertEqual(len(account.receiving_keys.addresses), 0)
        self.assertEqual(len(account.change_keys.child_keys), 0)
        self.assertEqual(len(account.change_keys.addresses), 0)

        account.ensure_enough_addresses()
        self.assertEqual(len(account.receiving_keys.child_keys), 20)
        self.assertEqual(len(account.receiving_keys.addresses), 20)
        self.assertEqual(len(account.change_keys.child_keys), 6)
        self.assertEqual(len(account.change_keys.addresses), 6)

    def test_generate_account_from_seed(self):
        account = self.ACCOUNT_CLASS.from_seed(
            self.coin,
            "carbon smart garage balance margin twelve chest sword toast envelope bottom stomach ab"
            "sent"
        )
        self.assertEqual(
            account.private_key.extended_key_string(),
            'LprvXPsFZUGgrX1X9HiyxABZSf6hWJK7kHv4zGZRyyiHbBq5Wu94cE1DMvttnpLYReTPNW4eYwX9dWMvTz3PrB'
            'wwbRafEeA1ZXL69U2egM4QJdq'
        )
        self.assertEqual(
            account.public_key.extended_key_string(),
            'Lpub2hkYkGHXktBhLpwUhKKogyuJ1M7Gt9EkjFTVKyDqZiZpWdhLuCoT1eKDfXfysMFfG4SzfXXcA2SsHzrjHK'
            'Ea5aoCNRBAhjT5NPLV6hXtvEi'
        )
        self.assertEqual(
            account.receiving_keys.generate_next_address(),
            'bCqJrLHdoiRqEZ1whFZ3WHNb33bP34SuGx'
        )
        private_key = account.get_private_key_for_address('bCqJrLHdoiRqEZ1whFZ3WHNb33bP34SuGx')
        self.assertEqual(
            private_key.extended_key_string(),
            'LprvXTnmVLXGKvRGo2ihBE6LJ771G3VVpAx2zhTJvjnx5P3h6iZ4VJX8PvwTcgzJZ1hqXX61Wpn4pQoP6n2wgp'
            'S8xjzCM6H2uGzCXuAMy5H9vtA'
        )
        self.assertIsNone(account.get_private_key_for_address('BcQjRlhDOIrQez1WHfz3whnB33Bp34sUgX'))

    SAVED_ACCOUNT_DATA = {
        'seed':
            "carbon smart garage balance margin twelve chest sword toast envelope bottom stomac"
            "h absent",
        'encrypted': False,
        'private_key':
            'LprvXPsFZUGgrX1X9HiyxABZSf6hWJK7kHv4zGZRyyiHbBq5Wu94cE1DMvttnpLYReTPNW4eYwX9dWMvTz3PrB'
            'wwbRafEeA1ZXL69U2egM4QJdq',
        'public_key':
            'Lpub2hkYkGHXktBhLpwUhKKogyuJ1M7Gt9EkjFTVKyDqZiZpWdhLuCoT1eKDfXfysMFfG4SzfXXcA2SsHzrjHK'
            'Ea5aoCNRBAhjT5NPLV6hXtvEi',
        'receiving_gap': 10,
        'receiving_keys': [
            '02c68e2d1cf85404c86244ffa279f4c5cd00331e996d30a86d6e46480e3a9220f4',
            '03c5a997d0549875d23b8e4bbc7b4d316d962587483f3a2e62ddd90a21043c4941'
        ],
        'change_gap': 10,
        'change_keys': [
            '021460e8d728eee325d0d43128572b2e2bacdc027e420451df100cf9f2154ea5ab'
        ],
        'is_vanity': False,
    }

    def test_load_and_save_account(self):
        account = self.ACCOUNT_CLASS.from_dict(self.coin, self.SAVED_ACCOUNT_DATA)

        self.assertEqual(len(account.receiving_keys.addresses), 2)
        self.assertEqual(
            account.receiving_keys.addresses[0],
            'bCqJrLHdoiRqEZ1whFZ3WHNb33bP34SuGx'
        )
        self.assertEqual(len(account.change_keys.addresses), 1)
        self.assertEqual(
            account.change_keys.addresses[0],
            'bFpHENtqugKKHDshKFq2Mnb59Y2bx4vKgL'
        )

        self.assertDictEqual(dict(self.SAVED_ACCOUNT_DATA, coin='lbc_mainnet'), account.to_dict())

class TestAccount(TestAccountBase, unittest.TestCase):
    ACCOUNT_CLASS = Account

    def test_load_correct_class(self):
        account = account_from_dict(self.coin, self.SAVED_ACCOUNT_DATA)
        self.assertEqual(account.__class__, Account)

class TestVanityAccount(TestAccountBase, unittest.TestCase):
    ACCOUNT_CLASS = VanityAccount

    def test_load_correct_class(self):
        account = account_from_dict(self.coin, dict(self.SAVED_ACCOUNT_DATA, is_vanity=True))
        self.assertEqual(account.__class__, VanityAccount)

    def test_create_from_private_key(self):
        account = VanityAccount.from_private_key(
            self.coin,
            'LprvXPsFZUGgrX1X9HiyxABZSf6hWJK7kHv4zGZRyyiHbBq5Wu94cE1DMvttnpLYReTPNW4eYwX9dWMvTz3PrB'
            'wwbRafEeA1ZXL69U2egM4QJdq'
        )
        self.assertEqual(
            account.private_key.extended_key_string(),
            'LprvXPsFZUGgrX1X9HiyxABZSf6hWJK7kHv4zGZRyyiHbBq5Wu94cE1DMvttnpLYReTPNW4eYwX9dWMvTz3PrB'
            'wwbRafEeA1ZXL69U2egM4QJdq'
        )
        self.assertEqual(account.seed, None)
        self.assertEqual(
            account.public_key.extended_key_string(),
            'Lpub2hkYkGHXktBhLpwUhKKogyuJ1M7Gt9EkjFTVKyDqZiZpWdhLuCoT1eKDfXfysMFfG4SzfXXcA2SsHzrjHK'
            'Ea5aoCNRBAhjT5NPLV6hXtvEi'
        )
        self.assertEqual(
            account.receiving_keys.generate_next_address(),
            'bCqJrLHdoiRqEZ1whFZ3WHNb33bP34SuGx'
        )
        private_key = account.get_private_key_for_address('bCqJrLHdoiRqEZ1whFZ3WHNb33bP34SuGx')
        self.assertEqual(
            private_key.extended_key_string(),
            'LprvXTnmVLXGKvRGo2ihBE6LJ771G3VVpAx2zhTJvjnx5P3h6iZ4VJX8PvwTcgzJZ1hqXX61Wpn4pQoP6n2wgp'
            'S8xjzCM6H2uGzCXuAMy5H9vtA'
        )
        self.assertIsNone(account.get_private_key_for_address('BcQjRlhDOIrQez1WHfz3whnB33Bp34sUgX'))
