import { Construct } from 'constructs';
import * as qldb from 'aws-cdk-lib/aws-qldb';
import * as cdk from 'aws-cdk-lib';

export class QLDBStack extends Construct {
  public readonly ledger: qldb.CfnLedger;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.ledger = new qldb.CfnLedger(this, 'AuditLedger', {
      name: 'dooh-audit-ledger',
      permissionsMode: 'STANDARD',
      deletionProtection: true,
    });
  }
}
