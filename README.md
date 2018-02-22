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
$ AWS_REGION=ap-northeast-1 sam local generate_event schedule | sam local invoke --template src/template.yaml --env-vars env.json
```


### Tests

ローカルでユニットテストを行う場合は以下のコマンドを実行します。


```shell
(venv) $ python -m doctest src/lambda_function.py -v
```
