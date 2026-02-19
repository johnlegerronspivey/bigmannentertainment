import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Frontend } from './constructs/frontend';
import { Auth } from './constructs/auth';
import { Api } from './constructs/api';
import { Lambdas } from './constructs/lambdas';
import { DynamoDBTables } from './constructs/dynamodb';
import { KinesisStack } from './constructs/kinesis';
import { EventBridgeStack } from './constructs/eventbridge';
import { QLDBStack } from './constructs/qldb';

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const frontend = new Frontend(this, 'Frontend');
    const auth = new Auth(this, 'Auth');
    const tables = new DynamoDBTables(this, 'DynamoDB');
    const kinesis = new KinesisStack(this, 'Kinesis');
    const lambdas = new Lambdas(this, 'Lambdas', { tables, kinesis, auth });
    const api = new Api(this, 'Api', { lambdas, auth });
    new EventBridgeStack(this, 'EventBridge', { lambdas });
    new QLDBStack(this, 'QLDB');
  }
}
