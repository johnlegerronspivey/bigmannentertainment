import * as cdk from 'aws-cdk-lib';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as codestarnotifications from 'aws-cdk-lib/aws-codestarnotifications';
import { Construct } from 'constructs';

export interface CICDPipelineStackProps extends cdk.StackProps {
  environments: string[];
  repositoryUri: string;
  githubOwner: string;
  githubRepo: string;
  githubBranch: string;
}

export class CICDPipelineStack extends cdk.Stack {
  public readonly pipeline: codepipeline.Pipeline;
  public readonly artifactsBucket: s3.Bucket;
  public readonly notificationTopic: sns.Topic;

  constructor(scope: Construct, id: string, props: CICDPipelineStackProps) {
    super(scope, id, props);

    // S3 bucket for pipeline artifacts
    this.artifactsBucket = new s3.Bucket(this, 'PipelineArtifacts', {
      bucketName: `bigmann-pipeline-artifacts-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      lifecycleRules: [{
        id: 'DeleteOldArtifacts',
        expiration: cdk.Duration.days(30),
      }],
    });

    // SNS Topic for notifications
    this.notificationTopic = new sns.Topic(this, 'PipelineNotifications', {
      topicName: 'bigmann-pipeline-notifications',
      displayName: 'Big Mann Entertainment Pipeline Notifications',
    });

    // CodeBuild projects
    const backendBuildProject = this.createBackendBuildProject();
    const frontendBuildProject = this.createFrontendBuildProject();
    const testProject = this.createTestProject();

    // Pipeline artifacts
    const sourceOutput = new codepipeline.Artifact('Source');
    const backendBuildOutput = new codepipeline.Artifact('BackendBuild');
    const frontendBuildOutput = new codepipeline.Artifact('FrontendBuild');
    const testOutput = new codepipeline.Artifact('TestResults');

    // Main pipeline
    this.pipeline = new codepipeline.Pipeline(this, 'BigMannPipeline', {
      pipelineName: 'bigmann-entertainment-pipeline',
      artifactBucket: this.artifactsBucket,
      stages: [
        {
          stageName: 'Source',
          actions: [
            new codepipeline_actions.GitHubSourceAction({
              actionName: 'GitHub_Source',
              owner: props.githubOwner,
              repo: props.githubRepo,
              branch: props.githubBranch,
              oauthToken: cdk.SecretValue.secretsManager('github-access-token'),
              output: sourceOutput,
            }),
          ],
        },
        {
          stageName: 'Build',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Backend_Build',
              project: backendBuildProject,
              input: sourceOutput,
              outputs: [backendBuildOutput],
              environmentVariables: {
                ENVIRONMENT: { value: 'development' },
                AWS_DEFAULT_REGION: { value: this.region },
                AWS_ACCOUNT_ID: { value: this.account },
              },
            }),
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Frontend_Build',
              project: frontendBuildProject,
              input: sourceOutput,
              outputs: [frontendBuildOutput],
              environmentVariables: {
                ENVIRONMENT: { value: 'development' },
                AWS_DEFAULT_REGION: { value: this.region },
                AWS_ACCOUNT_ID: { value: this.account },
              },
            }),
          ],
        },
        {
          stageName: 'Test',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Run_Tests',
              project: testProject,
              input: sourceOutput,
              outputs: [testOutput],
              runOrder: 1,
            }),
          ],
        },
        {
          stageName: 'Deploy_Development',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Backend_Dev',
              project: this.createDeployProject('development', 'backend'),
              input: backendBuildOutput,
              runOrder: 1,
            }),
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Frontend_Dev',
              project: this.createDeployProject('development', 'frontend'),
              input: frontendBuildOutput,
              runOrder: 2,
            }),
          ],
        },
        {
          stageName: 'Approval_Staging',
          actions: [
            new codepipeline_actions.ManualApprovalAction({
              actionName: 'Manual_Approval_Staging',
              additionalInformation: 'Please review and approve deployment to staging environment',
              notificationTopic: this.notificationTopic,
            }),
          ],
        },
        {
          stageName: 'Deploy_Staging',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Backend_Staging',
              project: this.createDeployProject('staging', 'backend'),
              input: backendBuildOutput,
              runOrder: 1,
            }),
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Frontend_Staging',
              project: this.createDeployProject('staging', 'frontend'),
              input: frontendBuildOutput,
              runOrder: 2,
            }),
          ],
        },
        {
          stageName: 'Approval_Production',
          actions: [
            new codepipeline_actions.ManualApprovalAction({
              actionName: 'Manual_Approval_Production',
              additionalInformation: 'Please review and approve deployment to production environment',
              notificationTopic: this.notificationTopic,
            }),
          ],
        },
        {
          stageName: 'Deploy_Production',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Backend_Production',
              project: this.createDeployProject('production', 'backend'),
              input: backendBuildOutput,
              runOrder: 1,
            }),
            new codepipeline_actions.CodeBuildAction({
              actionName: 'Deploy_Frontend_Production',
              project: this.createDeployProject('production', 'frontend'),
              input: frontendBuildOutput,
              runOrder: 2,
            }),
          ],
        },
      ],
    });

    // Pipeline notifications
    new codestarnotifications.NotificationRule(this, 'PipelineNotificationRule', {
      source: this.pipeline,
      events: [
        'codepipeline-pipeline-pipeline-execution-failed',
        'codepipeline-pipeline-pipeline-execution-succeeded',
        'codepipeline-pipeline-stage-execution-failed',
        'codepipeline-pipeline-manual-approval-needed',
      ],
      targets: [this.notificationTopic],
    });

    // Outputs
    new cdk.CfnOutput(this, 'PipelineName', {
      value: this.pipeline.pipelineName,
      exportName: 'BigMann-Pipeline-Name',
    });

    new cdk.CfnOutput(this, 'ArtifactsBucketName', {
      value: this.artifactsBucket.bucketName,
      exportName: 'BigMann-Pipeline-Artifacts-Bucket',
    });
  }

  private createBackendBuildProject(): codebuild.Project {
    const project = new codebuild.Project(this, 'BackendBuild', {
      projectName: 'bigmann-backend-build',
      source: codebuild.Source.gitHub({
        owner: 'your-github-owner',
        repo: 'bigmann-entertainment',
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        computeType: codebuild.ComputeType.SMALL,
        privileged: true, // Required for Docker builds
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Logging in to Amazon ECR...',
              'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
              'REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/bigmann-fastapi-$ENVIRONMENT',
              'COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)',
              'IMAGE_TAG=${COMMIT_HASH:=latest}',
              'echo Installing backend dependencies...',
              'cd backend',
              'pip install --upgrade pip',
              'pip install -r requirements.txt',
              'pip install pytest pytest-cov black flake8 safety bandit',
            ],
          },
          build: {
            commands: [
              'echo Running security scans...',
              'safety check --json --output security-report.json || true',
              'bandit -r . -f json -o bandit-report.json || true',
              'echo Running code quality checks...',
              'black --check . || true',
              'flake8 . --output-file=flake8-report.txt || true',
              'echo Running tests...',
              'pytest tests/ --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml || true',
              'echo Building Docker image...',
              'docker build -t $REPOSITORY_URI:latest .',
              'docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG',
            ],
          },
          post_build: {
            commands: [
              'echo Build completed on `date`',
              'echo Pushing the Docker image...',
              'docker push $REPOSITORY_URI:latest',
              'docker push $REPOSITORY_URI:$IMAGE_TAG',
              'printf \'{"imageUri":"%s"}\' $REPOSITORY_URI:$IMAGE_TAG > imageDetail.json',
            ],
          },
        },
        artifacts: {
          files: [
            'imageDetail.json',
            'backend/test-results.xml',
            'backend/coverage.xml',
            'backend/security-report.json',
            'backend/bandit-report.json',
            'backend/flake8-report.txt',
          ],
        },
        reports: {
          pytest_reports: {
            files: ['backend/test-results.xml'],
            'file-format': 'JUNITXML',
          },
          coverage_reports: {
            files: ['backend/coverage.xml'],
            'file-format': 'COBERTURAXML',
          },
        },
      }),
      environmentVariables: {
        AWS_DEFAULT_REGION: {
          value: this.region,
        },
        AWS_ACCOUNT_ID: {
          value: this.account,
        },
      },
    });

    // Grant permissions
    project.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'ecr:BatchCheckLayerAvailability',
        'ecr:GetDownloadUrlForLayer',
        'ecr:BatchGetImage',
        'ecr:GetAuthorizationToken',
        'ecr:PutImage',
        'ecr:InitiateLayerUpload',
        'ecr:UploadLayerPart',
        'ecr:CompleteLayerUpload',
      ],
      resources: ['*'],
    }));

    return project;
  }

  private createFrontendBuildProject(): codebuild.Project {
    const project = new codebuild.Project(this, 'FrontendBuild', {
      projectName: 'bigmann-frontend-build',
      source: codebuild.Source.gitHub({
        owner: 'your-github-owner',
        repo: 'bigmann-entertainment',
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        computeType: codebuild.ComputeType.SMALL,
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Installing frontend dependencies...',
              'cd frontend',
              'yarn install',
            ],
          },
          build: {
            commands: [
              'echo Running frontend tests...',
              'yarn test:$ENVIRONMENT || true',
              'echo Building frontend application for $ENVIRONMENT...',
              'yarn build:$ENVIRONMENT',
            ],
          },
          post_build: {
            commands: [
              'echo Build completed on `date`',
            ],
          },
        },
        artifacts: {
          files: ['**/*'],
          'base-directory': 'frontend/build',
        },
      }),
      environmentVariables: {
        AWS_DEFAULT_REGION: {
          value: this.region,
        },
        AWS_ACCOUNT_ID: {
          value: this.account,
        },
      },
    });

    return project;
  }

  private createTestProject(): codebuild.Project {
    return new codebuild.Project(this, 'TestProject', {
      projectName: 'bigmann-test-project',
      source: codebuild.Source.codeCommit({
        repository: codebuild.Repository.fromSourceVersion('main'),
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        computeType: codebuild.ComputeType.SMALL,
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Installing test dependencies...',
              'cd backend && pip install -r requirements.txt && pip install pytest pytest-cov',
              'cd ../frontend && yarn install',
            ],
          },
          build: {
            commands: [
              'echo Running backend tests...',
              'cd backend && pytest tests/ --cov=. --cov-report=xml --junitxml=test-results.xml',
              'echo Running frontend tests...',
              'cd ../frontend && yarn test --coverage --watchAll=false',
            ],
          },
          post_build: {
            commands: [
              'echo Tests completed on `date`',
            ],
          },
        },
        artifacts: {
          files: [
            'backend/test-results.xml',
            'backend/coverage.xml',
            'frontend/coverage/**/*',
          ],
        },
        reports: {
          backend_tests: {
            files: ['backend/test-results.xml'],
            'file-format': 'JUNITXML',
          },
          backend_coverage: {
            files: ['backend/coverage.xml'],
            'file-format': 'COBERTURAXML',
          },
        },
      }),
    });
  }

  private createDeployProject(environment: string, component: 'backend' | 'frontend'): codebuild.Project {
    const projectName = `bigmann-deploy-${component}-${environment}`;
    
    let buildSpec: codebuild.BuildSpec;
    
    if (component === 'backend') {
      buildSpec = codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Logging in to Amazon ECR...',
              'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
              'REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/bigmann-fastapi-' + environment,
              'IMAGE_TAG=latest',
            ],
          },
          build: {
            commands: [
              'echo Deploying backend to ' + environment + '...',
              'echo Creating ECS task definition...',
              `cat > taskdef.json << EOF
{
  "family": "bigmann-${environment}-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::${this.account}:role/bigmann-${environment}-ecs-task-execution-role",
  "taskRoleArn": "arn:aws:iam::${this.account}:role/bigmann-${environment}-ecs-task-role",
  "containerDefinitions": [
    {
      "name": "bigmann-${environment}-backend",
      "image": "$REPOSITORY_URI:$IMAGE_TAG",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "${environment}"
        }
      ],
      "secrets": [
        {
          "name": "MONGO_URL",
          "valueFrom": "arn:aws:secretsmanager:${this.region}:${this.account}:secret:bigmann/${environment}/database:connection_string::"
        },
        {
          "name": "STRIPE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:${this.region}:${this.account}:secret:bigmann/${environment}/stripe:secret_key::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/bigmann-${environment}-backend",
          "awslogs-region": "${this.region}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF`,
              'echo Updating ECS service...',
              `aws ecs register-task-definition --cli-input-json file://taskdef.json --region ${this.region}`,
              `aws ecs update-service --cluster bigmann-${environment}-cluster --service bigmann-${environment}-backend-service --task-definition bigmann-${environment}-backend --region ${this.region}`,
              `aws ecs wait services-stable --cluster bigmann-${environment}-cluster --services bigmann-${environment}-backend-service --region ${this.region}`,
            ],
          },
          post_build: {
            commands: [
              'echo Deployment completed on `date`',
            ],
          },
        },
      });
    } else {
      buildSpec = codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          pre_build: {
            commands: [
              'echo Preparing frontend deployment...',
              `S3_BUCKET=bigmann-frontend-${environment}-${this.account}`,
              `DISTRIBUTION_ID=$(aws cloudformation describe-stacks --stack-name BigMann-${environment.charAt(0).toUpperCase() + environment.slice(1)} --query 'Stacks[0].Outputs[?OutputKey==\`CloudFrontDistributionId\`].OutputValue' --output text --region ${this.region})`,
            ],
          },
          build: {
            commands: [
              'echo Deploying frontend to S3...',
              'aws s3 sync . s3://$S3_BUCKET/ --delete --cache-control "public, max-age=31536000" --exclude "*.html" --exclude "service-worker.js"',
              'aws s3 sync . s3://$S3_BUCKET/ --delete --cache-control "public, max-age=0, must-revalidate" --include "*.html" --include "service-worker.js"',
              'echo Creating CloudFront invalidation...',
              'aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"',
            ],
          },
          post_build: {
            commands: [
              'echo Frontend deployment completed on `date`',
            ],
          },
        },
      });
    }

    const project = new codebuild.Project(this, `Deploy${component.charAt(0).toUpperCase() + component.slice(1)}${environment.charAt(0).toUpperCase() + environment.slice(1)}`, {
      projectName: projectName,
      source: codebuild.Source.codeCommit({
        repository: codebuild.Repository.fromSourceVersion('main'),
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_5_0,
        computeType: codebuild.ComputeType.SMALL,
        privileged: component === 'backend',
      },
      buildSpec: buildSpec,
      environmentVariables: {
        AWS_DEFAULT_REGION: {
          value: this.region,
        },
        AWS_ACCOUNT_ID: {
          value: this.account,
        },
        ENVIRONMENT: {
          value: environment,
        },
      },
    });

    // Grant necessary permissions
    project.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'ecs:RegisterTaskDefinition',
        'ecs:UpdateService',
        'ecs:DescribeServices',
        'ecs:DescribeTaskDefinition',
        'ecs:DescribeClusters',
        'iam:PassRole',
        's3:GetObject',
        's3:PutObject',
        's3:DeleteObject',
        's3:ListBucket',
        'cloudfront:CreateInvalidation',
        'cloudformation:DescribeStacks',
        'ecr:GetAuthorizationToken',
        'ecr:BatchCheckLayerAvailability',
        'ecr:GetDownloadUrlForLayer',
        'ecr:BatchGetImage',
      ],
      resources: ['*'],
    }));

    return project;
  }
}