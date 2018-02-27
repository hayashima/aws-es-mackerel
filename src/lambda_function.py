import json
import os
from calendar import timegm
from datetime import datetime, timedelta
from logging import getLogger, DEBUG, INFO
from urllib.request import Request, urlopen

import boto3

MACKEREL_API_PATH = 'https://api.mackerelio.com/api/v0/services/{service_name}/tsdb'

os.environ['TZ'] = 'Asia/Tokyo'
logger = getLogger(__name__)
if os.getenv("AWS_SAM_LOCAL"):
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)


def load_es_metrics(kick_time: datetime) -> list:
    """
    AWSのElasticsearch Serviceのストレージ空き容量をCloudWatchから取得する

    :param kick_time: Lambdaバッチの起動時刻
    :return: 取得したmetricsのリスト
    """

    end_time = kick_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_time = (kick_time + timedelta(minutes=-10)).strftime('%Y-%m-%dT%H:%M:%SZ')
    logger.debug(f'Load metrics from {start_time} to {end_time}')

    client = boto3.client('cloudwatch', 'ap-northeast-1')
    response = client.get_metric_statistics(
        Namespace='AWS/ES',
        MetricName='FreeStorageSpace',
        Dimensions=[
            {'Name': 'DomainName', 'Value': os.getenv('ELASTICSEARCH_DOMAIN_NAME', '')},
            {'Name': 'ClientId', 'Value': os.getenv('ELASTICSEARCH_CLIENT_ID', '')}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Average'],
        Unit='Megabytes'
    )
    if str(response['ResponseMetadata']['HTTPStatusCode']) != "200":
        return []
    return sorted(response['Datapoints'], key=lambda d: d['Timestamp'], reverse=True)


def convert_metrics_bytes(value: float, unit: str):
    """
    CloudWatchから取得したストレージ容量の単位をBytesに変換する
    Mackerelのグラフの単位をBytesに指定するため
    :param value: metric値
    :param unit: 単位
    :return: bytes換算したmetric値

    >>> convert_metrics_bytes(1, 'Hoge')
    1
    >>> convert_metrics_bytes(1, 'Kilobytes')
    1000
    >>> convert_metrics_bytes(1, 'Megabytes')
    1000000
    >>> convert_metrics_bytes(1, 'Gigabytes')
    1000000000
    >>> convert_metrics_bytes(1, 'Terabytes')
    1000000000000
    """

    if unit == 'Kilobytes':
        value *= 1_000
    elif unit == 'Megabytes':
        value *= 1_000_000
    elif unit == 'Gigabytes':
        value *= 1_000_000_000
    elif unit == 'Terabytes':
        value *= 1_000_000_000_000
    return value


def convert_service_metrics(metric_name: str, metric_value_name: str, metrics: list):
    """
    CloudWatchから取得したメトリックをMackerelにポストするサービスメトリックの形式に変換する

    :param metric_name: Mackerelのグラフに表示するメトリック名
    :param metric_value_name: CloudWatchのメトリック名
    :param metrics: CloudWatchから取得したメトリックのリスト
    :return: Mackerelにポストするサービスメトリックのリスト
    """
    return [
        {'name': metric_name,
         'time': timegm(m['Timestamp'].timetuple()),
         'value': convert_metrics_bytes(m[metric_value_name], m['Unit'])}
        for m in metrics
    ]


def post_service_metrics(metrics):
    """
    Mackerelにサービスメトリックをポストする

    :param metrics: Mackerelにポストするメトリックのリスト
    :return: 処理結果
    """
    path = MACKEREL_API_PATH.format(service_name=os.getenv('MACKEREL_SERVICE_NAME', ''))
    logger.debug(path)
    logger.debug(metrics)
    try:
        request = Request(path, json.dumps(metrics).encode('utf-8'))
        request.add_header('X-Api-Key', os.getenv('MACKEREL_API_KEY', ''))
        request.add_header('Content-Type', 'application/json')

        return urlopen(request).read().decode('utf-8')
    except Exception as e:
        logger.exception(e)
        return {'success': False}


def lambda_handler(event, context):
    kick_time = datetime.utcnow()
    logger.info('start!')
    metrics = load_es_metrics(kick_time)
    converted_metrics = convert_service_metrics('custom.ES.FreeStorage', 'Average', metrics)
    return post_service_metrics(converted_metrics)
