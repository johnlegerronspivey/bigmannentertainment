import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cognito from 'aws-cdk-lib/aws-cognito';

export interface ApiProps {
  lambdas: any;
  auth: any;
}

export class Api extends Construct {
  public readonly api: apigateway.RestApi;

  constructor(scope: Construct, id: string, props: ApiProps) {
    super(scope, id);

    this.api = new apigateway.RestApi(this, 'DoohApi', {
      restApiName: 'DOOH Platform API',
      description: 'Programmatic DOOH platform REST API',
      deployOptions: { stageName: 'v1' },
    });

    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'CognitoAuth', {
      cognitoUserPools: [props.auth.userPool],
    });

    const campaigns = this.api.root.addResource('campaigns');
    campaigns.addMethod('GET', new apigateway.LambdaIntegration(props.lambdas.campaignHandler), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    campaigns.addMethod('POST', new apigateway.LambdaIntegration(props.lambdas.campaignHandler), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    const creatives = this.api.root.addResource('creatives');
    creatives.addMethod('GET', new apigateway.LambdaIntegration(props.lambdas.creativeHandler), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
    creatives.addMethod('POST', new apigateway.LambdaIntegration(props.lambdas.creativeHandler), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });

    const attribution = this.api.root.addResource('attribution');
    attribution.addMethod('GET', new apigateway.LambdaIntegration(props.lambdas.attributionHandler), {
      authorizer,
      authorizationType: apigateway.AuthorizationType.COGNITO,
    });
  }
}
