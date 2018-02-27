# aws-es-mackerel

AWS Elasticsearch Serviceのストレージ使用状況をMackerelのサービスメトリックとして投稿するLambda Functionです。

定期的にメトリックスを投稿するため、CloudWatchのスケジュールを使用する予定です。

### Prepare

- SAM Local

    [AWS SAM Local](https://github.com/awslabs/aws-sam-local)を使用しています。

    [Installation](https://github.com/awslabs/aws-sam-local#installation)を参考にしてインストールしておきます。

- Python

    Lambdaの実行環境としてPython3.6を選択しています。
    ユニットテスト（doctest）やIDEの入力補完の恩恵を受けるためにセットアップしておきます。


    venvで環境を作るとグローバルの環境を汚さなくて便利です。

    requirements.txtに必要なライブラリを記載しておきます。


```shell
# Python3は既にインストールしてある前提
$ python3 --version
Python 3.6.x

$ python3 -m venv ./venv
$ source ./venv/bin/activate
(venv) $ pip install --upgrade -r ./requirements.txt
```

### Usage

`env.json.sample` を `env.json` にコピーして内容を設定する。

ローカルで実行するには以下のコマンドを実行します。

```shell
$ sam local generate-event schedule | sam local invoke PostEsMetrics -t src/template.yaml -n env.json
# or まったく同じ内容を以下のシェルスクリプトに記載しているので↓でもOK
$ ./kick.sh
```


### Tests

ローカルでユニットテストを行う場合は以下のコマンドを実行します。


```shell
(venv) $ python -m doctest src/lambda_function.py -v
```


### deploy

SAM Localを使用してデプロイする

```shell
$ cd src
$ sam package --template-file template.yaml --s3-bucket <YOUR-BUCKET-NAME-HERE> --s3-prefix <DIR-NAME-HERE> --output-template-file package.yaml

Uploading to <prefix-id> nnnn / nnnn (100.00%)
Successfully packaged artifacts and wrote output template to file package.yaml.
Execute the following command to deploy the packaged template
aws cloudformation deploy --tempalte-file package.yaml --stack-name <YOUR STACK NAME>

$ sam deploy --template-file package.yaml --stack-name <YOUR STACK NAME> --capabilities CAPABILITY_IAM

Waiting for changeset to be created..
Waiting for stack create/update to complete
Successfully created/updated stack - <YOUR STACK NAME>
```

##### 以下初回デプロイ時のみ

* Lambdaコンソールに各環境変数（`MACKEREL_API_KEY`, `MACKEREL_SERVICE_NAME`, `ELASTICSEARCH_DOMAIN_NAME`, `ELASTICSEARCH_CLIENT_ID`）が登録されているので値を設定する。
* Lambdaの実行ロールにCloudWatchメトリックの取得ができる権限を付ける。
    - IAMコンソールから`cloudwatch:GetMetricStatistics`を追加してやる
* Lambdaコンソールの「トリガーの追加」から`CloudWatch Events`のトリガーを設定する。
