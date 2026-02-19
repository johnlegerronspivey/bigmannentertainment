import { Construct } from 'constructs';
import * as kinesis from 'aws-cdk-lib/aws-kinesis';
import * as cdk from 'aws-cdk-lib';

export class KinesisStack extends Construct {
  public readonly stream: kinesis.Stream;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.stream = new kinesis.Stream(this, 'ImpressionStream', {
      shardCount: 2,
      retentionPeriod: cdk.Duration.hours(24),
    });
  }
}
