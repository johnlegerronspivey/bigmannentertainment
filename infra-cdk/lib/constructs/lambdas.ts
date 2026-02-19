import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';

export interface LambdasProps {
  tables: any;
  kinesis: any;
  auth: any;
}

export class Lambdas extends Construct {
  public readonly campaignHandler: lambda.Function;
  public readonly creativeHandler: lambda.Function;
  public readonly attributionHandler: lambda.Function;

  constructor(scope: Construct, id: string, props: LambdasProps) {
    super(scope, id);

    const commonRole = new iam.Role(this, 'LambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    });

    this.campaignHandler = new lambda.Function(this, 'CampaignHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'campaign.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../services/campaign')),
      role: commonRole,
      environment: {
        CAMPAIGNS_TABLE: props.tables.campaigns.tableName,
      },
    });

    this.creativeHandler = new lambda.Function(this, 'CreativeHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'creative.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../services/creative')),
      role: commonRole,
      environment: {
        CREATIVES_TABLE: props.tables.creatives.tableName,
      },
    });

    this.attributionHandler = new lambda.Function(this, 'AttributionHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'attribution.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../services/attribution')),
      role: commonRole,
      environment: {
        ATTRIBUTION_TABLE: props.tables.attribution.tableName,
        KINESIS_STREAM: props.kinesis.stream.streamName,
      },
    });

    props.tables.campaigns.grantReadWriteData(this.campaignHandler);
    props.tables.creatives.grantReadWriteData(this.creativeHandler);
    props.tables.attribution.grantReadWriteData(this.attributionHandler);
    props.kinesis.stream.grantWrite(this.attributionHandler);
  }
}
