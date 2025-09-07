import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as cloudwatchActions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as certificatemanager from 'aws-cdk-lib/aws-certificatemanager';
import * as route53 from 'aws-cdk-lib/aws-route53';
import * as targets from 'aws-cdk-lib/aws-route53-targets';
import { Construct } from 'constructs';

export interface BigMannEnvironmentStackProps extends cdk.StackProps {
  environment: string;
  domain: string;
  certificateArn?: string;
  createCertificate?: boolean;
}

export class BigMannEnvironmentStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly cluster: ecs.Cluster;
  public readonly loadBalancer: elbv2.ApplicationLoadBalancer;
  public readonly fastapiRepository: ecr.Repository;
  public readonly frontendBucket: s3.Bucket;
  public readonly distribution: cloudfront.Distribution;
  public readonly alertTopic: sns.Topic;
  public readonly certificate?: certificatemanager.Certificate;
  public readonly hostedZone?: route53.IHostedZone;

  constructor(scope: Construct, id: string, props: BigMannEnvironmentStackProps) {
    super(scope, id, props);

    // VPC Configuration
    this.vpc = new ec2.Vpc(this, `${props.environment}-VPC`, {
      maxAzs: props.environment === 'production' ? 3 : 2,
      natGateways: props.environment === 'production' ? 2 : 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
      ],
    });

    // ECR Repository for FastAPI
    this.fastapiRepository = new ecr.Repository(this, `${props.environment}-FastAPI-Repo`, {
      repositoryName: `bigmann-fastapi-${props.environment}`,
      imageScanOnPush: true,
      lifecycleRules: [{
        maxImageCount: props.environment === 'production' ? 10 : 5,
      }],
    });

    // ECS Cluster
    this.cluster = new ecs.Cluster(this, `${props.environment}-Cluster`, {
      vpc: this.vpc,
      containerInsights: props.environment !== 'development',
      clusterName: `bigmann-${props.environment}-cluster`,
    });

    // Application Load Balancer
    this.loadBalancer = new elbv2.ApplicationLoadBalancer(this, `${props.environment}-ALB`, {
      vpc: this.vpc,
      internetFacing: true,
      loadBalancerName: `bigmann-${props.environment}-alb`,
    });

    // S3 Bucket for React App
    this.frontendBucket = new s3.Bucket(this, `${props.environment}-Frontend-Bucket`, {
      bucketName: `bigmann-frontend-${props.environment}-${this.account}`,
      websiteIndexDocument: 'index.html',
      websiteErrorDocument: 'error.html',
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: props.environment === 'production' ? 
        cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
      versioned: props.environment === 'production',
    });

    // CloudFront Origin Access Identity
    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, `${props.environment}-OAI`, {
      comment: `OAI for ${props.environment} environment`,
    });

    // Grant CloudFront read access to S3 bucket
    this.frontendBucket.grantRead(originAccessIdentity);

    // CloudFront Distribution
    this.distribution = new cloudfront.Distribution(this, `${props.environment}-Distribution`, {
      defaultBehavior: {
        origin: new origins.S3Origin(this.frontendBucket, {
          originAccessIdentity: originAccessIdentity,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      additionalBehaviors: {
        '/api/*': {
          origin: new origins.LoadBalancerV2Origin(this.loadBalancer, {
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY,
          }),
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        },
      },
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
      priceClass: props.environment === 'production' ? 
        cloudfront.PriceClass.PRICE_CLASS_ALL : cloudfront.PriceClass.PRICE_CLASS_100,
    });

    // SNS Topic for Alerts
    this.alertTopic = new sns.Topic(this, `${props.environment}-Alerts`, {
      topicName: `bigmann-${props.environment}-alerts`,
      displayName: `Big Mann Entertainment ${props.environment} Alerts`,
    });

    // CloudWatch Log Groups
    const backendLogGroup = new logs.LogGroup(this, `${props.environment}-Backend-Logs`, {
      logGroupName: `/ecs/bigmann-${props.environment}-backend`,
      retention: this.getLogRetention(props.environment),
      removalPolicy: props.environment === 'production' ? 
        cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    const frontendLogGroup = new logs.LogGroup(this, `${props.environment}-Frontend-Logs`, {
      logGroupName: `/cloudfront/bigmann-${props.environment}-frontend`,
      retention: this.getLogRetention(props.environment),
      removalPolicy: props.environment === 'production' ? 
        cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
    });

    // CloudWatch Alarms
    this.createCloudWatchAlarms(props.environment);

    // Secrets Manager setup
    this.createSecretsManager(props.environment);

    // IAM Roles
    this.createIAMRoles(props.environment);

    // Outputs
    new cdk.CfnOutput(this, 'VPCId', {
      value: this.vpc.vpcId,
      exportName: `${props.environment}-VPC-ID`,
    });

    new cdk.CfnOutput(this, 'ClusterArn', {
      value: this.cluster.clusterArn,
      exportName: `${props.environment}-Cluster-ARN`,
    });

    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: this.loadBalancer.loadBalancerDnsName,
      exportName: `${props.environment}-ALB-DNS`,
    });

    new cdk.CfnOutput(this, 'FastAPIRepository', {
      value: this.fastapiRepository.repositoryUri,
      exportName: `${props.environment}-FastAPI-Repository-URI`,
    });

    new cdk.CfnOutput(this, 'FrontendBucketName', {
      value: this.frontendBucket.bucketName,
      exportName: `${props.environment}-Frontend-Bucket-Name`,
    });

    new cdk.CfnOutput(this, 'CloudFrontURL', {
      value: `https://${this.distribution.distributionDomainName}`,
      exportName: `${props.environment}-CloudFront-URL`,
    });

    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: this.distribution.distributionId,
      exportName: `${props.environment}-CloudFront-Distribution-ID`,
    });
  }

  private getLogRetention(environment: string): logs.RetentionDays {
    switch (environment) {
      case 'production':
        return logs.RetentionDays.ONE_YEAR;
      case 'staging':
        return logs.RetentionDays.ONE_MONTH;
      default:
        return logs.RetentionDays.ONE_WEEK;
    }
  }

  private createCloudWatchAlarms(environment: string) {
    // ALB Response Time Alarm
    const responseTimeAlarm = new cloudwatch.Alarm(this, `${environment}-High-Response-Time`, {
      alarmName: `bigmann-${environment}-high-response-time`,
      metric: this.loadBalancer.metrics.targetResponseTime(),
      threshold: this.getResponseTimeThreshold(environment),
      evaluationPeriods: 2,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    responseTimeAlarm.addAlarmAction(new cloudwatchActions.SnsAction(this.alertTopic));

    // ALB Error Rate Alarm
    const errorRateAlarm = new cloudwatch.Alarm(this, `${environment}-High-Error-Rate`, {
      alarmName: `bigmann-${environment}-high-error-rate`,
      metric: this.loadBalancer.metrics.httpCodeTarget(elbv2.HttpCodeTarget.TARGET_5XX_COUNT),
      threshold: this.getErrorThreshold(environment),
      evaluationPeriods: 2,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    errorRateAlarm.addAlarmAction(new cloudwatchActions.SnsAction(this.alertTopic));

    // CloudFront Error Rate Alarm
    const cloudFrontErrorAlarm = new cloudwatch.Alarm(this, `${environment}-CloudFront-Errors`, {
      alarmName: `bigmann-${environment}-cloudfront-errors`,
      metric: this.distribution.metric4xxErrorRate(),
      threshold: 5, // 5% error rate
      evaluationPeriods: 2,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    cloudFrontErrorAlarm.addAlarmAction(new cloudwatchActions.SnsAction(this.alertTopic));
  }

  private getResponseTimeThreshold(environment: string): number {
    switch (environment) {
      case 'production':
        return 0.5; // 500ms
      case 'staging':
        return 1.0; // 1 second
      default:
        return 2.0; // 2 seconds
    }
  }

  private getErrorThreshold(environment: string): number {
    switch (environment) {
      case 'production':
        return 10; // 10 errors per period
      case 'staging':
        return 20; // 20 errors per period
      default:
        return 50; // 50 errors per period
    }
  }

  private createSecretsManager(environment: string) {
    // Database secrets
    new secretsmanager.Secret(this, `${environment}-Database-Secret`, {
      secretName: `bigmann/${environment}/database`,
      description: `MongoDB Atlas credentials for ${environment}`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          username: `bigmann_${environment}`,
          database_name: `bigmann_entertainment_${environment}`,
        }),
        generateStringKey: 'password',
        excludeCharacters: '"@/\\',
      },
    });

    // Stripe secrets
    new secretsmanager.Secret(this, `${environment}-Stripe-Secret`, {
      secretName: `bigmann/${environment}/stripe`,
      description: `Stripe API credentials for ${environment}`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          publishable_key: 'pk_test_placeholder',
          webhook_secret: 'whsec_placeholder',
        }),
        generateStringKey: 'secret_key',
        excludeCharacters: '"@/\\',
      },
    });

    // PayPal secrets
    new secretsmanager.Secret(this, `${environment}-PayPal-Secret`, {
      secretName: `bigmann/${environment}/paypal`,
      description: `PayPal API credentials for ${environment}`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          client_id: 'paypal_client_id_placeholder',
          environment: environment === 'production' ? 'live' : 'sandbox',
        }),
        generateStringKey: 'client_secret',
        excludeCharacters: '"@/\\',
      },
    });

    // Web3 secrets
    new secretsmanager.Secret(this, `${environment}-Web3-Secret`, {
      secretName: `bigmann/${environment}/web3`,
      description: `Web3 configuration for ${environment}`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          provider_url: `https://eth-${environment === 'production' ? 'mainnet' : 'goerli'}.alchemyapi.io/v2/your-api-key`,
          contract_addresses: {
            nft: '0x0000000000000000000000000000000000000000',
            token: '0x0000000000000000000000000000000000000000',
          },
        }),
        generateStringKey: 'private_key',
        excludeCharacters: '"@/\\',
      },
    });

    // JWT secrets
    new secretsmanager.Secret(this, `${environment}-JWT-Secret`, {
      secretName: `bigmann/${environment}/jwt`,
      description: `JWT signing secret for ${environment}`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          algorithm: 'HS256',
          expiration_hours: 24,
        }),
        generateStringKey: 'secret_key',
        excludeCharacters: '"@/\\',
      },
    });
  }

  private createIAMRoles(environment: string) {
    // ECS Task Execution Role
    const ecsTaskExecutionRole = new iam.Role(this, `${environment}-ECS-Task-Execution-Role`, {
      roleName: `bigmann-${environment}-ecs-task-execution-role`,
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy'),
      ],
    });

    // ECS Task Role
    const ecsTaskRole = new iam.Role(this, `${environment}-ECS-Task-Role`, {
      roleName: `bigmann-${environment}-ecs-task-role`,
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
    });

    // Grant access to Secrets Manager
    ecsTaskRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'secretsmanager:GetSecretValue',
        'secretsmanager:DescribeSecret',
      ],
      resources: [
        `arn:aws:secretsmanager:${this.region}:${this.account}:secret:bigmann/${environment}/*`,
      ],
    }));

    // Grant access to S3
    ecsTaskRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
      ],
      resources: [
        this.frontendBucket.bucketArn,
        `${this.frontendBucket.bucketArn}/*`,
      ],
    }));

    // Grant access to CloudWatch Logs
    ecsTaskRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
      resources: [
        `arn:aws:logs:${this.region}:${this.account}:log-group:/ecs/bigmann-${environment}-*`,
      ],
    }));

    // CodeBuild Service Role
    const codeBuildRole = new iam.Role(this, `${environment}-CodeBuild-Role`, {
      roleName: `bigmann-${environment}-codebuild-role`,
      assumedBy: new iam.ServicePrincipal('codebuild.amazonaws.com'),
    });

    // Grant CodeBuild permissions
    codeBuildRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'ecr:BatchCheckLayerAvailability',
        'ecr:GetDownloadUrlForLayer',
        'ecr:BatchGetImage',
        'ecr:GetAuthorizationToken',
        'ecr:PutImage',
        'ecr:InitiateLayerUpload',
        'ecr:UploadLayerPart',
        'ecr:CompleteLayerUpload',
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
        'cloudfront:CreateInvalidation',
      ],
      resources: ['*'],
    }));

    // Export role ARNs
    new cdk.CfnOutput(this, 'ECSTaskExecutionRoleArn', {
      value: ecsTaskExecutionRole.roleArn,
      exportName: `${environment}-ECS-Task-Execution-Role-ARN`,
    });

    new cdk.CfnOutput(this, 'ECSTaskRoleArn', {
      value: ecsTaskRole.roleArn,
      exportName: `${environment}-ECS-Task-Role-ARN`,
    });

    new cdk.CfnOutput(this, 'CodeBuildRoleArn', {
      value: codeBuildRole.roleArn,
      exportName: `${environment}-CodeBuild-Role-ARN`,
    });
  }
}
