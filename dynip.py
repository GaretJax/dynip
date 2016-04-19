import datetime

import requests

import click

from boto3.session import Session


def get_external_ip():
    r = requests.get('http://ipecho.net/plain')
    r.raise_for_status()
    return r.text.strip()


def get_hosted_zone_id(client, hosted_zone):
    hosted_zones = client.list_hosted_zones_by_name(DNSName=hosted_zone)
    assert len(hosted_zones['HostedZones']) == 1
    return hosted_zones['HostedZones'][0]['Id']


def update_ip(session, subdomain, ip, ttl):
    now = datetime.datetime.utcnow().replace(microsecond=0)

    client = session.client('route53')

    hosted_zone_id = get_hosted_zone_id(client, subdomain.split('.', 1)[1])

    client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': subdomain,
                    'Type': 'A',
                    'TTL': ttl,
                    'ResourceRecords': [{
                        'Value': ip,
                    }],
                },
            }, {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': subdomain,
                    'Type': 'TXT',
                    'TTL': ttl,
                    'ResourceRecords': [{
                        'Value': '"last-update={}"'.format(now.isoformat()),
                    }],
                },
            }],
        },
    )


@click.command()
@click.option('--aws-access-key-id', '-k', envvar='AWS_ACCESS_KEY_ID')
@click.option('--aws-secret-access-key', '-s', envvar='AWS_SECRET_ACCESS_KEY')
@click.option('--ttl', default=60, type=int)
@click.argument('subdomain')
@click.argument('ip', required=False)
def main(aws_access_key_id, aws_secret_access_key, ttl, subdomain, ip):
    session = Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    if not ip:
        ip = get_external_ip()

    update_ip(session, subdomain, ip, ttl)


if __name__ == '__main__':
    main()
