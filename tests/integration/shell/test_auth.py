# -*- coding: utf-8 -*-
"""
    tests.integration.shell.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging

# Import 3rd-party libs
import pytest

# Import Salt libs
import salt.utils.platform

log = logging.getLogger(__name__)


USERA = "saltdev-auth"
USERA_PWD = "saltdev"
HASHED_USERA_PWD = "$6$SALTsalt$ZZFD90fKFWq8AGmmX0L3uBtS9fXL62SrTk5zcnQ6EkD6zoiM3kB88G1Zvs0xm/gZ7WXJRs5nsTBybUvGSqZkT."


@pytest.fixture(scope="module")
def saltdev_account(sminion):
    try:
        assert sminion.functions.user.add(USERA, createhome=False)
        assert sminion.functions.shadow.set_password(
            USERA, USERA_PWD if salt.utils.platform.is_darwin() else HASHED_USERA_PWD
        )
        assert USERA in sminion.functions.user.list_users()
        # Run tests
        yield
    finally:
        sminion.functions.user.delete(USERA, remove=True)


SALTOPS = "saltops"


@pytest.fixture(scope="module")
def saltops_group(sminion):
    try:
        assert sminion.functions.group.add(SALTOPS)
        # Run tests
        yield
    finally:
        sminion.functions.group.delete(SALTOPS)


USERB = "saltdev-adm"
USERB_PWD = USERA_PWD
HASHED_USERB_PWD = HASHED_USERA_PWD


@pytest.fixture(scope="module")
def saltadm_account(sminion, saltops_group):
    try:
        assert sminion.functions.user.add(USERB, groups=[SALTOPS], createhome=False)
        assert sminion.functions.shadow.set_password(
            USERB, USERB_PWD if salt.utils.platform.is_darwin() else HASHED_USERB_PWD
        )
        assert USERB in sminion.functions.user.list_users()
        # Run tests
        yield
    finally:
        sminion.functions.user.delete(USERB, remove=True)


@pytest.mark.skip_if_not_root
@pytest.mark.destructive_test
@pytest.mark.skip_on_windows
class TestUserAuth(object):
    """
    Test user auth mechanisms
    """

    @pytest.mark.slow_test(seconds=5)  # Test takes >1 and <=5 seconds
    def test_pam_auth_valid_user(self, salt_cli, saltdev_account):
        """
        test that pam auth mechanism works with a valid user
        """
        # test user auth against pam
        ret = salt_cli.run(
            "-a",
            "pam",
            "--username",
            USERA,
            "--password",
            USERA_PWD,
            "test.ping",
            minion_tgt="minion",
        )
        assert ret.exitcode == 0
        assert ret.json is True

    @pytest.mark.slow_test(seconds=10)  # Test takes >5 and <=10 seconds
    def test_pam_auth_invalid_user(self, salt_cli, saltdev_account):
        """
        test pam auth mechanism errors for an invalid user
        """
        ret = salt_cli.run(
            "-a",
            "pam",
            "--username",
            "nouser",
            "--password",
            "1234",
            "test.ping",
            minion_tgt="minion",
        )
        assert ret.stdout == "Authentication error occurred."


@pytest.mark.skip_if_not_root
@pytest.mark.destructive_test
class TestGroupAuth(object):
    """
    Test group auth mechanisms
    """

    @pytest.mark.slow_test(seconds=10)  # Test takes >5 and <=10 seconds
    def test_pam_auth_valid_group(self, salt_cli, saltadm_account):
        """
        test that pam auth mechanism works for a valid group
        """
        # test group auth against pam: saltadm is not configured in
        # external_auth, but saltops is and saldadm is a member of saltops
        ret = salt_cli.run(
            "-a",
            "pam",
            "--username",
            USERB,
            "--password",
            USERB_PWD,
            "test.ping",
            minion_tgt="minion",
        )
        assert ret.exitcode == 0
        assert ret.json is True
