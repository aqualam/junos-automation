from junos_sb import ClassJunosSB
import pytest


@pytest.fixture
def junos_connection():
    user = 'abc'
    pwd = 'password'
    hostname = 'test-junos'
    junos_obj = ClassJunosSB(user, pwd)
    junos_obj.connect(hostname)
    return junos_obj


def test_get_snat_cfg(junos_connection):
    assert junos_connection.get_snat_cfg() == {
                'entry': 2,
                'snat_entry': [
                    {'name': 'source-nat-rule', 'from': 'trust',
                     'to': 'untrust', 'action': 'interface'},
                    {'name': 'snat-rule', 'from': 'trust',
                     'to': 'test', 'action': 'pool_outbound'}
                ],
            }


def test_get_snat_pool_ip(junos_connection):
    assert junos_connection.get_snat_pool_ip('pool_outbound') == {
                'entry': 1, 'pool_name': 'pool_outbound',
                'address_range': ['1.2.3.4', '1.2.3.4'],
            }


def test_get_zone_interface(junos_connection):
    assert junos_connection.get_zone_interface('untrust') == {
                'entry': 2, 'zone': 'untrust',
                'interfaces': ['ge-0/0/15.0', 'ge-0/0/7.0'],
            }


def test_get_interface_ip(junos_connection):
    assert junos_connection.get_interface_ip('ge-0/0/10.0') == {
                'entry': 2, 'interface': 'ge-0/0/10.0',
                'ip': ['1.2.3.2', '2.3.4.5'],
            }

