#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { BigMannEnvironmentStack } from '../lib/aws-infrastructure-stack';

const app = new cdk.App();

// Get the AWS account and region from environment variables or CDK context
const account = process.env.CDK_DEFAULT_ACCOUNT || '314108682794';
const region = 'us-east-1';

// Development Environment
new BigMannEnvironmentStack(app, 'BigMann-Development', {
  environment: 'development',
  env: {
    account: account,
    region: region,
  },
  tags: {
    Environment: 'development',
    Project: 'BigMannEntertainment',
    Owner: 'DevTeam',
  },
});

// Staging Environment
new BigMannEnvironmentStack(app, 'BigMann-Staging', {
  environment: 'staging',
  env: {
    account: account,
    region: region,
  },
  tags: {
    Environment: 'staging',
    Project: 'BigMannEntertainment',
    Owner: 'DevTeam',
  },
});

// Production Environment
new BigMannEnvironmentStack(app, 'BigMann-Production', {
  environment: 'production',
  domain: 'bigmannentertainment.com',
  env: {
    account: account,
    region: region,
  },
  tags: {
    Environment: 'production',
    Project: 'BigMannEntertainment',
    Owner: 'DevTeam',
    CostCenter: 'Production',
  },
});

// Add global tags to all stacks
cdk.Tags.of(app).add('Project', 'BigMannEntertainment');
cdk.Tags.of(app).add('ManagedBy', 'CDK');
cdk.Tags.of(app).add('CreatedOn', new Date().toISOString().split('T')[0]);