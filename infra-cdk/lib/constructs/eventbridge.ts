import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';

export interface EventBridgeProps {
  lambdas: any;
}

export class EventBridgeStack extends Construct {
  public readonly bus: events.EventBus;

  constructor(scope: Construct, id: string, props: EventBridgeProps) {
    super(scope, id);

    this.bus = new events.EventBus(this, 'DoohEventBus', {
      eventBusName: 'dooh-events',
    });

    new events.Rule(this, 'CampaignCreatedRule', {
      eventBus: this.bus,
      eventPattern: {
        source: ['dooh.campaigns'],
        detailType: ['CampaignCreated'],
      },
      targets: [new targets.LambdaFunction(props.lambdas.campaignHandler)],
    });

    new events.Rule(this, 'ImpressionReceivedRule', {
      eventBus: this.bus,
      eventPattern: {
        source: ['dooh.impressions'],
        detailType: ['ImpressionReceived'],
      },
      targets: [new targets.LambdaFunction(props.lambdas.attributionHandler)],
    });
  }
}
