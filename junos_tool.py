#!/usr/bin/env python3

from jnpr.junos import Device
import sys


class ClassJunosTool(object):
    """ClassJunosTool class can retrieve JUNOS device configuration
    """

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.user_pwd = password
        self.conn = None

    def connect(self, host):
        """Initializes connection to JUNOS device

        Args:
            host: JUNOS device hostname

        Raises:
            Exception: An error occurred connecting JUNOS device
        """
        try:
            self.conn = Device(host=host, user=self.user_name,
                               passwd=self.user_pwd)
            self.conn.open()
        except Exception as err:
            print(err)
            sys.exit(1)

    def close(self):
        """Terminates connection to JUNOS device"""
        self.conn.close()

    def get_snat_cfg(self):
        """Get Source NAT configuration from JUNOS device

        Retrieve Source NAT config and return SNAT rule in dictionary format

        Returns:
            A dict mapping keys to a SNAT rule entry. For example:

            {'entry': 2,
            'snat_entry': [
                {'name': 'source-nat-rule', 'from': 'trust',
                'to': 'untrust', 'action': 'interface'},
                {'name': 'snat-rule', 'from': 'trust',
                'to': 'test', 'action': 'pool_outbound'}
                ]
            }

        Raises:
            KeyError: An error occurred accessing
                snat_summary['ssg-source-nat-summary-information']
                [0]['ssg-source-rule-entry']
                list when no SNAT cfg on device
        """
        snat_summary = self.conn.rpc.retrieve_source_nat_summary({'format': 'json'})
        return_snat_cfg_dict = {}
        try:
            snat_rule_list = []
            for snat_entry in snat_summary['ssg-source-nat-summary-information']\
                    [0]['ssg-source-rule-entry']:
                snat_from = snat_entry['ssg-source-rule-context-from'][0]['data']
                snat_to = snat_entry['ssg-source-rule-context-to'][0]['data']
                snat_action = snat_entry['ssg-source-rule-action'][0]['data']
                snat_name = snat_entry['ssg-source-rule-name'][0]['data']
                snat_rule = {
                    'name': snat_name,
                    'from': snat_from,
                    'to': snat_to,
                    'action': snat_action,
                }
                snat_rule_list.append(snat_rule)
            return_snat_cfg_dict = {
                'entry': len(snat_rule_list),
                'snat_entry': snat_rule_list}
        except KeyError:
            print('No SNAT config')
            return_snat_cfg_dict ={'entry': 0, 'snat_cfg': []}

        return return_snat_cfg_dict

    def get_snat_pool_ip(self, snat_pool):
        """Get Source NAT pool config from JUNOS device

        Retrieve Source NAT pool config and return SNAT pool ip addresses
        in dictionary format

        Args:
            snat_pool: SNAT pool name

        Returns:
            A dict mapping keys to a SNAT pool entry. For example:

            {'entry': 1, 'pool_name': 'pool_outbound',
            'address_range': ['1.2.3.4', '1.2.3.4']}

        Raises:
            KeyError: An error occurred accessing
                snat_pool_info['source-nat-pool-detail-information']
                [0]['source-nat-pool-info-entry'][0]['pool-name'][0]['data']
                list when no SNAT pool cfg on device
        """
        snat_pool_info = self.conn.rpc.retrieve_source_nat_pool_information(
            {'format': 'json'}, all=True)
        return_snat_pool_dict = {}
        try:
            pool_name = snat_pool_info['source-nat-pool-detail-information']\
                [0]['source-nat-pool-info-entry'][0]['pool-name'][0]['data']
            if snat_pool in pool_name:
                pool_detail = snat_pool_info['source-nat-pool-detail-information']\
                    [0]['source-nat-pool-info-entry']\
                    [0]['source-pool-address-range'][0]
                address_low = pool_detail['address-range-low'][0]['data']
                address_high = pool_detail['address-range-high'][0]['data']
                pool_list = [address_low, address_high]
                return_snat_pool_dict = {'entry': 1,
                                         'pool_name': snat_pool,
                                         'address_range': pool_list}
        except KeyError:
            print('No {} can be found!'.format(snat_pool))
            return_snat_pool_dict = {'entry': 0, 'pool_name': snat_pool,
                                     'address_range': []}

        return return_snat_pool_dict

    def get_zone_interface(self, zone):
        """Get zone interfaces from JUNOS device

        Retrieve zone interfaces and return interface name
        in dictionary format

        Args:
            zone: Security zone name

        Returns:
            A dict mapping keys to a zone interfaces entry. For example:

            {'entry': 2, 'zone': 'untrust',
            'interfaces': ['ge-0/0/15.0', 'ge-0/0/7.0']}

        Raises:
            KeyError: An error occurred accessing
                zone_info['zones-information'][0]['zones-security'][0]
                ['zones-security-interfaces'][0]
                ['zones-security-interface-name']
                list when no zone can be found on device
        """
        zone_info = self.conn.rpc.get_zones_information(
                                {'format': 'json'},
                                get_zones_named_information=zone,
                            )
        return_zone_interfaces_dict = {}
        try:
            security_interfaces = zone_info['zones-information'][0]\
                ['zones-security'][0]['zones-security-interfaces'][0]\
                ['zones-security-interface-name']
            interfaces_list = []
            for items in security_interfaces:
                interfaces_list.append(items['data'])
            return_zone_interfaces_dict = {'entry': len(interfaces_list),
                                           'zone': zone,
                                           'interfaces': interfaces_list}
        except KeyError:
            print('Security {} zone does not exist!'.format(zone))
            return_zone_interfaces_dict = {'entry': 0, 'zone': zone,
                                           'interface': []}

        return return_zone_interfaces_dict

    def get_interface_ip(self, interface):
        """Get interfaces IP address from JUNOS device

        Retrieve interfaces IP address and return IP address list
        in dictionary format

        Args:
            interface: Device interface name

        Returns:
            A dict mapping keys to an interfaces IP address entry.
            For example:

            {'entry': 2, 'interface': 'ge-0/0/10.0',
            'ip': ['1.2.3.2', '2.3.4.5']}

        Raises:
            KeyError: An error occurred accessing
                interface_info['interface-information'][0]
                ['logical-interface'][0]['address-family'][0]
                ['interface-address']
                list when no zone can be found on device
        """
        interface_info = self.conn.rpc.get_interface_information(
            {'format': 'json'}, interface_name=interface, terse=True)
        ip_list = []
        try:
            logical_interface = interface_info['interface-information'][0]\
                ['logical-interface'][0]['address-family'][0]\
                ['interface-address']
            for items in logical_interface:
                ip_list.append(items['ifa-local'][0]['data'].split('/')[0])
            interface_ip = {'entry': len(ip_list),
                            'interface': interface,
                            'ip': ip_list}
        except KeyError:
            print('No IP can be found on {}'.format(interface))
            interface_ip = {'entry': len(ip_list),
                            'interface': interface,
                            'ip': ip_list
                            }

        return interface_ip


def main():
    pass


if __name__ == '__main__':
        sys.exit(main())
